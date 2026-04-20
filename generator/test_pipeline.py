from generator.test_data_generator import generate_test_data
from generator.file_writer import write_test_file
from generator.code_validator import validate_test_code
from generator.test_template import build_test_template
from generator.assertion_builder import build_assertions
import json


def generate_and_save_test(api_schema):
    api_name = api_schema["path"].strip("/").replace("/", "_") or "root"

    test_cases = generate_test_data(api_schema)
    if test_cases is None:
        print("❌ 测试数据生成失败")
        return None

    test_cases_text = json.dumps(
        test_cases,
        indent=4,
        ensure_ascii=False
    )
    assertion_code = build_assertions(api_schema["response_fields"])

    final_code = build_test_template(
        api_schema,
        test_cases_text,
        assertion_code
    )

    if not validate_test_code(final_code):
        print(f"❌ 生成代码验证失败: {api_name}")
        return None

    file_path = write_test_file(api_name, final_code)
    print(f"✅ 测试文件生成成功: {file_path}")
    return file_path