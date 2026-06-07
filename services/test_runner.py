import json

import httpx
import asyncio
import random

from typing import Any, TypedDict
from models.test_case import SingleAssertionModel, SingleTestCaseRequest, SingleTestCaseResult

def every_item_matches(actual: Any, assertion: SingleAssertionModel) -> tuple[bool, str]:
    failure_details: list[str] = []

    if not isinstance(actual, list):
        return False, "Expected an array, but got a different type."

    for item_index, item in enumerate(actual):
        for item_check in assertion.conditions:
            try:
                value = getValueFromJsonPath(item, item_check.path) if item_check.path else item
            except KeyError as e:
                failure_details.append(
                    f"Item at index {item_index}: {e.args[0]}"
                )
                continue

            operator_passed, operator_failure_detail = handle_operator(
                item_check.operator,
                value,
                item_check,
            )

            if not operator_passed:
                failure_details.append(
                    f"Item at index {item_index}, path '{item_check.path}', operator '{item_check.operator}': {operator_failure_detail}"
                )

    if failure_details:
        return False, "\n".join(failure_details)

    return True, ""

def some_item_matches(actual: Any, assertion: SingleAssertionModel) -> tuple[bool, str]:
    failure_details: list[str] = []

    if not isinstance(actual, list):
        return False, "Expected an array, but got a different type."

    for item_index, item in enumerate(actual):
        item_failure_details: list[str] = []

        for item_check in assertion.conditions:
            try:
                value = getValueFromJsonPath(item, item_check.path) if item_check.path else item
            except KeyError as e:
                item_failure_details.append(
                    f"Item at index {item_index}: {e.args[0]}"
                )
                continue

            operator_passed, operator_failure_detail = handle_operator(
                item_check.operator,
                value,
                item_check,
            )

            if not operator_passed:
                item_failure_details.append(
                    f"Item at index {item_index}, path '{item_check.path}', operator '{item_check.operator}': {operator_failure_detail}"
                )

        if not item_failure_details:
            return True, ""

        failure_details.extend(item_failure_details)

    return False, "No item matched all conditions.\n" + "\n".join(failure_details)

def define_operator_result(
    passed: bool,
    failure_message: str | None = None,
) -> tuple[bool, str]:
    if passed:
        return True, ""

    return False, (failure_message or "")

operator_map = {
    "equals":             lambda actual, assertion: define_operator_result(actual == assertion.value, f"Expected {assertion.value!r} ({type(assertion.value).__name__}), " f"but got {actual!r} ({type(actual).__name__})"),
    "not_equals":         lambda actual, assertion: define_operator_result(actual != assertion.value, f"Expected {assertion.value!r} ({type(assertion.value).__name__}) to not equal actual value {actual!r} ({type(actual).__name__})"),
    "exists":             lambda actual, assertion: define_operator_result(actual is not None, f"Expected field to exist, but it was None"),
    "is_number":          lambda actual, assertion: define_operator_result(isinstance(actual, (int, float)) and not isinstance(actual, bool), f"Expected a number, but got {type(actual).__name__}"),
    "is_string":          lambda actual, assertion: define_operator_result(isinstance(actual, str), f"Expected a string, but got {type(actual).__name__}"),
    "is_boolean":         lambda actual, assertion: define_operator_result(isinstance(actual, bool), f"Expected a boolean, but got {type(actual).__name__}"),
    "is_array":           lambda actual, assertion: define_operator_result(isinstance(actual, list), f"Expected an array, but got {type(actual).__name__}"),
    "is_object":          lambda actual, assertion: define_operator_result(isinstance(actual, dict), f"Expected an object, but got {type(actual).__name__}"),
    "greater_than":       lambda actual, assertion: define_operator_result(isinstance(actual, (int, float)) and actual > assertion.value, f"Expected {assertion.value}, but got {actual}"),
    "less_than":          lambda actual, assertion: define_operator_result(isinstance(actual, (int, float)) and actual < assertion.value, f"Expected {assertion.value}, but got {actual}"),
    "contains" :          lambda actual, assertion: define_operator_result(
        (assertion.value in actual) if isinstance(actual, str) and isinstance(assertion.value, str)
        else (assertion.value in actual) if isinstance(actual, list)
        else (assertion.value in actual.values()) if isinstance(actual, dict)
        else False,
        f"Expected actual value '{actual}' to contain '{assertion.value}'."
    ),
    
    "every_item_matches": every_item_matches,
    "some_item_matches": some_item_matches,
}

def getValueFromJsonPath(json: dict[str, Any], path: str) -> Any:
        path_segments = path.split(".")
        value = json
        for segment in path_segments:
            if isinstance(value, dict) and segment in value:
                value = value[segment]
            elif isinstance(value, list) and segment.isdigit():
                list_index = int(segment)
                
                # checking if the list index exists to avoid IndexError
                if list_index < len(value):
                    value = value[list_index]
                else:
                    raise KeyError(f"Path '{path}' does not exist in the JSON response.")
            else:
                raise KeyError(f"Path '{path}' does not exist in the JSON response.")
        return value
    
def handle_operator(operator: str, actual_value: Any, assertion: Any) -> tuple[bool, str]:
    # assertion can be either a SingleAssertionModel or a RuleItemModel depending on the operator
    if operator in operator_map:
        return operator_map[operator](actual_value, assertion)
    else:
        raise ValueError(f"Unsupported operator: {operator}")

def test_single_assertion(assertion: SingleAssertionModel, response: httpx.Response) -> tuple[bool, str]:
        if assertion.type == "json_body":
            if "application/json" in response.headers.get("Content-Type", ""):
                # check if the response body is valid JSON
                try:
                    response_json = response.json()
                except ValueError:
                    return False, "Response body is not valid JSON."   
                # check if the specified JSON path exists in the response JSON and get the actual value at that path
                try:
                    actual_value = getValueFromJsonPath(response_json, assertion.path) if assertion.path else response_json
                except KeyError as e:
                    return False, e.args[0] # used args[0] to avoid getting the quote-wrapped version of the error message
                # evaluate the assertion based on the operator, expected value, actual value, and any additional conditions
                try:
                    assertion_passed, assertion_failure_message = handle_operator(assertion.operator, actual_value, assertion)
                except ValueError as e:
                    return False, str(e)
                # return the result of the assertion along with any failure details if the assertion failed
                if assertion_passed:
                    return True, ""
                else:
                    return False, (
                        f"Assertion failed for JSON body.\n"
                        f"Path: '{assertion.path}'\n"
                        f"Operator: '{assertion.operator}'\n"
                        f"Details:\n{assertion_failure_message}"
                    )
            else:
                return False, "Expected JSON response, but got different Content-Type. Actual Content-Type: " + response.headers.get("Content-Type", "")
        else:
            return False, f"Unsupported assertion type: {assertion.type}"
    
async def send_test_request(test_case: SingleTestCaseRequest) -> httpx.Response:
    method = test_case.method.lower()
    max_time_seconds = test_case.max_response_time_ms / 1000
    methods_with_body = {"post", "put", "patch"}
    # I'm using kwargs here to conditionally add the JSON body to the request if it's needed
    request_kwargs: dict[str, Any] = { "timeout": max_time_seconds }
    # Add the json body to the request if it's a method that supports a body and if a body is provided in the test case
    if method in methods_with_body and test_case.body is not None: 
        request_kwargs["json"] = test_case.body
    # Add headers to the request if headers are provided in the test case
    if test_case.headers is not None:
        request_kwargs["headers"] = test_case.headers
    # Add query parameters to the request if query parameters are provided in the test case
    if test_case.query_params is not None:
        request_kwargs["params"] = test_case.query_params
    
    async with httpx.AsyncClient() as client: # creates an async HTTP client and closes it when done
        method_func = getattr(client, method)
        return await method_func(str(test_case.url), **request_kwargs,) 

async def run_single_test_case(test_case: SingleTestCaseRequest) -> SingleTestCaseResult:
    result = SingleTestCaseResult(
        name=test_case.name,
        status="passed",
        failure_details=[],
        )
    
    # MVP
    # TODO: run multiple test cases instead of only one - DONE!
    # This makes the endpoint useful for real test runs.
    # TODO: run test cases concurrently with async - DONE!
    # This makes multiple checks faster instead of waiting one by one like a caveman.
    # TODO: add max_response_time_ms validation - DONE!
    # Fail the test if the API takes too long to respond.
    # TODO: support more HTTP methods - DONE!
    # Add POST, PUT, PATCH, and DELETE instead of only GET.
    # TODO: support request body payloads - DONE!
    # Needed for POST/PUT/PATCH tests where the API expects data.
    # TODO: support request headers - DONE!
    # Needed for APIs that require headers like Content-Type or Authorization.
    # TODO: support query parameters - DONE!
    # Needed for URLs like /users?page=1&limit=10 without manually stuffing it into the URL.
    # TODO: support list indexes in JSON paths - DONE!
    # Example: users.0.id should get the first user's id.
    # TODO: improve failure details for nested array/item checks - DONE!
    # Make failed every_item_matches / some_item_matches errors easier to understand.
    # TODO: validate bad assertions and unsupported operators - DONE!
    # Catch cursed input early, like missing path/value or operator names that do not exist.
    # TODO: make sure one failed test does not break the whole test run - DONE!
    # One trash test case should fail cleanly, not crash everything.
    
    # Later - nice but not needed for MVP
    # TODO: support response header assertions
    # Example: check if Content-Type header contains application/json.
    # Example: check if a custom header X-RateLimit-Remaining is greater than 0.
    # Example: X-Request-ID exists.
    # Useful for validating API metadata, caching headers, auth headers, rate limits, and content types.
    # TODO: support response text/body checks for non-JSON responses
    # Example: HTML page contains "Login".
    # TODO: support response header checks
    # Example: Content-Type contains application/json.
    # TODO: retry failed requests
    # Useful for flaky APIs, but not needed right now.
    # TODO: add follow redirects option
    # Useful when endpoints return 301/302 redirects.
    # TODO: save test run history
    # Store previous runs so users can see what passed/failed over time.
    # TODO: scheduled test runs
    # Run checks automatically every X minutes/hours.
    # TODO: notifications/alerts when tests fail
    # Email/Discord/Slack alerts when something breaks.
    # TODO: dashboard analytics and trends
    # Charts for uptime, response time, failures, etc.
     
    try:
        response = await send_test_request(test_case)
    except httpx.TimeoutException:
        result.status = "failed"
        result.failure_details.append(f"Request timed out after {test_case.max_response_time_ms} ms.")
        return result
    except httpx.RequestError as exc:
        result.failure_details.append(
            f"Request failed for {exc.request.url!r}. Reason: {str(exc)}"
        )

        # Returning early since we couldn't get a response to validate against expected status code or assertions
        result.status = "failed"
        return result
    except ValueError as exc:
        result.failure_details.append(str(exc))
        result.status = "failed"
        return result
    else: # If the request succeeded, check the response against the expected status code and assertions
        try:
            response_body = response.json()
        except ValueError:
            response_body = response.text

        result.response = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response_body,
        }
        
        response_status_code = response.status_code
        expected_status_code = test_case.expected_status_code

        # First check if the response status code matches the expected status code
        if response_status_code != expected_status_code: # I didn't check if it existed because it is a required field, so it should always exist
            result.failure_details.append(f"Response status code '{response_status_code}' does not match expected status code '{expected_status_code}'.")
        # Check assertions if assertions are provided
        if test_case.assertions is not None:
            assertions = test_case.assertions
            
            for assertion in assertions:
                assertion_passed, assertion_failure_detail = test_single_assertion(assertion, response)
                if not assertion_passed:
                    result.failure_details.append(assertion_failure_detail)

    # Determine overall test case status based on failure details
    result.status = "failed" if result.failure_details else "passed"

    return result

async def run_multiple_test_case(test_cases: list[SingleTestCaseRequest]) -> list[SingleTestCaseResult]:
    test_cases_results = []

    for test_case in test_cases:
        try:
            test_result = await run_single_test_case(test_case)
            test_cases_results.append(test_result)
        except Exception as exc:
            test_cases_results.append(exc)

    final_results: list[SingleTestCaseResult] = []

    for test_case, test_result in zip(test_cases, test_cases_results):
        if isinstance(test_result, BaseException):
            final_results.append(
                SingleTestCaseResult(
                    name=test_case.name,
                    status="failed",
                    failure_details=[
                        f"Unexpected test error: {str(test_result)}"
                    ],
                )
            )
        else:
            final_results.append(test_result)


    return final_results