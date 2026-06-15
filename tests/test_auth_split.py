import unittest
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError

from main import app
from services.auth import get_current_user


class AuthDependencyTests(unittest.TestCase):
    def test_missing_token_is_unauthorized(self):
        with self.assertRaises(HTTPException) as exc:
            get_current_user(None)

        self.assertEqual(exc.exception.status_code, 401)

    def test_malformed_token_is_unauthorized(self):
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="bad-token",
        )

        with patch("services.auth.get_jwks_client") as mock_jwks_client:
            mock_jwks_client.return_value.get_signing_key_from_jwt.side_effect = (
                InvalidTokenError("bad token")
            )

            with self.assertRaises(HTTPException) as exc:
                get_current_user(credentials)

        self.assertEqual(exc.exception.status_code, 401)

    def test_valid_token_returns_current_user(self):
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="valid-token",
        )

        with patch("services.auth.get_jwks_client") as mock_jwks_client:
            with patch("services.auth.jwt.decode") as mock_decode:
                with patch.dict(
                    "os.environ",
                    {"SUPABASE_URL": "https://example.supabase.co"},
                ):
                    mock_jwks_client.return_value.get_signing_key_from_jwt.return_value.key = (
                        "public-key"
                    )
                    mock_decode.return_value = {
                        "sub": "user-123",
                        "email": "user@example.com",
                    }

                    current_user = get_current_user(credentials)

        self.assertEqual(current_user.id, "user-123")
        self.assertEqual(current_user.email, "user@example.com")


class AuthRouteSplitTests(unittest.TestCase):
    def setUp(self):
        app.dependency_overrides.clear()

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_saved_routes_have_auth_dependency(self):
        protected_paths = {
            "/project",
            "/projects",
            "/project/{project_id}",
            "/project/{project_id}/targets",
            "/target",
            "/target/{target_id}",
            "/target/{target_id}/test-suites",
            "/test-suite",
            "/test-suite/{test_suite_id}",
            "/smoke-test",
            "/smoke-test/{smoke_test_id}",
            "/test-suite/{suite_id}/smoke-tests",
            "/test-suite/{suite_id}/runs",
            "/runs/{run_group_id}",
            "/runs/{run_group_id}/results",
            "/user/run-smoke-tests",
            "/user/run-single-smoke-test",
        }

        routes_by_path = {
            route.path: route
            for route in app.routes
            if route.path in protected_paths
        }

        self.assertEqual(set(routes_by_path), protected_paths)

        for route in routes_by_path.values():
            dependency_calls = [
                dependency.call
                for dependency in route.dependant.dependencies
            ]

            self.assertIn(get_current_user, dependency_calls)

    def test_public_runner_routes_have_no_auth_dependency(self):
        public_paths = {
            "/run-single-smoke-test",
            "/run-smoke-tests",
        }

        routes_by_path = {
            route.path: route
            for route in app.routes
            if route.path in public_paths
        }

        self.assertEqual(set(routes_by_path), public_paths)

        for route in routes_by_path.values():
            dependency_calls = [
                dependency.call
                for dependency in route.dependant.dependencies
            ]

            self.assertNotIn(get_current_user, dependency_calls)


if __name__ == "__main__":
    unittest.main()
