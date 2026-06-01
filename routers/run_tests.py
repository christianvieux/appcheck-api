# Imports
from fastapi import APIRouter
from pydantic import BaseModel, AnyUrl, PositiveInt, Field
from typing import Any, Literal
from services.test_runner import run_multiple_test_case
from models.test_case import RunTestsRequest

# Initialize router
router = APIRouter()

# Endpoints
@router.post("/run-tests", status_code=200) # better than "/health" :P
async def run_tests(request: RunTestsRequest):

    tests_results = await run_multiple_test_case(request.test_cases)

    # calculating summary
    total_tests = len(request.test_cases)
    number_of_failed_tests = sum(
        1 for test_result in tests_results
        if test_result.status == "failed"
        )
    number_of_passed_tests = total_tests - number_of_failed_tests
    
    overall_status = "failed" if number_of_failed_tests > 0 else "passed"
    message = "Test run completed. " +(
        "All test cases passed."
        if number_of_failed_tests == 0
        else "Some test cases failed."
    )

    return {
        "message": message,
        "status": overall_status,
        "test_results": tests_results,
        "summary": {
            "passed": number_of_passed_tests,
            "failed": number_of_failed_tests,
            "total" : total_tests,
            },
        }