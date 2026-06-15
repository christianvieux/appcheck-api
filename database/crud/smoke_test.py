from database.crud.base import BaseCRUD
from database.models import SmokeTest, TestSuite


SMOKE_TEST_RESPONSE_LOAD_OPTIONS = ()


class SmokeTestCRUD(BaseCRUD):
    def suite_exists(self, db_connection, suite_id: int):
        return (
            db_connection
            .query(TestSuite)
            .filter(TestSuite.id == suite_id)
            .first()
        )

    def list_by_suite(self, db_connection, suite_id: int):
        return (
            db_connection
            .query(self.Model)
            .options(*SMOKE_TEST_RESPONSE_LOAD_OPTIONS)
            .filter(self.Model.suite_id == suite_id)
            .all()
        )


smoke_test_crud = SmokeTestCRUD(SmokeTest)
