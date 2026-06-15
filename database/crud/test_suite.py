from sqlalchemy.orm import selectinload

from database.crud.base import BaseCRUD
from database.models import Target, TestSuite


TEST_SUITE_RESPONSE_LOAD_OPTIONS = (
    selectinload(TestSuite.smoke_tests),
)


class TestSuiteCRUD(BaseCRUD):
    def list_by_target(self, db_connection, target_id: int):
        return (
            db_connection
            .query(self.Model)
            .options(*TEST_SUITE_RESPONSE_LOAD_OPTIONS)
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
