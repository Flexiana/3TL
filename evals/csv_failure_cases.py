"""
CSV Failure Cases vs 3TL Success

Tests scenarios where CSV is ambiguous or fails, but 3TL succeeds.
"""

from inspect_ai import Task, eval, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes, match
from inspect_ai.solver import generate

# Case 1: Type Ambiguity - Is "123" a string or number?
CSV_TYPE_AMBIGUOUS = """id,code,amount
1,123,456
2,ABC,789"""

THREE_TL_TYPE_EXPLICIT = """#! Transaction
#@ id:uint, code:str, amount:uint
1, 123, 456
2, ABC, 789"""


# Case 2: Precision Loss - Can't distinguish 1.0 vs 1.00
CSV_PRECISION_LOST = """product,price,tax_rate
Widget,19.99,0.05
Gadget,20.00,0.050"""

THREE_TL_PRECISION_KEPT = """#! Product
#@ product:str, price:decimal(10,2), tax_rate:decimal(5,3)
Widget, 19.99, 0.050
Gadget, 20.00, 0.050"""


# Case 3: Boolean Ambiguity - What does "1" mean?
CSV_BOOLEAN_AMBIGUOUS = """user,active,admin
Alice,1,0
Bob,yes,no
Charlie,true,false"""

THREE_TL_BOOLEAN_CLEAR = """#! User
#@ user:str, active:bool, admin:bool
Alice, true, false
Bob, true, false
Charlie, true, false"""


# Case 4: Null vs Empty String
CSV_NULL_AMBIGUOUS = """name,middle_name,nickname
Alice,,
Bob,Robert,Bobby"""

THREE_TL_NULL_CLEAR = """#! Person
#@ name:str, middle_name:str?, nickname:str?
Alice, ,
Bob, Robert, Bobby"""


# Case 5: Date Format Ambiguity
CSV_DATE_AMBIGUOUS = """event,date
Meeting,01/02/03
Launch,12/31/99"""

THREE_TL_DATE_CLEAR = """#! Event
#@ event:str, date:date
Meeting, 2003-01-02
Launch, 1999-12-31"""


# Case 6: Enum Validation - Invalid values not caught
CSV_ENUM_UNCHECKED = """order_id,status
101,pending
102,SHIPPED
103,delivered
104,in_transit"""

THREE_TL_ENUM_VALIDATED = """#! Order
#@ order_id:uint, status:enum(pending|shipped|delivered)
101, pending
102, shipped
103, delivered"""


# Case 7: Foreign Key Ambiguity
CSV_FK_UNCLEAR = """order_id,user_id,product_id
1,5,10
2,5,11"""

THREE_TL_FK_EXPLICIT = """#! Order
#@ order_id:uint, user_id:ref(User.id), product_id:ref(Product.id)
1, 5, 10
2, 5, 11"""


# Case 8: Array Representation
CSV_ARRAY_MESSY = """product,tags
Laptop,\"electronics,computers,portable\"
Book,\"education,paperback\""""

THREE_TL_ARRAY_CLEAN = """#! Product
#@ product:str, tags:str[]
Laptop, [electronics, computers, portable]
Book, [education, paperback]"""


@task
def csv_type_ambiguity():
    """CSV: Can't tell if '123' is string or number"""
    return Task(
        dataset=[
            Sample(
                input=f"In this CSV data:\n\n{CSV_TYPE_AMBIGUOUS}\n\nIs the 'code' field a string or a number? Be specific.",
                target=["ambiguous", "unclear", "could be", "either", "depends", "not sure"]
            ),
            Sample(
                input=f"In this 3TL data:\n\n{THREE_TL_TYPE_EXPLICIT}\n\nIs the 'code' field a string or a number?",
                target=["string", "str"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def csv_precision_loss():
    """CSV: Can't distinguish 0.05 vs 0.050 (different precisions)"""
    return Task(
        dataset=[
            Sample(
                input=f"In this CSV:\n\n{CSV_PRECISION_LOST}\n\nWhat is the EXACT precision (number of decimal places) for the tax_rate field?",
                target=["can't", "unclear", "ambiguous", "not specified", "lost"]
            ),
            Sample(
                input=f"In this 3TL data:\n\n{THREE_TL_PRECISION_KEPT}\n\nWhat is the EXACT precision (number of decimal places) for the tax_rate field?",
                target=["3", "decimal(5,3)"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def csv_boolean_inconsistency():
    """CSV: Boolean values can be represented many ways"""
    return Task(
        dataset=[
            Sample(
                input=f"In this CSV:\n\n{CSV_BOOLEAN_AMBIGUOUS}\n\nAre the boolean representations consistent? List the different ways booleans are represented.",
                target=["1/0", "yes/no", "true/false", "inconsistent", "three different"]
            ),
            Sample(
                input=f"In this 3TL data:\n\n{THREE_TL_BOOLEAN_CLEAR}\n\nHow are boolean values represented?",
                target=["true", "false", "consistent"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def csv_null_vs_empty():
    """CSV: Can't distinguish null from empty string"""
    return Task(
        dataset=[
            Sample(
                input=f"In this CSV:\n\n{CSV_NULL_AMBIGUOUS}\n\nIs Alice's middle_name NULL or an empty string? Can you tell for certain?",
                target=["can't tell", "ambiguous", "unclear", "could be either", "not sure"]
            ),
            Sample(
                input=f"In this 3TL data:\n\n{THREE_TL_NULL_CLEAR}\n\nThe middle_name is declared as 'str?' - what does the '?' mean?",
                target=["nullable", "optional", "can be null"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def csv_date_format_confusion():
    """CSV: Date format is ambiguous (MM/DD/YY vs DD/MM/YY)"""
    return Task(
        dataset=[
            Sample(
                input=f"In this CSV:\n\n{CSV_DATE_AMBIGUOUS}\n\nFor the date '01/02/03', what date does this represent? Is it January 2, 2003 or February 1, 2003? Can you tell?",
                target=["ambiguous", "could be", "unclear", "depends", "can't tell", "either"]
            ),
            Sample(
                input=f"In this 3TL data:\n\n{THREE_TL_DATE_CLEAR}\n\nWhat date format is used?",
                target=["ISO", "YYYY-MM-DD", "2003-01-02", "unambiguous"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def csv_enum_validation_missing():
    """CSV: No way to validate enum values"""
    return Task(
        dataset=[
            Sample(
                input=f"In this CSV:\n\n{CSV_ENUM_UNCHECKED}\n\nIs 'SHIPPED' a valid status value? How can you tell what the valid status values are?",
                target=["can't tell", "unclear", "would need", "infer", "look at", "don't know"]
            ),
            Sample(
                input=f"In this 3TL data:\n\n{THREE_TL_ENUM_VALIDATED}\n\nWhat are the valid values for the 'status' field?",
                target=["pending", "shipped", "delivered"]
            ),
            Sample(
                input=f"Looking at this 3TL schema:\n\n{THREE_TL_ENUM_VALIDATED}\n\nIf I tried to add a row with status='cancelled', would it be valid according to the schema?",
                target=["no", "invalid", "not valid", "not allowed"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def csv_foreign_key_unclear():
    """CSV: Foreign keys are just numbers, unclear what they reference"""
    return Task(
        dataset=[
            Sample(
                input=f"In this CSV:\n\n{CSV_FK_UNCLEAR}\n\nWhat table and column does 'user_id' reference?",
                target=["can't tell", "unclear", "don't know", "infer", "probably", "assume"]
            ),
            Sample(
                input=f"In this 3TL data:\n\n{THREE_TL_FK_EXPLICIT}\n\nWhat table and column does 'user_id' reference?",
                target=["User.id", "User table"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def csv_array_representation():
    """CSV: No standard way to represent arrays"""
    return Task(
        dataset=[
            Sample(
                input=f"In this CSV:\n\n{CSV_ARRAY_MESSY}\n\nHow are the tags represented? Is this a single string or an array?",
                target=["string", "comma", "quoted", "ambiguous", "not clear"]
            ),
            Sample(
                input=f"In this 3TL data:\n\n{THREE_TL_ARRAY_CLEAN}\n\nWhat is the type of the 'tags' field?",
                target=["array", "str[]", "list"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


@task
def csv_schema_inference_wrong():
    """CSV: Schema inference can be wrong"""
    return Task(
        dataset=[
            Sample(
                input=f"""Given this CSV with 2 rows:

id,code
1,123
2,456

If I infer the schema, 'code' looks like a number. But what if row 3 is:

3,ABC

What problem does this cause?""",
                target=["breaks", "error", "fail", "type", "mismatch", "wrong"]
            ),
            Sample(
                input=f"""In 3TL, the schema is declared upfront:

#! Data
#@ id:uint, code:str
1, 123
2, 456
3, ABC

Why doesn't row 3 cause a problem here?""",
                target=["declared", "explicit", "schema", "string", "type is str", "upfront"]
            ),
        ],
        solver=[generate()],
        scorer=includes(),
    )


if __name__ == "__main__":
    # Run all CSV failure case tests
    eval(
        [
            csv_type_ambiguity(),
            csv_precision_loss(),
            csv_boolean_inconsistency(),
            csv_null_vs_empty(),
            csv_date_format_confusion(),
            csv_enum_validation_missing(),
            csv_foreign_key_unclear(),
            csv_array_representation(),
            csv_schema_inference_wrong(),
        ],
        model="anthropic/claude-3-5-haiku-20241022",
    )
