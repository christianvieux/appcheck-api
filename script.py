import requests

BASE_URL = "http://localhost:8000"

def post(path, payload):
    response = requests.post(f"{BASE_URL}{path}", json=payload)

    if not response.ok:
        print(f"FAILED POST {path}")
        print(response.status_code)
        print(response.text)
        raise SystemExit(1)

    return response.json()


# project = post("/project", {
#     "name": "JSONPlaceholder Project",
#     "description": "Seeded project for testing smoke test storage"
# })

# project_id = project["id"]

# target = post("/target", {
#     "project_id": project_id,
#     "name": "JSONPlaceholder API",
#     "url": "https://jsonplaceholder.typicode.com",
#     "target_type": "api"
# })

# target_id = target["id"]

suite = post("/test-suite", {
    "target_id": 1,
    "name": "Basic Smoke Test Suite_3",
    "description": "Seeded suite with fake public API smoke tests"
})

suite_id = suite["id"]

smoke_tests = [
    {
        "name": "Get user 1",
        "description": "Checks that user 1 loads correctly",
        "method": "GET",
        "path": "/users/1",
        "expected_status": 200,
        "assertions": [
            {
                "type": "json_body",
                "path": "id",
                "operator": "equals",
                "value": 1,
                "conditions": []
            },
            {
                "type": "json_body",
                "path": "email",
                "operator": "contains",
                "value": "@",
                "conditions": []
            }
        ]
    },
    {
        "name": "Get all users",
        "description": "Checks that users list returns an array",
        "method": "GET",
        "path": "/users",
        "expected_status": 200,
        "assertions": [
            {
                "type": "json_body",
                "path": None,
                "operator": "is_array",
                "value": None,
                "conditions": []
            }
        ]
    },
    {
        "name": "Get post 1",
        "description": "Checks that post 1 loads correctly",
        "method": "GET",
        "path": "/posts/1",
        "expected_status": 200,
        "assertions": [
            {
                "type": "json_body",
                "path": "id",
                "operator": "equals",
                "value": 1,
                "conditions": []
            },
            {
                "type": "json_body",
                "path": "title",
                "operator": "is_string",
                "value": None,
                "conditions": []
            }
        ]
    },
    {
        "name": "Get posts by user 1",
        "description": "Checks query params work",
        "method": "GET",
        "path": "/posts",
        "query_params": {
            "userId": "1"
        },
        "expected_status": 200,
        "assertions": [
            {
                "type": "json_body",
                "path": None,
                "operator": "is_array",
                "value": None,
                "conditions": []
            },
            {
                "type": "json_body",
                "path": "0.userId",
                "operator": "equals",
                "value": 1,
                "conditions": []
            }
        ]
    },
    {
        "name": "Create fake post",
        "description": "Checks POST body handling",
        "method": "POST",
        "path": "/posts",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": {
            "title": "Smoke Test Post",
            "body": "Created by seed script",
            "userId": 1
        },
        "expected_status": 201,
        "assertions": [
            {
                "type": "json_body",
                "path": "id",
                "operator": "exists",
                "value": None,
                "conditions": []
            },
            {
                "type": "json_body",
                "path": "title",
                "operator": "equals",
                "value": "Smoke Test Post",
                "conditions": []
            }
        ]
    }
]

for smoke_test in smoke_tests:
    payload = {
        "suite_id": 1,
        "target_id": 4,
        "headers": None,
        "query_params": None,
        "body": None,
        "max_response_time_ms": 30000,
        **smoke_test
    }

    created = post("/smoke-test", payload)
    print(f"Created smoke test: {created.get('name', smoke_test['name'])}")

print("\nSeed complete, because apparently we survived.")
# print(f"Project ID: {project_id}")
# print(f"Target ID: {target_id}")
print(f"Suite ID: {suite_id}")
print(f"Check saved tests at: {BASE_URL}/test-suite/{suite_id}/smoke-tests")