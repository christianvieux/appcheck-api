from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import SQLAlchemyError

from Database.crud.saved_test import saved_test_crud
from services.database import start_database_session
from models.saved_test import SavedTestCreate, SavedTestUpdate


router = APIRouter()


@router.post("/saved-test", status_code=200)
async def create_saved_test(request_body: SavedTestCreate):
    database_session = start_database_session()

    try:
        suite = saved_test_crud.suite_exists(
            database_session,
            request_body.suite_id,
        )

        if not suite:
            raise HTTPException(
                status_code=404,
                detail="Test suite not found.",
            )

        target = saved_test_crud.target_exists(
            database_session,
            request_body.target_id,
        )

        if not target:
            raise HTTPException(
                status_code=404,
                detail="Target not found.",
            )

        new_saved_test = saved_test_crud.create(
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

        return {
            "message": "Saved test created!",
            "saved_test": new_saved_test,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while creating the saved test.",
        )

    except Exception:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()


@router.get("/test-suite/{suite_id}/saved-tests", status_code=200)
async def list_saved_tests_for_suite(suite_id: int):
    database_session = start_database_session()

    try:
        suite = saved_test_crud.suite_exists(
            database_session,
            suite_id,
        )

        if not suite:
            raise HTTPException(
                status_code=404,
                detail="Test suite not found.",
            )

        saved_tests = saved_test_crud.list_by_suite(
            database_session,
            suite_id,
        )

        return {
            "saved_tests": saved_tests,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while retrieving saved tests.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()


@router.get("/saved-test/{saved_test_id}", status_code=200)
async def get_saved_test(saved_test_id: int):
    database_session = start_database_session()

    try:
        saved_test = saved_test_crud.read(
            database_session,
            saved_test_id,
        )

        if not saved_test:
            raise HTTPException(
                status_code=404,
                detail="Saved test not found.",
            )

        return {
            "saved_test": saved_test,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while retrieving the saved test.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()


@router.put("/saved-test/{saved_test_id}", status_code=200)
async def update_saved_test(
    saved_test_id: int,
    request_body: SavedTestUpdate,
):
    database_session = start_database_session()

    try:
        update_data = request_body.model_dump(exclude_unset=True)

        if "assertions" in update_data and update_data["assertions"] is not None:
            update_data["assertions"] = [
                assertion.model_dump() if hasattr(assertion, "model_dump") else assertion
                for assertion in update_data["assertions"]
            ]

        updated_saved_test = saved_test_crud.update(
            database_session,
            saved_test_id,
            update_data,
        )

        if not updated_saved_test:
            raise HTTPException(
                status_code=404,
                detail="Saved test not found.",
            )

        return {
            "message": "Saved test updated!",
            "saved_test": updated_saved_test,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while updating the saved test.",
        )

    except Exception:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()


@router.delete("/saved-test/{saved_test_id}", status_code=200)
async def delete_saved_test(saved_test_id: int):
    database_session = start_database_session()

    try:
        deleted_saved_test = saved_test_crud.delete(
            database_session,
            saved_test_id,
        )

        if not deleted_saved_test:
            raise HTTPException(
                status_code=404,
                detail="Saved test not found.",
            )

        return {
            "message": "Saved test deleted!",
            "saved_test": deleted_saved_test,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while deleting the saved test.",
        )

    except Exception:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()