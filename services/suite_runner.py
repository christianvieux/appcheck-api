from datetime import datetime
from time import perf_counter
from urllib.parse import urljoin
from typing import Any, cast

from fastapi import HTTPException
from pydantic import AnyUrl

from database.models import Project, SmokeTest, Target, TestResult, TestRun, TestSuite
from models.smoke_tests import SingleSmokeTestRequest
from services.smoke_tests_runner import run_multiple_smoke_tests


class SuiteRunner:
    async def run_smoke_suite(self, db_connection, suite_id: int, owner_id: str):
        started_at = datetime.now()
        started_perf_counter = perf_counter()

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

        smoke_tests = (
            db_connection
            .query(SmokeTest)
            .filter(SmokeTest.suite_id == suite_id)
            .all()
        )

        if not smoke_tests:
            raise HTTPException(
                status_code=400,
                detail="Test suite has no smoke tests.",
            )

        executable_tests = []
        executable_smoke_tests = []

        for smoke_test in smoke_tests:
            target = (
                db_connection
                .query(Target)
                .filter(Target.id == smoke_test.target_id)
                .first()
            )

            if not target:
                raise HTTPException(
                    status_code=404,
                    detail=f"Target not found for smoke test '{smoke_test.name}'.",
                )

            full_url = self.build_full_url(
                target.url,
                smoke_test.path,
            )

            executable_test = SingleSmokeTestRequest(
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

            executable_tests.append(executable_test)
            executable_smoke_tests.append(smoke_test)

        test_run_results = await run_multiple_smoke_tests(executable_tests)

        finished_at = datetime.now()
        duration_ms = round((perf_counter() - started_perf_counter) * 1000)

        # `run_multiple_smoke_tests` returns a list of `SingleSmokeTestResult` models
        # Convert any pydantic model instances to dicts so we can use dict methods
        results: list = []
        for item in test_run_results:
            if hasattr(item, "model_dump"):
                results.append(item.model_dump())
            elif hasattr(item, "dict"):
                results.append(item.dict())
            else:
                results.append(item)

        passed_count = 0
        failed_count = 0

        for result in results:
            if result.get("status") == "passed":
                passed_count += 1

            if result.get("status") == "failed":
                failed_count += 1

        test_run = TestRun(
            suite_id=suite_id,
            status="failed" if failed_count else "passed",
            total_tests=len(results),
            passed_count=passed_count,
            failed_count=failed_count,
            duration_ms=duration_ms,
            started_at=started_at,
            finished_at=finished_at,
        )

        db_connection.add(test_run)
        db_connection.flush()

        saved_results = []

        for smoke_test, result in zip(executable_smoke_tests, results):
            failure_details = self.clean_failure_details(
                result.get("failure_details"),
            )

            response = result.get("response") or {}
            status_code = response.get("status_code")

            test_result = TestResult(
                test_run_id=test_run.id,
                saved_test_id=smoke_test.id,
                target_id=smoke_test.target_id,
                status=result.get("status", "failed"),
                status_code=status_code,
                expected_status_code=smoke_test.expected_status,
                response_time_ms=result.get("response_time_ms"),
                failure_message=failure_details[0] if failure_details else None,
                failure_details=failure_details,
                assertion_results=[],
            )

            db_connection.add(test_result)
            saved_results.append((test_result, smoke_test))

        db_connection.commit()
        db_connection.refresh(test_run)

        for test_result, _smoke_test in saved_results:
            db_connection.refresh(test_result)

        return {
            "run_id": test_run.id,
            "suite_id": suite_id,
            "suite_name": suite.name,
            "status": test_run.status,
            "passed_count": passed_count,
            "failed_count": failed_count,
            "total_tests": len(results),
            "duration_ms": duration_ms,
            "started_at": test_run.started_at,
            "finished_at": test_run.finished_at,
            "created_at": test_run.created_at,
            "results": [
                self.serialize_test_result(test_result, smoke_test)
                for test_result, smoke_test in saved_results
            ],
        }

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

    def serialize_test_run(self, test_run: TestRun):
        return {
            "run_id": test_run.id,
            "suite_id": test_run.suite_id,
            "suite_name": test_run.suite.name if test_run.suite else "",
            "status": test_run.status,
            "total_tests": test_run.total_tests,
            "passed_count": test_run.passed_count,
            "failed_count": test_run.failed_count,
            "duration_ms": test_run.duration_ms,
            "started_at": test_run.started_at,
            "finished_at": test_run.finished_at,
            "created_at": test_run.created_at,
        }

    def serialize_test_result(self, test_result: TestResult, smoke_test: SmokeTest | None = None):
        resolved_smoke_test = smoke_test or test_result.smoke_test

        return {
            "id": test_result.id,
            "test_run_id": test_result.test_run_id,
            "saved_test_id": test_result.saved_test_id,
            "target_id": test_result.target_id,
            "name": resolved_smoke_test.name if resolved_smoke_test else None,
            "status": test_result.status,
            "status_code": test_result.status_code,
            "expected_status_code": test_result.expected_status_code,
            "response_time_ms": test_result.response_time_ms,
            "failure_message": test_result.failure_message,
            "failure_details": self.clean_failure_details(test_result.failure_details),
            "assertion_results": test_result.assertion_results,
            "created_at": test_result.created_at,
        }


suite_runner = SuiteRunner()
