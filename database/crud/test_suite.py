from database.crud.base import BaseCRUD
from database.models import TestSuite, Target


class TestSuiteCRUD(BaseCRUD):
    def list_by_target(self, db_connection, target_id: int):
        return (
            db_connection
            .query(self.Model)
            .filter(self.Model.target_id == target_id)
            .all()
        )

    def target_exists(self, db_connection, target_id: int):
        return (
            db_connection
            .query(Target)
            .filter(Target.id == target_id)
            .first()
        )


test_suite_crud = TestSuiteCRUD(TestSuite)