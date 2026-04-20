def validate_test_code(code):
    if not code or not code.strip():
        print("❌ 代码为空")
        return False
    # 1. 判断是否包含 test 函数
    if "def test_" not in code:
        print("❌ 代码中没有找到 test 函数定义")
        return False

    # 2. 判断是否包含 assert
    # 你补
    if "assert" not in code:
        print("❌ 代码中没有找到 assert 语句")
        return False

    # 3. 判断是否使用 api_client
    # 你补
    if "api_client" not in code:
        print("❌ 代码中没有找到 api_client 的使用")
        return False
    # 4. 如果全部通过
    return True