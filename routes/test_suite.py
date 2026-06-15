from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from database.crud.test_suite import TEST_SUITE_RESPONSE_LOAD_OPTIONS, test_suite_crud
from database.models import Project, Target, TestSuite
from models.smoke_test_run_result import (
    SmokeTestRunGroupResponse,
    SmokeTestRunGroupSummaryResponse,
    SmokeTestRunResultResponse,
)
from models.test_suite import TestSuiteCreate, TestSuiteResponse, TestSuiteUpdate
from services.auth import CurrentUser, get_current_user
from services.database import start_database_session
from services.smoke_test_run_service import smoke_test_run_service

router = APIRouter()


@router.post("/test-suite", status_code=200, response_model=TestSuiteResponse)
async def create_test_suite(
    request_body: TestSuiteCreate,
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

        return (
            database_session
            .query(TestSuite)
            .options(*TEST_SUITE_RESPONSE_LOAD_OPTIONS)
            .filter(TestSuite.id == new_test_suite.id)
            .first()
        )

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


@router.get("/test-suite/{suite_id}/runs", status_code=200, response_model=list[SmokeTestRunGroupSummaryResponse])
async def list_run_groups_for_suite(
    suite_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        return smoke_test_run_service.list_run_groups_for_suite(
            database_session,
            suite_id,
            current_user.id,
        )

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while retrieving run groups.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()


@router.get("/runs/{run_group_id}", status_code=200, response_model=SmokeTestRunGroupResponse)
async def get_run_group(
    run_group_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        return smoke_test_run_service.get_run_group(
            database_session,
            run_group_id,
            current_user.id,
        )

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while retrieving the run group.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()


@router.get("/runs/{run_group_id}/results", status_code=200, response_model=list[SmokeTestRunResultResponse])
async def list_results_for_run_group(
    run_group_id: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        results = smoke_test_run_service.list_results_for_group(
            database_session,
            run_group_id,
            current_user.id,
        )

        return [
            smoke_test_run_service.serialize_result(result)
            for result in results
        ]

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while retrieving run results.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()


@router.get("/target/{target_id}/test-suites", status_code=200, response_model=list[TestSuiteResponse])
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

        return test_suites

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


@router.get("/test-suite/{test_suite_id}", status_code=200, response_model=TestSuiteResponse)
async def get_test_suite(
    test_suite_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        test_suite = (
            database_session
            .query(TestSuite)
            .options(*TEST_SUITE_RESPONSE_LOAD_OPTIONS)
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


@router.put("/test-suite/{test_suite_id}", status_code=200, response_model=TestSuiteResponse)
async def update_test_suite(
    test_suite_id: int,
    request_body: TestSuiteUpdate,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        update_data = request_body.model_dump(exclude_unset=True)

        test_suite = (
            database_session
            .query(TestSuite)
            .options(*TEST_SUITE_RESPONSE_LOAD_OPTIONS)
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

        return (
            database_session
            .query(TestSuite)
            .options(*TEST_SUITE_RESPONSE_LOAD_OPTIONS)
            .filter(TestSuite.id == test_suite.id)
            .first()
        )

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
