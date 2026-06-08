from database.crud.base import BaseCRUD
from database.models import SmokeTest, TestSuite, Target


class SmokeTestCRUD(BaseCRUD):
    def suite_exists(self, db_connection, suite_id: int):
        return (
            db_connection
            .query(TestSuite)
            .filter(TestSuite.id == suite_id)
            .first()
        )

    def target_exists(self, db_connection, target_id: int):
        return (
            db_connection
            .query(Target)
            .filter(Target.id == target_id)
            .first()
        )

    def list_by_suite(self, db_connection, suite_id: int):
        return (
            db_connection
            .query(self.Model)
            .filter(self.Model.suite_id == suite_id)
            .all()
        )


smoke_test_crud = SmokeTestCRUD(SmokeTest)