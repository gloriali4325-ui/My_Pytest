def build_test_template(api_schema, test_cases_text, extra_assertion_code):
    path = api_schema["path"]
    method = api_schema["method"].lower()

    safe_name = path.strip("/").replace("/", "_").replace("-", "_")
    if not safe_name:
        safe_name = "root"

    test_func_name = f"test_{safe_name}"

    indented_extra_assertion_code = "\n".join(
        "    " + line for line in extra_assertion_code.splitlines()
    )

    final_code = f"""import pytest

test_cases = {test_cases_text}

@pytest.mark.parametrize("case", test_cases)
def {test_func_name}(api_client, case):
    response = api_client.{method}("{path}", json=case["data"])
    assert response.status_code == case["expected_status"]

    response_data = response.json()

    for field in case["expected_fields"]:
        assert field in response_data

{indented_extra_assertion_code}
"""
    return final_code