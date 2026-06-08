from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from database.crud.test_suite import test_suite_crud
from database.models import Project, Target, TestResult, TestRun, TestSuite
from services.auth import CurrentUser, get_current_user
from services.database import start_database_session
from models.test_suite import (
    PostTestSuiteRequestBody,
    TestResultResponse,
    TestRunDetailResponse,
    TestRunResponse,
    UpdateTestSuiteRequestBody,
)
from services.suite_runner import suite_runner

router = APIRouter()


@router.post("/test-suite", status_code=200)
async def create_test_suite(
    request_body: PostTestSuiteRequestBody,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
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

        new_test_suite = test_suite_crud.create(
            database_session,
            {
                "target_id": request_body.target_id,
                "name": request_body.name,
                "description": request_body.description,
            },
        )

        return new_test_suite

    except HTTPException:
        raise

    except SQLAlchemyError:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while creating the test suite.",
        )

    except Exception:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()

@router.post("/test-suite/{suite_id}/run", status_code=200, response_model=TestRunDetailResponse)
async def run_smoke_test_suite(
    suite_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        suite_run_result = await suite_runner.run_smoke_suite(
            database_session,
            suite_id,
            current_user.id,
        )

        return suite_run_result

    except HTTPException:
        raise

    except SQLAlchemyError:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while running the test suite.",
        )

    except Exception:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()

@router.get("/test-suite/{suite_id}/runs", status_code=200, response_model=list[TestRunResponse])
async def list_test_runs_for_suite(
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
            .filter(TestSuite.id == suite_id)
            .filter(Project.owner_id == current_user.id)
            .first()
        )

        if not suite:
            raise HTTPException(
                status_code=404,
                detail="Test suite not found.",
            )

        test_runs = (
            database_session
            .query(TestRun)
            .filter(TestRun.suite_id == suite_id)
            .order_by(TestRun.created_at.desc(), TestRun.id.desc())
            .all()
        )

        return [
            suite_runner.serialize_test_run(test_run)
            for test_run in test_runs
        ]

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while retrieving test runs.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()

@router.get("/runs/{run_id}", status_code=200, response_model=TestRunDetailResponse)
async def get_test_run(
    run_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        test_run = (
            database_session
            .query(TestRun)
            .join(TestSuite, TestRun.suite_id == TestSuite.id)
            .join(Target, TestSuite.target_id == Target.id)
            .join(Project, Target.project_id == Project.id)
            .filter(TestRun.id == run_id)
            .filter(Project.owner_id == current_user.id)
            .first()
        )

        if not test_run:
            raise HTTPException(
                status_code=404,
                detail="Test run not found.",
            )

        return {
            **suite_runner.serialize_test_run(test_run),
            "results": [
                suite_runner.serialize_test_result(result)
                for result in test_run.results
            ],
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while retrieving the test run.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()

@router.get("/runs/{run_id}/results", status_code=200, response_model=list[TestResultResponse])
async def list_test_results_for_run(
    run_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        test_run = (
            database_session
            .query(TestRun)
            .join(TestSuite, TestRun.suite_id == TestSuite.id)
            .join(Target, TestSuite.target_id == Target.id)
            .join(Project, Target.project_id == Project.id)
            .filter(TestRun.id == run_id)
            .filter(Project.owner_id == current_user.id)
            .first()
        )

        if not test_run:
            raise HTTPException(
                status_code=404,
                detail="Test run not found.",
            )

        test_results = (
            database_session
            .query(TestResult)
            .filter(TestResult.test_run_id == run_id)
            .order_by(TestResult.id.asc())
            .all()
        )

        return [
            suite_runner.serialize_test_result(test_result)
            for test_result in test_results
        ]

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while retrieving test results.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()

@router.get("/target/{target_id}/test-suites", status_code=200)
async def list_test_suites_for_target(
    target_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        target = (
            database_session
            .query(Target)
            .join(Project, Target.project_id == Project.id)
            .filter(
                Target.id == target_id,
                Project.owner_id == current_user.id,
            )
            .first()
        )

        if not target:
            raise HTTPException(
                status_code=404,
                detail="Target not found.",
            )

        test_suites = test_suite_crud.list_by_target(
            database_session,
            target_id,
        )

        return {
            "test_suites": test_suites,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while retrieving test suites.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()

@router.get("/test-suite/{test_suite_id}", status_code=200)
async def get_test_suite(
    test_suite_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        test_suite = (
            database_session
            .query(TestSuite)
            .join(Target, TestSuite.target_id == Target.id)
            .join(Project, Target.project_id == Project.id)
            .filter(
                TestSuite.id == test_suite_id,
                Project.owner_id == current_user.id,
            )
            .first()
        )

        if not test_suite:
            raise HTTPException(
                status_code=404,
                detail="Test suite not found.",
            )

        return test_suite

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while retrieving the test suite.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()

@router.put("/test-suite/{test_suite_id}", status_code=200)
async def update_test_suite(
    test_suite_id: int,
    request_body: UpdateTestSuiteRequestBody,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        update_data = request_body.model_dump(exclude_unset=True)

        test_suite = (
            database_session
            .query(TestSuite)
            .join(Target, TestSuite.target_id == Target.id)
            .join(Project, Target.project_id == Project.id)
            .filter(
                TestSuite.id == test_suite_id,
                Project.owner_id == current_user.id,
            )
            .first()
        )

        if not test_suite:
            raise HTTPException(
                status_code=404,
                detail="Test suite not found.",
            )

        for key, value in update_data.items():
            if value is not None:
                setattr(test_suite, key, value)

        database_session.commit()
        database_session.refresh(test_suite)

        return test_suite

    except HTTPException:
        raise

    except SQLAlchemyError:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while updating the test suite.",
        )

    except Exception:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()

@router.delete("/test-suite/{test_suite_id}", status_code=200)
async def delete_test_suite(
    test_suite_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        deleted_test_suite = (
            database_session
            .query(TestSuite)
            .join(Target, TestSuite.target_id == Target.id)
            .join(Project, Target.project_id == Project.id)
            .filter(
                TestSuite.id == test_suite_id,
                Project.owner_id == current_user.id,
            )
            .first()
        )

        if not deleted_test_suite:
            raise HTTPException(
                status_code=404,
                detail="Test suite not found.",
            )

        database_session.delete(deleted_test_suite)
        database_session.commit()

        return {
            "message": "Test suite deleted!",
            "test_suite": deleted_test_suite,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while deleting the test suite.",
        )

    except Exception:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()
