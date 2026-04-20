from generator.assertion_builder import build_assertions
def inject_assertions(cleaned_code, assertion_code):

    marker = "response_data = response.json()"

    if marker not in cleaned_code:
        print("❌ 未找到 response_data 位置")
        return cleaned_code

    # 你来补这里 ⭐⭐⭐
    new_code = cleaned_code.replace(
        marker,
        marker + "\n" + assertion_code
    )

    return new_code