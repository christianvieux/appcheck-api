from sqlalchemy.orm import selectinload

from database.crud.base import BaseCRUD
from database.models import Project, Target, TestSuite


TARGET_RESPONSE_LOAD_OPTIONS = (
    selectinload(Target.test_suites)
    .selectinload(TestSuite.smoke_tests),
)


class TargetCRUD(BaseCRUD):
    def list_by_project(self, db_connection, project_id: int):
        return (
            db_connection
            .query(self.Model)
            .options(*TARGET_RESPONSE_LOAD_OPTIONS)
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
