# generator/test_generator.py

from generator.prompt_builder import build_test_prompt
from generator.llm_client import call_llm


def generate_test_code(api_schema):
    """
    只负责：
    API schema → LLM → 原始测试代码
    """

    prompt = build_test_prompt(
        path=api_schema["path"],
        method=api_schema["method"],
        request_fields=api_schema["request_fields"],
        response_fields=api_schema["response_fields"]
    )

    if not prompt:
        print("❌ 构建 test prompt 失败")
        return None

    raw_output = call_llm(prompt)

    if not raw_output:
        print("❌ LLM 未返回测试代码")
        return None

    return raw_output