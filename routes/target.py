from fastapi import APIRouter, Depends, HTTPException
from database.crud.target import target_crud
from database.models import Project, Target
from services.database import start_database_session
from models.target import PostTargetRequestBody, UpdateTargetRequestBody
from sqlalchemy.exc import SQLAlchemyError
from services.auth import CurrentUser, get_current_user

router = APIRouter()


@router.post("/target", status_code=200)
async def create_target(
    request_body: PostTargetRequestBody,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        project = (
            database_session
            .query(Project)
            .filter(
                Project.id == request_body.project_id,
                Project.owner_id == current_user.id,
            )
            .first()
        )

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        new_target = target_crud.create(
            database_session,
            {
                "project_id": request_body.project_id,
                "name": request_body.name,
                "url": str(request_body.url),
                "target_type": request_body.target_type,
            },
        )

        return new_target

    except HTTPException:
        raise

    except SQLAlchemyError:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while creating the target.",
        )

    except Exception:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()

@router.get("/project/{project_id}/targets", status_code=200)
async def list_targets_for_project(
    project_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        project = (
            database_session
            .query(Project)
            .filter(
                Project.id == project_id,
                Project.owner_id == current_user.id,
            )
            .first()
        )

        if not project:
            raise HTTPException(
                status_code=404,
                detail="Project not found.",
            )

        targets = target_crud.list_by_project(
            database_session,
            project_id,
        )

        return {
            "targets": targets,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while retrieving targets.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()

@router.get("/target/{target_id}", status_code=200)
async def get_target(
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

        return target

    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while retrieving the target.",
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()

@router.put("/target/{target_id}", status_code=200)
async def update_target(
    target_id: int,
    request_body: UpdateTargetRequestBody,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        update_data = request_body.model_dump(exclude_unset=True)

        if "url" in update_data:
            update_data["url"] = str(update_data["url"])

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

        for key, value in update_data.items():
            if value is not None:
                setattr(target, key, value)

        database_session.commit()
        database_session.refresh(target)

        return target

    except HTTPException:
        raise

    except SQLAlchemyError:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while updating the target.",
        )

    except Exception:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()

@router.delete("/target/{target_id}", status_code=200)
async def delete_target(
    target_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    database_session = start_database_session()

    try:
        deleted_target = (
            database_session
            .query(Target)
            .join(Project, Target.project_id == Project.id)
            .filter(
                Target.id == target_id,
                Project.owner_id == current_user.id,
            )
            .first()
        )

        if not deleted_target:
            raise HTTPException(
                status_code=404,
                detail="Target not found.",
            )

        database_session.delete(deleted_target)
        database_session.commit()

        return {
            "message": "Target deleted!",
            "target": deleted_target,
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while deleting the target.",
        )

    except Exception:
        database_session.rollback()

        raise HTTPException(
            status_code=500,
            detail="Unexpected server error.",
        )

    finally:
        database_session.close()
