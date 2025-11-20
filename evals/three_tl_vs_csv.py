"""
3TL vs CSV Comprehension Evaluation

Tests whether LLMs better understand structured data in 3TL format vs plain CSV.
Demonstrates advantages of 3TL: type information, schemas, relationships, etc.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from inspect_ai import Task, eval, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import match, includes
from inspect_ai.solver import generate, system_message

# Load environment variables from .env
load_dotenv()

# Sample data for testing
CSV_USERS = """id,name,email,role,active
1,Alice,alice@example.com,admin,true
2,Bob,bob@example.com,user,true
3,Charlie,charlie@example.com,user,false"""

THREE_TL_USERS = """#! User
#@ id:uint, name:str, email:str, role:enum(admin|user|moderator), active:bool
1, Alice, alice@example.com, admin, true
2, Bob, bob@example.com, user, true
3, Charlie, charlie@example.com, user, false"""

CSV_PRODUCTS_ORDERS = """# products.csv
id,name,price,category
1,Laptop,999.99,Electronics
2,Book,19.99,Books

# orders.csv
id,user_id,product_id,quantity,total
1,1,1,1,999.99
2,2,2,3,59.97"""

THREE_TL_PRODUCTS_ORDERS = """#! Product
#@ id:uint, name:str, price:decimal(10,2), category:str
1, Laptop, 999.99, Electronics
2, Book, 19.99, Books

#! Order
#@ id:uint, user_id:ref(User.id), product_id:ref(Product.id), quantity:uint, total:decimal(10,2)
1, 1, 1, 1, 999.99
2, 2, 2, 3, 59.97"""


@task
def type_inference_csv():
    """Test if LLM can infer correct types from CSV data"""
    return Task(
        dataset=[
            Sample(
                input=f"Given this CSV data:\n\n{CSV_USERS}\n\nWhat is the data type of the 'id' column? Answer with just the type name (e.g., integer, string, boolean, etc.)",
                target="integer"
            ),
            Sample(
                input=f"Given this CSV data:\n\n{CSV_USERS}\n\nWhat is the data type of the 'active' column? Answer with just the type name.",
                target="boolean"
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def type_reading_3tl():
    """Test if LLM can read types directly from 3TL schema"""
    return Task(
        dataset=[
            Sample(
                input=f"Given this 3TL data:\n\n{THREE_TL_USERS}\n\nWhat is the data type of the 'id' column? Answer with just the type name from the schema.",
                target="uint"
            ),
            Sample(
                input=f"Given this 3TL data:\n\n{THREE_TL_USERS}\n\nWhat is the data type of the 'active' column? Answer with just the type name from the schema.",
                target="bool"
            ),
            Sample(
                input=f"Given this 3TL data:\n\n{THREE_TL_USERS}\n\nWhat is the data type of the 'role' column? Include the full type definition.",
                target="enum(admin|user|moderator)"
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def relationship_inference_csv():
    """Test if LLM can identify foreign key relationships in CSV"""
    return Task(
        dataset=[
            Sample(
                input=f"Given these CSV files:\n\n{CSV_PRODUCTS_ORDERS}\n\nWhat is the relationship between the 'user_id' column in orders.csv and the users? Describe the foreign key relationship in one sentence.",
                target=["references", "foreign key", "User", "id"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def relationship_reading_3tl():
    """Test if LLM can read explicit relationships from 3TL"""
    return Task(
        dataset=[
            Sample(
                input=f"Given this 3TL data:\n\n{THREE_TL_PRODUCTS_ORDERS}\n\nWhat table and column does 'user_id' reference? Answer in format: Table.column",
                target="User.id"
            ),
            Sample(
                input=f"Given this 3TL data:\n\n{THREE_TL_PRODUCTS_ORDERS}\n\nWhat table and column does 'product_id' reference? Answer in format: Table.column",
                target="Product.id"
            ),
        ],
        solver=[generate()],
        scorer=match(),
    )


@task
def schema_generation_comparison():
    """Test quality of schema generation in both formats"""
    return Task(
        dataset=[
            Sample(
                input="Create a CSV schema (just the header row) for a blog post with: an ID, title, content, author name, publication date, and published status.",
                target="id,title,content,author,date,published"
            ),
            Sample(
                input="Create a 3TL schema definition for a blog post with: an ID (unsigned integer), title (string), content (nullable string), author name (string), publication date (date type), and published status (boolean).",
                target=["#@ id:uint", "title:str", "content:str?", "published:bool", "date"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def data_validation_csv():
    """Test if LLM can spot type errors in CSV"""
    csv_invalid = """id,name,price,active
1,Widget,19.99,true
2,Gadget,not-a-number,yes
3,Thing,29.99,true"""

    return Task(
        dataset=[
            Sample(
                input=f"Find the data validation errors in this CSV:\n\n{csv_invalid}\n\nList any values that don't match expected types.",
                target=["not-a-number", "yes", "price", "active"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def data_validation_3tl():
    """Test if LLM can spot type errors in 3TL"""
    three_tl_invalid = """#! Product
#@ id:uint, name:str, price:decimal(10,2), active:bool
1, Widget, 19.99, true
2, Gadget, not-a-number, yes
3, Thing, 29.99, true"""

    return Task(
        dataset=[
            Sample(
                input=f"Find the data validation errors in this 3TL data:\n\n{three_tl_invalid}\n\nList any values that don't match their declared types.",
                target=["not-a-number", "yes", "row 2", "Gadget"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def precision_understanding():
    """Test if LLM understands precision specs (3TL advantage)"""
    return Task(
        dataset=[
            Sample(
                input="In 3TL, what does 'decimal(10,2)' mean? Explain the two numbers.",
                target=["10", "precision", "2", "scale", "digits"]
            ),
            Sample(
                input=f"Given this 3TL schema:\n\n#@ price:decimal(10,2)\n\nWhat is the maximum value that can be stored in 'price'?",
                target=["99999999.99", "8 digits", "2 decimal"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def multi_table_csv():
    """Test understanding of multi-table data in CSV format"""
    return Task(
        dataset=[
            Sample(
                input=f"Given these CSV files:\n\n{CSV_PRODUCTS_ORDERS}\n\nHow many different files/tables are represented here?",
                target="2"
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def multi_table_3tl():
    """Test understanding of multi-table data in 3TL format"""
    return Task(
        dataset=[
            Sample(
                input=f"Given this 3TL data:\n\n{THREE_TL_PRODUCTS_ORDERS}\n\nHow many tables are defined in this file?",
                target="2"
            ),
            Sample(
                input=f"Given this 3TL data:\n\n{THREE_TL_PRODUCTS_ORDERS}\n\nList the table names in order.",
                target=["Product", "Order"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def enum_understanding():
    """Test if LLM understands enum constraints (3TL-only feature)"""
    return Task(
        dataset=[
            Sample(
                input=f"Given this 3TL data:\n\n{THREE_TL_USERS}\n\nWhat are the valid values for the 'role' column?",
                target=["admin", "user", "moderator"]
            ),
            Sample(
                input=f"Given this 3TL data:\n\n{THREE_TL_USERS}\n\nIf someone tried to insert a user with role='superuser', would it be valid?",
                target=["no", "invalid", "not valid", "not allowed"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


# Comparison suite that runs all evals
@task
def three_tl_comprehension_suite():
    """
    Comprehensive suite comparing LLM understanding of 3TL vs CSV.

    This eval demonstrates that 3TL provides:
    1. Explicit type information (no inference needed)
    2. Clear foreign key relationships
    3. Multiple tables in one file
    4. Enum constraints
    5. Precision specifications
    6. Better validation error detection
    """
    return Task(
        dataset=[
            # Type clarity
            Sample(
                input=f"Compare these two representations of the same data:\n\nCSV:\n{CSV_USERS}\n\n3TL:\n{THREE_TL_USERS}\n\nWhich format makes the data types explicitly clear without inference?",
                target=["3TL", "second"]
            ),
            # Relationship clarity
            Sample(
                input=f"Compare these representations:\n\nCSV:\n{CSV_PRODUCTS_ORDERS}\n\n3TL:\n{THREE_TL_PRODUCTS_ORDERS}\n\nWhich format explicitly shows foreign key relationships?",
                target=["3TL", "second"]
            ),
            # Enum constraints
            Sample(
                input=f"Can you tell from this CSV what values are allowed in the 'role' column?\n\n{CSV_USERS}",
                target=["no", "cannot", "can't", "unclear", "infer"]
            ),
            Sample(
                input=f"Can you tell from this 3TL what values are allowed in the 'role' column?\n\n{THREE_TL_USERS}",
                target=["yes", "admin", "user", "moderator", "enum"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


if __name__ == "__main__":
    # Run the comprehensive comparison suite
    eval(
        three_tl_comprehension_suite(),
        model="openai/gpt-4",  # Change to anthropic/claude-3-5-sonnet-20241022 or other models
    )
