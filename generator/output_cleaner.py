def clean_llm_output(text):
    # 1. 去掉 markdown fence
    cleaned_text = text.replace("```python", "")
    cleaned_text = cleaned_text.replace("```", "")

    # 2. 找到 test 函数起始位置
    start_index = cleaned_text.find("def test_")

    # 你补这里
    # 如果找到 test 函数，就截断前面的内容
    if start_index != -1:
        cleaned_text = cleaned_text[start_index:]

    # 3. 去掉首尾空白
    cleaned_text = cleaned_text.strip()

    return cleaned_text