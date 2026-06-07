from fastapi import APIRouter, HTTPException
from Database.crud.project import project_crud
from services.database import start_database_session
from models.project import PostProjectRequestBody, UpdateProjectRequestBody
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()


@router.post("/project", status_code=200)
async def create_project(request_body: PostProjectRequestBody):
    database_session = start_database_session()

    try:
        new_project = project_crud.create(
            database_session,
            {
                "name": request_body.name,
                "description": request_body.description,
            },
        )

        return {
            "message": "Project created!",
            "project": new_project,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while creating the project.",
        )

    except Exception:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()

@router.get("/projects", status_code=200)
async def list_projects():
    database_session = start_database_session()

    try:
        projects = project_crud.list(database_session)

        return {
            "projects": projects,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while retrieving projects.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()

@router.get("/project/{project_id}", status_code=200)
async def get_project(project_id: int):
    database_session = start_database_session()

    try:
        project = project_crud.read(database_session, project_id)

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        return {
            "project": project,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while retrieving the project.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()

@router.put("/project/{project_id}", status_code=200)
async def update_project(project_id: int, request_body: UpdateProjectRequestBody):
    database_session = start_database_session()

    try:
        updated_project = project_crud.update(
            database_session,
            project_id,
            {
                "name": request_body.name,
                "description": request_body.description,
            },
        )

        if not updated_project:
            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        return {
            "message": "Project updated!",
            "project": updated_project,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while updating the project.",
        )

    except Exception:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()

@router.delete("/project/{project_id}", status_code=200)
async def delete_project(project_id: int):
    database_session = start_database_session()

    try:
        deleted_project = project_crud.delete(database_session, project_id)

        if not deleted_project:
            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        return {
            "message": "Project deleted!",
            "project": deleted_project,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while deleting the project.",
        )

    except Exception:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()