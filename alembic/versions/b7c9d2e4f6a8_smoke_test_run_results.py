"""replace test runs with smoke test run results

Revision ID: b7c9d2e4f6a8
Revises: c21ac45fa906
Create Date: 2026-06-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7c9d2e4f6a8"
down_revision: Union[str, Sequence[str], None] = "c21ac45fa906"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "smoke_test_run_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("run_group_id", sa.String(), nullable=False),
        sa.Column("owner_id", sa.String(), nullable=False),
        sa.Column("smoke_test_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("suite_id", sa.Integer(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("run_source", sa.String(), nullable=False),
        sa.Column("triggered_by", sa.String(), nullable=False),
        sa.Column("name_snapshot", sa.String(), nullable=False),
        sa.Column("method_snapshot", sa.String(), nullable=False),
        sa.Column("url_snapshot", sa.String(), nullable=False),
        sa.Column("path_snapshot", sa.String(), nullable=False),
        sa.Column("expected_status_snapshot", sa.Integer(), nullable=False),
        sa.Column("max_response_time_ms_snapshot", sa.Integer(), nullable=False),
        sa.Column("assertions_snapshot", sa.JSON(), nullable=True),
        sa.Column("headers_snapshot", sa.JSON(), nullable=True),
        sa.Column("query_params_snapshot", sa.JSON(), nullable=True),
        sa.Column("body_snapshot", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("failure_message", sa.String(), nullable=True),
        sa.Column("failure_details", sa.JSON(), nullable=True),
        sa.Column("assertion_results", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["smoke_test_id"], ["smoke_tests.id"]),
        sa.ForeignKeyConstraint(["suite_id"], ["test_suites.id"]),
        sa.ForeignKeyConstraint(["target_id"], ["targets.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_smoke_test_run_results_owner_id", "smoke_test_run_results", ["owner_id"])
    op.create_index("ix_smoke_test_run_results_project_id", "smoke_test_run_results", ["project_id"])
    op.create_index("ix_smoke_test_run_results_run_group_id", "smoke_test_run_results", ["run_group_id"])
    op.create_index("ix_smoke_test_run_results_run_source", "smoke_test_run_results", ["run_source"])
    op.create_index("ix_smoke_test_run_results_smoke_test_id", "smoke_test_run_results", ["smoke_test_id"])
    op.create_index("ix_smoke_test_run_results_suite_id", "smoke_test_run_results", ["suite_id"])
    op.create_index("ix_smoke_test_run_results_target_id", "smoke_test_run_results", ["target_id"])
    op.create_index("ix_smoke_test_run_results_triggered_by", "smoke_test_run_results", ["triggered_by"])

    # Legacy rows can only be made tenant-safe when their owning project has owner_id.
    op.execute(
        """
        INSERT INTO smoke_test_run_results (
            run_group_id,
            owner_id,
            smoke_test_id,
            project_id,
            suite_id,
            target_id,
            run_source,
            triggered_by,
            name_snapshot,
            method_snapshot,
            url_snapshot,
            path_snapshot,
            expected_status_snapshot,
            max_response_time_ms_snapshot,
            assertions_snapshot,
            headers_snapshot,
            query_params_snapshot,
            body_snapshot,
            status,
            status_code,
            response_time_ms,
            failure_message,
            failure_details,
            assertion_results,
            started_at,
            finished_at,
            created_at
        )
        SELECT
            'legacy-' || test_runs.id,
            projects.owner_id,
            test_results.saved_test_id,
            targets.project_id,
            test_runs.suite_id,
            test_results.target_id,
            'suite',
            'manual',
            smoke_tests.name,
            smoke_tests.method,
            rtrim(targets.url, '/') || '/' || ltrim(smoke_tests.path, '/'),
            smoke_tests.path,
            smoke_tests.expected_status,
            smoke_tests.max_response_time_ms,
            smoke_tests.assertions,
            smoke_tests.headers,
            smoke_tests.query_params,
            smoke_tests.body,
            test_results.status,
            test_results.status_code,
            test_results.response_time_ms,
            test_results.failure_message,
            test_results.failure_details,
            test_results.assertion_results,
            test_runs.started_at,
            test_runs.finished_at,
            test_results.created_at
        FROM test_results
        JOIN test_runs ON test_results.test_run_id = test_runs.id
        JOIN smoke_tests ON test_results.saved_test_id = smoke_tests.id
        JOIN targets ON test_results.target_id = targets.id
        JOIN projects ON targets.project_id = projects.id
        WHERE projects.owner_id IS NOT NULL
        """
    )

    op.drop_table("test_results")
    op.drop_table("test_runs")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        "test_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("suite_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("total_tests", sa.Integer(), nullable=False),
        sa.Column("passed_count", sa.Integer(), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["suite_id"], ["test_suites.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "test_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("test_run_id", sa.Integer(), nullable=False),
        sa.Column("saved_test_id", sa.Integer(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("expected_status_code", sa.Integer(), nullable=False),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("failure_message", sa.String(), nullable=True),
        sa.Column("failure_details", sa.JSON(), nullable=True),
        sa.Column("assertion_results", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["saved_test_id"], ["smoke_tests.id"]),
        sa.ForeignKeyConstraint(["target_id"], ["targets.id"]),
        sa.ForeignKeyConstraint(["test_run_id"], ["test_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.drop_index("ix_smoke_test_run_results_triggered_by", table_name="smoke_test_run_results")
    op.drop_index("ix_smoke_test_run_results_target_id", table_name="smoke_test_run_results")
    op.drop_index("ix_smoke_test_run_results_suite_id", table_name="smoke_test_run_results")
    op.drop_index("ix_smoke_test_run_results_smoke_test_id", table_name="smoke_test_run_results")
    op.drop_index("ix_smoke_test_run_results_run_source", table_name="smoke_test_run_results")
    op.drop_index("ix_smoke_test_run_results_run_group_id", table_name="smoke_test_run_results")
    op.drop_index("ix_smoke_test_run_results_project_id", table_name="smoke_test_run_results")
    op.drop_index("ix_smoke_test_run_results_owner_id", table_name="smoke_test_run_results")
    op.drop_table("smoke_test_run_results")
