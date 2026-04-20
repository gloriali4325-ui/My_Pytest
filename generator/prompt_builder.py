def build_test_prompt(path, method, request_fields, response_fields):
    request_text = "\n".join(f"{key}: {value}" for key, value in request_fields.items())
    response_text = "\n".join(f"{key}: {value}" for key, value in response_fields.items())

    prompt = f"""
Generate a pytest test case for this API:

{method} {path}

Request fields:
{request_text}

Response fields:
{response_text}

Requirements:

1. Use api_client fixture
2. Send request using api_client.{method.lower()}
3. Check status_code == 200
4. Assert response fields exist
5. The test function name must follow:
   test_{path.strip("/").replace("/", "_")}_success

Output format example:

def test_example_success(api_client):
    response = api_client.post("/example", json={{}})

    assert response.status_code == 200

    data = response.json()

    assert "field" in data

Important:

Return only Python code.
Do not include markdown.
Do not include explanation.
Only output pure Python code.
"""
    return prompt


def build_data_prompt(path, method, request_fields, response_fields):
    request_text = "\n".join(f"{key}: {value}" for key, value in request_fields.items())
    response_text = "\n".join(f"{key}: {value}" for key, value in response_fields.items())

    prompt = f"""
Generate structured pytest cases for this API:

{method} {path}

Request fields:
{request_text}

Success response fields:
{response_text}

Requirements:
1. Return a JSON list only
2. Generate at least 5 cases
3. Include both valid and invalid inputs
4. Each item must use this exact schema:
   {{
     "name": "short_case_name",
     "data": {{"field": "value"}},
     "expected_status": 200,
     "expected_fields": ["field_name"]
   }}
5. For valid cases, expected_status should be 200 and expected_fields should include the success response fields
6. For invalid cases, expected_status should be 400 and expected_fields should include "error"
7. Do not include markdown
8. Do not include explanation
9.Assert response field types based on schema
"""

    return prompt
