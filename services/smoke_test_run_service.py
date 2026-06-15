from collections import defaultdict
from datetime import datetime
from typing import Any, cast
from urllib.parse import urljoin
from uuid import uuid4

from fastapi import HTTPException
from pydantic import AnyUrl
from sqlalchemy.orm import selectinload

from database.models import Project, SmokeTest, SmokeTestRunResult, Target, TestSuite
from models.smoke_test_run_result import RunSource, TriggeredBy
from models.smoke_tests import SingleSmokeTestRequest, SingleSmokeTestResult
from services.smoke_tests_runner import run_single_smoke_test


class SmokeTestRunService:
    async def run_saved_smoke_tests(
        self,
        db_connection,
        smoke_test_ids: list[int],
        owner_id: str,
        run_source: RunSource,
        triggered_by: TriggeredBy = "manual",
        run_group_id: str | None = None,
    ):
        group_id = run_group_id or str(uuid4())
        smoke_tests = self.get_owned_smoke_tests(
            db_connection,
            smoke_test_ids,
            owner_id,
        )

        saved_results: list[SmokeTestRunResult] = []

        for smoke_test in smoke_tests:
            started_at = datetime.now()
            target = smoke_test.target or smoke_test.suite.target
            full_url = self.build_full_url(target.url, smoke_test.path)

            try:
                executable_test = self.build_executable_test(
                    smoke_test,
                    full_url,
                )
                test_result = await run_single_smoke_test(executable_test)
            except Exception as exc:
                test_result = SingleSmokeTestResult(
                    name=smoke_test.name,
                    status="failed",
                    failure_details=[f"Unexpected saved test error: {str(exc)}"],
                )

            finished_at = datetime.now()
            result_row = self.build_result_row(
                smoke_test=smoke_test,
                target=target,
                full_url=full_url,
                result=test_result,
                run_group_id=group_id,
                owner_id=owner_id,
                run_source=run_source,
                triggered_by=triggered_by,
                started_at=started_at,
                finished_at=finished_at,
            )

            db_connection.add(result_row)
            saved_results.append(result_row)

        db_connection.commit()

        for saved_result in saved_results:
            db_connection.refresh(saved_result)

        return self.serialize_run_group(
            saved_results,
            message=self.build_run_message(saved_results),
            include_results=True,
        )

    def get_owned_smoke_tests(
        self,
        db_connection,
        smoke_test_ids: list[int],
        owner_id: str,
    ) -> list[SmokeTest]:
        unique_ids = list(dict.fromkeys(smoke_test_ids))

        smoke_tests = (
            db_connection
            .query(SmokeTest)
            .options(
                selectinload(SmokeTest.target),
                selectinload(SmokeTest.suite).selectinload(TestSuite.target),
            )
            .join(Target, SmokeTest.target_id == Target.id)
            .join(Project, Target.project_id == Project.id)
            .filter(
                SmokeTest.id.in_(unique_ids),
                Project.owner_id == owner_id,
            )
            .all()
        )

        smoke_tests_by_id = {
            smoke_test.id: smoke_test
            for smoke_test in smoke_tests
        }

        missing_ids = [
            smoke_test_id
            for smoke_test_id in unique_ids
            if smoke_test_id not in smoke_tests_by_id
        ]

        if missing_ids:
            raise HTTPException(
                status_code=404,
                detail="One or more smoke tests were not found.",
            )

        # SQL IN queries do not preserve input order, so rebuild the list from the request IDs.
        return [smoke_tests_by_id[smoke_test_id] for smoke_test_id in smoke_test_ids]

    def build_executable_test(
        self,
        smoke_test: SmokeTest,
        full_url: str,
    ) -> SingleSmokeTestRequest:
        return SingleSmokeTestRequest(
            name=smoke_test.name,
            url=cast(AnyUrl, full_url),
            method=smoke_test.method,
            expected_status_code=smoke_test.expected_status,
            max_response_time_ms=smoke_test.max_response_time_ms,
            assertions=smoke_test.assertions or [],
            headers=smoke_test.headers,
            body=smoke_test.body,
            query_params=smoke_test.query_params,
        )

    def build_result_row(
        self,
        smoke_test: SmokeTest,
        target: Target,
        full_url: str,
        result: SingleSmokeTestResult,
        run_group_id: str,
        owner_id: str,
        run_source: RunSource,
        triggered_by: TriggeredBy,
        started_at: datetime,
        finished_at: datetime,
    ) -> SmokeTestRunResult:
        result_data = result.model_dump()
        failure_details = self.clean_failure_details(result_data.get("failure_details"))
        response = result_data.get("response") or {}
        status_code = response.get("status_code") if isinstance(response, dict) else None

        return SmokeTestRunResult(
            run_group_id=run_group_id,
            owner_id=owner_id,
            smoke_test_id=smoke_test.id,
            project_id=target.project_id,
            suite_id=smoke_test.suite_id,
            target_id=target.id,
            run_source=run_source,
            triggered_by=triggered_by,
            name_snapshot=smoke_test.name,
            method_snapshot=smoke_test.method,
            url_snapshot=full_url,
            path_snapshot=smoke_test.path,
            expected_status_snapshot=smoke_test.expected_status,
            max_response_time_ms_snapshot=smoke_test.max_response_time_ms,
            assertions_snapshot=smoke_test.assertions or [],
            headers_snapshot=smoke_test.headers,
            query_params_snapshot=smoke_test.query_params,
            body_snapshot=smoke_test.body,
            status=result_data.get("status", "failed"),
            status_code=status_code,
            response_time_ms=result_data.get("response_time_ms"),
            failure_message=failure_details[0] if failure_details else None,
            failure_details=failure_details,
            assertion_results=[],
            started_at=started_at,
            finished_at=finished_at,
        )

    def list_run_groups_for_suite(
        self,
        db_connection,
        suite_id: int,
        owner_id: str,
    ):
        suite = (
            db_connection
            .query(TestSuite)
            .join(Target, TestSuite.target_id == Target.id)
            .join(Project, Target.project_id == Project.id)
            .filter(
                TestSuite.id == suite_id,
                Project.owner_id == owner_id,
            )
            .first()
        )

        if not suite:
            raise HTTPException(
                status_code=404,
                detail="Test suite not found.",
            )

        suite_results = (
            db_connection
            .query(SmokeTestRunResult)
            .filter(
                SmokeTestRunResult.owner_id == owner_id,
                SmokeTestRunResult.suite_id == suite_id,
            )
            .order_by(
                SmokeTestRunResult.created_at.desc(),
                SmokeTestRunResult.id.desc(),
            )
            .all()
        )

        ordered_group_ids = list(dict.fromkeys(
            result.run_group_id
            for result in suite_results
        ))

        if not ordered_group_ids:
            return []

        all_group_results = (
            db_connection
            .query(SmokeTestRunResult)
            .filter(
                SmokeTestRunResult.owner_id == owner_id,
                SmokeTestRunResult.run_group_id.in_(ordered_group_ids),
            )
            .order_by(SmokeTestRunResult.id.asc())
            .all()
        )

        grouped_results = self.group_results(all_group_results)

        return [
            self.serialize_run_group(
                grouped_results[group_id],
                include_results=False,
            )
            for group_id in ordered_group_ids
        ]

    def get_run_group(self, db_connection, run_group_id: str, owner_id: str):
        results = self.list_results_for_group(
            db_connection,
            run_group_id,
            owner_id,
        )

        return self.serialize_run_group(results, include_results=True)

    def list_results_for_group(
        self,
        db_connection,
        run_group_id: str,
        owner_id: str,
    ):
        results = (
            db_connection
            .query(SmokeTestRunResult)
            .filter(
                SmokeTestRunResult.run_group_id == run_group_id,
                SmokeTestRunResult.owner_id == owner_id,
            )
            .order_by(SmokeTestRunResult.id.asc())
            .all()
        )

        if not results:
            raise HTTPException(
                status_code=404,
                detail="Run group not found.",
            )

        return results

    def group_results(self, results: list[SmokeTestRunResult]):
        grouped_results: dict[str, list[SmokeTestRunResult]] = defaultdict(list)

        for result in results:
            grouped_results[result.run_group_id].append(result)

        return grouped_results

    def serialize_run_group(
        self,
        results: list[SmokeTestRunResult],
        message: str | None = None,
        include_results: bool = True,
    ):
        if not results:
            raise HTTPException(
                status_code=404,
                detail="Run group not found.",
            )

        sorted_results = sorted(results, key=lambda result: result.id)
        passed_count = sum(1 for result in sorted_results if result.status == "passed")
        failed_count = sum(1 for result in sorted_results if result.status == "failed")
        started_at = min(result.started_at for result in sorted_results)
        finished_at = max(result.finished_at for result in sorted_results)
        duration_ms = round((finished_at - started_at).total_seconds() * 1000)

        response = {
            "run_group_id": sorted_results[0].run_group_id,
            "run_source": sorted_results[0].run_source,
            "triggered_by": sorted_results[0].triggered_by,
            "status": "failed" if failed_count else "passed",
            "total_tests": len(sorted_results),
            "passed_count": passed_count,
            "failed_count": failed_count,
            "duration_ms": max(duration_ms, 0),
            "project_ids": self.unique_sorted_ids(result.project_id for result in sorted_results),
            "suite_ids": self.unique_sorted_ids(result.suite_id for result in sorted_results),
            "target_ids": self.unique_sorted_ids(result.target_id for result in sorted_results),
            "started_at": started_at,
            "finished_at": finished_at,
            "created_at": sorted_results[0].created_at,
        }

        if message is not None:
            response["message"] = message

        if include_results:
            response["test_results"] = [
                self.serialize_result(result)
                for result in sorted_results
            ]

        return response

    def serialize_result(self, result: SmokeTestRunResult):
        return {
            "id": result.id,
            "run_group_id": result.run_group_id,
            "owner_id": result.owner_id,
            "smoke_test_id": result.smoke_test_id,
            "project_id": result.project_id,
            "suite_id": result.suite_id,
            "target_id": result.target_id,
            "run_source": result.run_source,
            "triggered_by": result.triggered_by,
            "name_snapshot": result.name_snapshot,
            "method_snapshot": result.method_snapshot,
            "url_snapshot": result.url_snapshot,
            "path_snapshot": result.path_snapshot,
            "expected_status_snapshot": result.expected_status_snapshot,
            "max_response_time_ms_snapshot": result.max_response_time_ms_snapshot,
            "assertions_snapshot": result.assertions_snapshot,
            "headers_snapshot": result.headers_snapshot,
            "query_params_snapshot": result.query_params_snapshot,
            "body_snapshot": result.body_snapshot,
            "status": result.status,
            "status_code": result.status_code,
            "response_time_ms": result.response_time_ms,
            "failure_message": result.failure_message,
            "failure_details": self.clean_failure_details(result.failure_details),
            "assertion_results": result.assertion_results or [],
            "started_at": result.started_at,
            "finished_at": result.finished_at,
            "created_at": result.created_at,
        }

    def build_run_message(self, results: list[SmokeTestRunResult]) -> str:
        failed_count = sum(1 for result in results if result.status == "failed")

        if failed_count:
            return "Test run completed. Some smoke tests failed."

        return "Test run completed. All smoke tests passed."

    def build_full_url(self, base_url: str, path: str):
        clean_base_url = base_url.rstrip("/") + "/"
        clean_path = path.lstrip("/")

        return urljoin(clean_base_url, clean_path)

    def clean_failure_details(self, failure_details: Any):
        if not failure_details:
            return []

        if isinstance(failure_details, list):
            return [str(detail) for detail in failure_details if detail]

        return [str(failure_details)]

    def unique_sorted_ids(self, values):
        return sorted({int(value) for value in values})


smoke_test_run_service = SmokeTestRunService()
