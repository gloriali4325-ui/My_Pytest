# generator/test_data_generator.py

from generator.llm_client import call_llm
from generator.prompt_builder import build_data_prompt
from generator.output_cleaner import clean_llm_output

import json


def _default_value_for_field(field_name, field_type):
    normalized_type = str(field_type).lower()

    if "int" in normalized_type:
        return 0

    if "bool" in normalized_type:
        return False

    return ""

def _is_success_case(api_schema, case_input):

    rules = api_schema.get("success_rules")

    if not rules:
        return all(
            value not in ("", None)
            for value in case_input.values()
        )

    required_fields = rules.get("required_fields", [])
    for field in required_fields:
        value = case_input.get(field)
        if value in ("", None):
            return False

    min_length_rules = rules.get("min_length", {})
    for field, min_len in min_length_rules.items():
        value = str(case_input.get(field, ""))
        if len(value) < min_len:
            return False

    contains_rules = rules.get("contains", {})
    for field, expected_substring in contains_rules.items():
        value = str(case_input.get(field, ""))
        if expected_substring not in value:
            return False

    return True

def _expected_fields_for_case(api_schema, expected_status):
    if expected_status == 200:
        return list(api_schema["response_fields"].keys())
    return ["error"]


def _normalize_case(api_schema, case, index):
    if not isinstance(case, dict):
        print(f"❌ 第 {index + 1} 条测试数据不是对象")
        return None

    case_input = case.get("data")
    expected_status = case.get("expected_status")
    expected_fields = case.get("expected_fields")
    name = case.get("name") or f"case_{index + 1}"

    if not isinstance(case_input, dict):
        print(f"❌ 第 {index + 1} 条测试数据缺少 input 对象")
        return None

    normalized_input = {}
    request_fields = api_schema["request_fields"]

    for field_name, field_type in request_fields.items():
        if field_name in case_input:
            normalized_input[field_name] = case_input[field_name]
        else:
            fallback_value = _default_value_for_field(field_name, field_type)
            normalized_input[field_name] = fallback_value
            print(
                f"⚠️ 第 {index + 1} 条测试数据缺少字段 {field_name}，"
                f"已自动补默认值: {fallback_value!r}"
            )

    extra_fields = sorted(set(case_input.keys()) - set(request_fields.keys()))
    if extra_fields:
        print(f"⚠️ 第 {index + 1} 条测试数据包含额外字段 {extra_fields}，已忽略")

    inferred_success = _is_success_case(api_schema, normalized_input)
    inferred_status = 200 if inferred_success else 400

    if not isinstance(expected_status, int):
        expected_status = inferred_status
        print(f"⚠️ 第 {index + 1} 条测试数据缺少 expected_status，已自动推断为 {expected_status}")
    elif expected_status != inferred_status:
        print(
            f"⚠️ 第 {index + 1} 条测试数据的 expected_status={expected_status} "
            f"与输入不一致，已修正为 {inferred_status}"
        )
        expected_status = inferred_status

    if not isinstance(expected_fields, list) or not all(isinstance(item, str) for item in expected_fields):
        expected_fields = _expected_fields_for_case(api_schema, expected_status)
        print(f"⚠️ 第 {index + 1} 条测试数据缺少 expected_fields，已自动推断为 {expected_fields}")
    else:
        expected_fields = _expected_fields_for_case(api_schema, expected_status)

    return {
        "name": str(name),
        "data": normalized_input,
        "expected_status": expected_status,
        "expected_fields": expected_fields,
    }


def generate_test_data(api_schema):
    """
    生成测试数据：
    request_fields → LLM → JSON list
    """

    request_fields = api_schema["request_fields"]
    response_fields = api_schema["response_fields"]

    # 1 构建 prompt
    prompt = build_data_prompt(
        path=api_schema["path"],
        method=api_schema["method"],
        request_fields=request_fields,
        response_fields=response_fields,
    )

    if not prompt:
        print("❌ 构建 data prompt 失败")
        return None

    # 2 调用 LLM
    raw_output = call_llm(prompt)

    if not raw_output:
        print("❌ LLM 未返回测试数据")
        return None

    # 3 清洗输出
    cleaned_output = clean_llm_output(raw_output)

    if not cleaned_output:
        print("❌ 清洗后的测试数据为空")
        return None

    # 4 JSON 解析
    try:
        test_data_list = json.loads(cleaned_output)

    except json.JSONDecodeError:
        print("❌ 解析生成的测试数据失败")
        return None

    # 5 类型检查
    if not isinstance(test_data_list, list):
        print("❌ 生成的测试数据格式不正确，应该是一个列表")
        return None

    normalized_cases = []
    for index, case in enumerate(test_data_list):
        normalized_case = _normalize_case(api_schema, case, index)
        if normalized_case is None:
            return None
        normalized_cases.append(normalized_case)

    print(f"✅ 生成 {len(normalized_cases)} 条测试数据")

    return normalized_cases
