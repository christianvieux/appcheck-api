from fastapi import APIRouter, Depends, HTTPException
from database.crud.project import project_crud
from services.database import start_database_session
from models.project import PostProjectRequestBody, UpdateProjectRequestBody
from sqlalchemy.exc import SQLAlchemyError
from services.auth import CurrentUser, get_current_user

router = APIRouter()


@router.post("/project", status_code=200)
async def create_project(
    request_body: PostProjectRequestBody,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        new_project = project_crud.create(
            database_session,
            {
                "owner_id": current_user.id,
                "name": request_body.name,
                "description": request_body.description,
            },
        )

        return new_project

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
async def list_projects(current_user: CurrentUser = Depends(get_current_user)):
    database_session = start_database_session()

    try:
        projects = (
            database_session
            .query(project_crud.Model)
            .filter(project_crud.Model.owner_id == current_user.id)
            .all()
        )

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
async def get_project(
    project_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        project = (
            database_session
            .query(project_crud.Model)
            .filter(
                project_crud.Model.id == project_id,
                project_crud.Model.owner_id == current_user.id,
            )
            .first()
        )

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        return project

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
async def update_project(
    project_id: int,
    request_body: UpdateProjectRequestBody,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        project = (
            database_session
            .query(project_crud.Model)
            .filter(
                project_crud.Model.id == project_id,
                project_crud.Model.owner_id == current_user.id,
            )
            .first()
        )

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        update_data = request_body.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if value is not None:
                setattr(project, key, value)

        database_session.commit()
        database_session.refresh(project)

        return project

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
async def delete_project(
    project_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        deleted_project = (
            database_session
            .query(project_crud.Model)
            .filter(
                project_crud.Model.id == project_id,
                project_crud.Model.owner_id == current_user.id,
            )
            .first()
        )

        if not deleted_project:
            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        database_session.delete(deleted_project)
        database_session.commit()

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
