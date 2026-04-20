import json

def load_api_schemas(file_path):
    # 1. 打开文件
    # 你补
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. 读取 JSON
    # 你补
    if not isinstance(data, list):
        raise ValueError("API schema JSON 文件必须是一个列表，每个元素代表一个 API 的定义。")
    elif len(data) == 0:
        raise ValueError("API schema JSON 文件不能为空。请至少定义一个 API。")
    else:
        print(f"成功加载 {len(data)} 个 API 定义。")

    # 3. 返回数据
    return data