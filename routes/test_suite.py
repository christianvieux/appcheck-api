from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from Database.crud.test_suite import test_suite_crud
from services.database import start_database_session
from models.test_suite import PostTestSuiteRequestBody, UpdateTestSuiteRequestBody


router = APIRouter()


@router.post("/test-suite", status_code=200)
async def create_test_suite(request_body: PostTestSuiteRequestBody):
    database_session = start_database_session()

    try:
        target = test_suite_crud.target_exists(
            database_session,
            request_body.target_id,
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

        return {
            "message": "Test suite created!",
            "test_suite": new_test_suite,
        }

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


@router.get("/target/{target_id}/test-suites", status_code=200)
async def list_test_suites_for_target(target_id: int):
    database_session = start_database_session()

    try:
        target = test_suite_crud.target_exists(
            database_session,
            target_id,
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
async def get_test_suite(test_suite_id: int):
    database_session = start_database_session()

    try:
        test_suite = test_suite_crud.read(
            database_session,
            test_suite_id,
        )

        if not test_suite:
            raise HTTPException(
                status_code=404,
                detail="Test suite not found.",
            )

        return {
            "test_suite": test_suite,
        }

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
):
    database_session = start_database_session()

    try:
        update_data = request_body.model_dump(exclude_unset=True)

        updated_test_suite = test_suite_crud.update(
            database_session,
            test_suite_id,
            update_data,
        )

        if not updated_test_suite:
            raise HTTPException(
                status_code=404,
                detail="Test suite not found.",
            )

        return {
            "message": "Test suite updated!",
            "test_suite": updated_test_suite,
        }

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
async def delete_test_suite(test_suite_id: int):
    database_session = start_database_session()

    try:
        deleted_test_suite = test_suite_crud.delete(
            database_session,
            test_suite_id,
        )

        if not deleted_test_suite:
            raise HTTPException(
                status_code=404,
                detail="Test suite not found.",
            )

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