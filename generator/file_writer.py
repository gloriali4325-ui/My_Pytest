from pathlib import Path

def write_test_file(api_name, code, output_dir="tests/generated"):
    # 1. 创建目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 2. 清洗 api_name
    safe_name = api_name.replace("/", "_")

    # 3. 生成文件路径
    file_path = output_path / f"test_{safe_name}.py"

    # 4. 写入代码
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    # 5. 返回路径
    return str(file_path)
