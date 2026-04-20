import requests  # 确保导入了 requests 库

def build_test_prompt(path, method, request_fields, response_fields):
    request_text = "\n".join(f"{key}: {value}" for key, value in request_fields.items())
    response_text = "\n".join(f"{key}: {value}" for key, value in response_fields.items())

    prompt = f"""
Generate a pytest test case for this API:

{method} {path}

Request fields:
{request_text}

Response fields:
{response_text}

Requirements:
1. Use api_client fixture
2. Check status_code == 200
3. Assert response fields exist
"""
    return prompt

def generate_test(api_schema):
    prompt = build_test_prompt(
        path=api_schema["path"],
        method=api_schema["method"],
        request_fields=api_schema["request_fields"],
        response_fields=api_schema["response_fields"]
    )

    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "qwen2.5:7b",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status() # 检查 HTTP 请求是否成功
        data = response.json()
        return data['response']
    except Exception as e:
        return f"Error connecting to Ollama: {e}"

# --- 执行部分：确保这段代码在函数定义之外 ---
if __name__ == "__main__":
    api_schema = {
        "path": "/login",
        "method": "POST",
        "request_fields": {
            "username": "string",
            "password": "string"
        },
        "response_fields": {
            "token": "string"
        }
    }

    print("正在发送请求到 Ollama...")
    test_code = generate_test(api_schema)
    print("-" * 30)
    print(test_code)