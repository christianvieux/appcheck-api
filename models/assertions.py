from enum import Enum

from pydantic import BaseModel, Field


class AssertionOperator(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    EXISTS = "exists"
    IS_NUMBER = "is_number"
    IS_STRING = "is_string"
    IS_BOOLEAN = "is_boolean"
    IS_ARRAY = "is_array"
    IS_OBJECT = "is_object"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    EVERY_ITEM_MATCHES = "every_item_matches"
    SOME_ITEM_MATCHES = "some_item_matches"


class AssertionOperatorMetadata(BaseModel):
    operator: AssertionOperator = Field(
        ...,
        description="Assertion operator identifier.",
        examples=["equals"],
    )

    requires_value: bool = Field(
        ...,
        description="Whether this operator requires a comparison value.",
    )

    requires_conditions: bool = Field(
        ...,
        description="Whether this operator requires nested conditions.",
    )

    allowed_in_rules: bool = Field(
        ...,
        description="Whether this operator can be used inside nested assertion rules.",
    )


ASSERTION_OPERATOR_METADATA: dict[AssertionOperator, AssertionOperatorMetadata] = {
    AssertionOperator.EQUALS: AssertionOperatorMetadata(
        operator=AssertionOperator.EQUALS,
        requires_value=True,
        requires_conditions=False,
        allowed_in_rules=True,
    ),
    AssertionOperator.NOT_EQUALS: AssertionOperatorMetadata(
        operator=AssertionOperator.NOT_EQUALS,
        requires_value=True,
        requires_conditions=False,
        allowed_in_rules=True,
    ),
    AssertionOperator.EXISTS: AssertionOperatorMetadata(
        operator=AssertionOperator.EXISTS,
        requires_value=False,
        requires_conditions=False,
        allowed_in_rules=True,
    ),
    AssertionOperator.IS_NUMBER: AssertionOperatorMetadata(
        operator=AssertionOperator.IS_NUMBER,
        requires_value=False,
        requires_conditions=False,
        allowed_in_rules=True,
    ),
    AssertionOperator.IS_STRING: AssertionOperatorMetadata(
        operator=AssertionOperator.IS_STRING,
        requires_value=False,
        requires_conditions=False,
        allowed_in_rules=True,
    ),
    AssertionOperator.IS_BOOLEAN: AssertionOperatorMetadata(
        operator=AssertionOperator.IS_BOOLEAN,
        requires_value=False,
        requires_conditions=False,
        allowed_in_rules=True,
    ),
    AssertionOperator.IS_ARRAY: AssertionOperatorMetadata(
        operator=AssertionOperator.IS_ARRAY,
        requires_value=False,
        requires_conditions=False,
        allowed_in_rules=True,
    ),
    AssertionOperator.IS_OBJECT: AssertionOperatorMetadata(
        operator=AssertionOperator.IS_OBJECT,
        requires_value=False,
        requires_conditions=False,
        allowed_in_rules=True,
    ),
    AssertionOperator.GREATER_THAN: AssertionOperatorMetadata(
        operator=AssertionOperator.GREATER_THAN,
        requires_value=True,
        requires_conditions=False,
        allowed_in_rules=True,
    ),
    AssertionOperator.LESS_THAN: AssertionOperatorMetadata(
        operator=AssertionOperator.LESS_THAN,
        requires_value=True,
        requires_conditions=False,
        allowed_in_rules=True,
    ),
    AssertionOperator.CONTAINS: AssertionOperatorMetadata(
        operator=AssertionOperator.CONTAINS,
        requires_value=True,
        requires_conditions=False,
        allowed_in_rules=True,
    ),
    AssertionOperator.EVERY_ITEM_MATCHES: AssertionOperatorMetadata(
        operator=AssertionOperator.EVERY_ITEM_MATCHES,
        requires_value=False,
        requires_conditions=True,
        allowed_in_rules=False,
    ),
    AssertionOperator.SOME_ITEM_MATCHES: AssertionOperatorMetadata(
        operator=AssertionOperator.SOME_ITEM_MATCHES,
        requires_value=False,
        requires_conditions=True,
        allowed_in_rules=False,
    ),
}


def list_assertion_operator_metadata() -> list[AssertionOperatorMetadata]:
    return list(ASSERTION_OPERATOR_METADATA.values())


def get_assertion_operator_metadata(
    operator: AssertionOperator,
) -> AssertionOperatorMetadata:
    return ASSERTION_OPERATOR_METADATA[operator]


def operator_requires_value(operator: AssertionOperator) -> bool:
    return get_assertion_operator_metadata(operator).requires_value


def operator_requires_conditions(operator: AssertionOperator) -> bool:
    return get_assertion_operator_metadata(operator).requires_conditions


def operator_allowed_in_rules(operator: AssertionOperator) -> bool:
    return get_assertion_operator_metadata(operator).allowed_in_rules
