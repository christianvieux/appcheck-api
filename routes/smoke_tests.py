from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from database.crud.smoke_test import smoke_test_crud
from database.models import Project, SmokeTest, Target, TestSuite
from services.auth import CurrentUser, get_current_user
from services.database import start_database_session
from services.smoke_tests_runner import run_multiple_smoke_tests as svc_run_multiple_smoke_tests, run_single_smoke_test as svc_run_single_smoke_test
from models.smoke_tests import SmokeTestCreate, SmokeTestUpdate, RunSmokeTestsRequest, SingleSmokeTestRequest


router = APIRouter()


@router.post("/smoke-test", status_code=200)
async def create_smoke_test(
    request_body: SmokeTestCreate,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        suite = (
            database_session
            .query(TestSuite)
            .join(Target, TestSuite.target_id == Target.id)
            .join(Project, Target.project_id == Project.id)
            .filter(
                TestSuite.id == request_body.suite_id,
                Project.owner_id == current_user.id,
            )
            .first()
        )

        if not suite:
            raise HTTPException(
                status_code=404,
                detail="Test suite not found.",
            )

        target = (
            database_session
            .query(Target)
            .join(Project, Target.project_id == Project.id)
            .filter(
                Target.id == request_body.target_id,
                Project.owner_id == current_user.id,
            )
            .first()
        )

        if not target:
            raise HTTPException(
                status_code=404,
                detail="Target not found.",
            )

        new_smoke_test = smoke_test_crud.create(
            database_session,
            {
                "suite_id": request_body.suite_id,
                "target_id": request_body.target_id,
                "name": request_body.name,
                "description": request_body.description,
                "method": request_body.method,
                "path": request_body.path,
                "headers": request_body.headers,
                "query_params": request_body.query_params,
                "body": request_body.body,
                "expected_status": request_body.expected_status,
                "max_response_time_ms": request_body.max_response_time_ms,
                "assertions": [
                    assertion.model_dump()
                    for assertion in request_body.assertions
                ],
            },
        )

        return new_smoke_test

    except HTTPException:
        raise

    except SQLAlchemyError:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while creating the smoke test.",
        )

    except Exception:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()


@router.get("/test-suite/{suite_id}/smoke-tests", status_code=200)
async def list_smoke_tests_for_suite(
    suite_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        suite = (
            database_session
            .query(TestSuite)
            .join(Target, TestSuite.target_id == Target.id)
            .join(Project, Target.project_id == Project.id)
            .filter(
                TestSuite.id == suite_id,
                Project.owner_id == current_user.id,
            )
            .first()
        )

        if not suite:
            raise HTTPException(
                status_code=404,
                detail="Test suite not found.",
            )

        smoke_tests = smoke_test_crud.list_by_suite(
            database_session,
            suite_id,
        )

        return {
            "smoke_tests": smoke_tests,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while retrieving smoke tests.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()


@router.get("/smoke-test/{smoke_test_id}", status_code=200)
async def get_smoke_test(
    smoke_test_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        smoke_test = (
            database_session
            .query(SmokeTest)
            .join(TestSuite, SmokeTest.suite_id == TestSuite.id)
            .join(Target, TestSuite.target_id == Target.id)
            .join(Project, Target.project_id == Project.id)
            .filter(
                SmokeTest.id == smoke_test_id,
                Project.owner_id == current_user.id,
            )
            .first()
        )

        if not smoke_test:
            raise HTTPException(
                status_code=404,
                detail="Smoke test not found.",
            )

        return smoke_test

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while retrieving the smoke test.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()


@router.put("/smoke-test/{smoke_test_id}", status_code=200)
async def update_smoke_test(
    smoke_test_id: int,
    request_body: SmokeTestUpdate,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        update_data = request_body.model_dump(exclude_unset=True)

        if "assertions" in update_data and update_data["assertions"] is not None:
            update_data["assertions"] = [
                assertion.model_dump() if hasattr(assertion, "model_dump") else assertion
                for assertion in update_data["assertions"]
            ]

        smoke_test = (
            database_session
            .query(SmokeTest)
            .join(TestSuite, SmokeTest.suite_id == TestSuite.id)
            .join(Target, TestSuite.target_id == Target.id)
            .join(Project, Target.project_id == Project.id)
            .filter(
                SmokeTest.id == smoke_test_id,
                Project.owner_id == current_user.id,
            )
            .first()
        )

        if not smoke_test:
            raise HTTPException(
                status_code=404,
                detail="Smoke test not found.",
            )

        for key, value in update_data.items():
            if value is not None:
                setattr(smoke_test, key, value)

        database_session.commit()
        database_session.refresh(smoke_test)

        return smoke_test

    except HTTPException:
        raise

    except SQLAlchemyError:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while updating the smoke test.",
        )

    except Exception:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()


@router.delete("/smoke-test/{smoke_test_id}", status_code=200)
async def delete_smoke_test(
    smoke_test_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        deleted_smoke_test = (
            database_session
            .query(SmokeTest)
            .join(TestSuite, SmokeTest.suite_id == TestSuite.id)
            .join(Target, TestSuite.target_id == Target.id)
            .join(Project, Target.project_id == Project.id)
            .filter(
                SmokeTest.id == smoke_test_id,
                Project.owner_id == current_user.id,
            )
            .first()
        )

        if not deleted_smoke_test:
            raise HTTPException(
                status_code=404,
                detail="Smoke test not found.",
            )

        database_session.delete(deleted_smoke_test)
        database_session.commit()

        return {
            "message": "Smoke test deleted!",
            "smoke_test": deleted_smoke_test,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while deleting the smoke test.",
        )

    except Exception:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()


#
@router.post("/run-smoke-tests", status_code=200) # better than "/health" :P
async def run_smoke_tests(request: RunSmokeTestsRequest):

    tests_results = await svc_run_multiple_smoke_tests(request.smoke_tests)

    # calculating summary
    total_tests = len(request.smoke_tests)
    number_of_failed_tests = sum(1 for test_result in tests_results if test_result.status == "failed")
    number_of_passed_tests = total_tests - number_of_failed_tests
    
    overall_status = "failed" if number_of_failed_tests > 0 else "passed"
    message = "Test run completed. " +(
        "All smoke tests passed."
        if number_of_failed_tests == 0
        else "Some smoke tests failed."
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

@router.post("/run-single-smoke-test", status_code=200)
async def run_single_smoke_test(smoke_test: SingleSmokeTestRequest):
    test_result = await svc_run_single_smoke_test(smoke_test)
    return test_result  # return the single smoke test result
