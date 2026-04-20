from generator.llm_client import check_ollama_status
from generator.test_pipeline import generate_and_save_test
from generator.schema_loader import load_api_schemas

def main():

    api_schemas = load_api_schemas("generator/apis.json")
    ok, message = check_ollama_status()
    print(message)
    if not ok:
        print("\n未开始生成测试文件。请先修复上面的 Ollama 连接或模型问题。")
        return

    success_count = 0
    fail_count = 0

    for api_schema in api_schemas:
        file_path = generate_and_save_test(api_schema)

        # 1. 判断成功还是失败
        # 你来补
        if file_path:
            print(f"✅ 成功生成测试文件: {file_path}")
            success_count += 1
        else:
            print(f"❌ 生成测试文件失败 for API: {api_schema['method']} {api_schema['path']}")
            fail_count += 1
            total_count = len(api_schemas)
    # 2. 最后打印汇总
    # 你来补
    print(f"\n测试文件生成汇总:")
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失败: {fail_count}")

if __name__ == "__main__":
    main()
