from Database.crud.base import BaseCRUD
from Database.models import Target, Project


class TargetCRUD(BaseCRUD):
    def list_by_project(self, db_connection, project_id: int):
        return (
            db_connection
            .query(self.Model)
            .filter(self.Model.project_id == project_id)
            .all()
        )

    def project_exists(self, db_connection, project_id: int):
        return (
            db_connection
            .query(Project)
            .filter(Project.id == project_id)
            .first()
        )


target_crud = TargetCRUD(Target)