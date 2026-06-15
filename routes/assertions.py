from fastapi import APIRouter

from models.assertions import (
    AssertionOperatorMetadata,
    list_assertion_operator_metadata,
)


router = APIRouter()


@router.get("/assertion-operators", status_code=200, response_model=list[AssertionOperatorMetadata])
async def list_assertion_operators():
    return list_assertion_operator_metadata()
