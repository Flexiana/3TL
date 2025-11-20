"""
Zero-Shot 3TL Understanding Test

Tests whether LLMs can understand 3TL format naturally WITHOUT
any documentation, examples, or explanation.

This tests if the syntax is intuitive and self-explanatory.
"""

from inspect_ai import Task, eval, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes, match
from inspect_ai.solver import generate

# Sample 3TL data with NO context or explanation
PRODUCT_DATA = """#! Product
#@ id:uint, name:str, price:decimal(10,2), category:enum(Electronics|Books|Toys), in_stock:bool
1, Laptop, 999.99, Electronics, true
2, Python Book, 29.99, Books, true
3, Robot Toy, 49.99, Toys, false"""

USER_ORDER_DATA = """#! User
#@ id:uint, name:str, email:str, status:enum(active|inactive|banned)
1, Alice, alice@example.com, active
2, Bob, bob@example.com, inactive

#! Order
#@ id:uint, user_id:ref(User.id), product_id:ref(Product.id), quantity:uint, total:decimal(10,2)
101, 1, 1, 1, 999.99
102, 2, 2, 2, 59.98"""


@task
def zero_shot_format_recognition():
    """Can the model recognize what format this is?"""
    return Task(
        dataset=[
            Sample(
                input=f"What data format is this?\n\n{PRODUCT_DATA}",
                target=["3TL", "typed", "schema", "table", "structured"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def zero_shot_structure_understanding():
    """Can the model understand the structure without explanation?"""
    return Task(
        dataset=[
            Sample(
                input=f"Looking at this data:\n\n{PRODUCT_DATA}\n\nWhat does the line starting with '#!' represent?",
                target=["table", "name", "definition", "header", "entity"]
            ),
            Sample(
                input=f"Looking at this data:\n\n{PRODUCT_DATA}\n\nWhat does the line starting with '#@' represent?",
                target=["schema", "column", "type", "definition", "field"]
            ),
            Sample(
                input=f"Looking at this data:\n\n{PRODUCT_DATA}\n\nHow many products are in this data?",
                target="3"
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def zero_shot_type_understanding():
    """Can the model understand type syntax without explanation?"""
    return Task(
        dataset=[
            Sample(
                input=f"Looking at this data:\n\n{PRODUCT_DATA}\n\nWhat does 'uint' mean for the id field?",
                target=["unsigned", "integer", "positive", "number", "whole"]
            ),
            Sample(
                input=f"Looking at this data:\n\n{PRODUCT_DATA}\n\nWhat does 'decimal(10,2)' mean for the price field?",
                target=["decimal", "10", "2", "precision", "scale"]
            ),
            Sample(
                input=f"Looking at this data:\n\n{PRODUCT_DATA}\n\nWhat does 'enum(Electronics|Books|Toys)' mean for the category field?",
                target=["Electronics", "Books", "Toys", "valid", "allowed", "one of"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def zero_shot_relationship_understanding():
    """Can the model understand ref() syntax without explanation?"""
    return Task(
        dataset=[
            Sample(
                input=f"Looking at this data:\n\n{USER_ORDER_DATA}\n\nWhat does 'ref(User.id)' mean for the user_id field in the Order table?",
                target=["reference", "User", "id", "foreign key", "relationship", "points to"]
            ),
            Sample(
                input=f"Looking at this data:\n\n{USER_ORDER_DATA}\n\nWhich user placed order 101?",
                target=["Alice", "1"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def zero_shot_data_extraction():
    """Can the model extract data correctly without explanation?"""
    return Task(
        dataset=[
            Sample(
                input=f"Looking at this data:\n\n{PRODUCT_DATA}\n\nWhat is the price of the Laptop?",
                target="999.99"
            ),
            Sample(
                input=f"Looking at this data:\n\n{PRODUCT_DATA}\n\nWhich products are in stock?",
                target=["Laptop", "Python Book"]
            ),
            Sample(
                input=f"Looking at this data:\n\n{PRODUCT_DATA}\n\nWhat category is the Robot Toy?",
                target="Toys"
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def zero_shot_syntax_explanation():
    """Can the model explain the syntax after seeing it?"""
    return Task(
        dataset=[
            Sample(
                input=f"Looking at this data format:\n\n{PRODUCT_DATA}\n\nExplain how the schema definition (the #@ line) works in 2 sentences.",
                target=["column", "type", "colon", "comma"]
            ),
            Sample(
                input=f"Looking at this data format:\n\n{USER_ORDER_DATA}\n\nHow many tables are defined here?",
                target="2"
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def zero_shot_comparison_to_csv():
    """Can the model compare to CSV without prompting?"""
    return Task(
        dataset=[
            Sample(
                input=f"Compare this format:\n\n{PRODUCT_DATA}\n\nto regular CSV. What's the main difference?",
                target=["type", "schema", "explicit", "column", "definition"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


if __name__ == "__main__":
    # Run all zero-shot tests
    eval(
        [
            zero_shot_format_recognition(),
            zero_shot_structure_understanding(),
            zero_shot_type_understanding(),
            zero_shot_relationship_understanding(),
            zero_shot_data_extraction(),
            zero_shot_syntax_explanation(),
            zero_shot_comparison_to_csv(),
        ],
        model="anthropic/claude-3-5-haiku-20241022",
    )
