import os
import subprocess
import time
import requests


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")


def _list_models_via_http():
    response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
    response.raise_for_status()
    data = response.json()
    models = data.get("models", [])
    return [item.get("name") for item in models if item.get("name")]


def _list_models_via_cli():
    result = subprocess.run(
        ["ollama", "list"],
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )

    model_names = []
    for line in result.stdout.splitlines()[1:]:
        parts = line.split()
        if parts:
            model_names.append(parts[0])
    return model_names


def check_ollama_status(model=DEFAULT_MODEL):
    try:
        model_names = _list_models_via_http()
        if model in model_names:
            return True, f"Ollama HTTP API 可用，已找到模型: {model}"
        if model_names:
            available = ", ".join(sorted(model_names))
            return False, f"Ollama HTTP API 可用，但未找到模型 {model}。当前可用模型: {available}"
        return False, "Ollama HTTP API 可用，但当前没有已拉取的模型。"
    except Exception as http_exc:
        try:
            model_names = _list_models_via_cli()
            if model in model_names:
                return True, f"Ollama CLI 可用，已找到模型: {model}。HTTP API 当前不可用，程序会自动回退到 CLI。"
            if model_names:
                available = ", ".join(sorted(model_names))
                return False, f"Ollama CLI 可用，但未找到模型 {model}。当前可用模型: {available}。HTTP API 错误: {http_exc}"
            return False, f"Ollama CLI 可用，但当前没有已拉取的模型。HTTP API 错误: {http_exc}"
        except Exception as cli_exc:
            return False, (
                f"Ollama 不可用。HTTP API 错误: {http_exc}。"
                f" CLI 错误: {cli_exc}"
            )


def _call_llm_via_http(prompt, model):
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("response")


def _call_llm_via_cli(prompt, model):
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
    )
    return result.stdout.strip()


def call_llm(prompt, model=DEFAULT_MODEL, max_retries=3):
    # 1. 先重试 HTTP
    for attempt in range(1, max_retries + 1):
        try:
            result = _call_llm_via_http(prompt, model)

            if not result or not result.strip():
                print(f"Ollama HTTP API 返回空结果，尝试次数 {attempt}/{max_retries}")
                if attempt < max_retries:
                    time.sleep(2)
                continue

            return result

        except Exception as http_exc:
            print(f"HTTP attempt {attempt} failed: {http_exc}")

            if attempt == max_retries:
                print("HTTP API 多次失败，准备回退到 CLI...")

            if attempt < max_retries:
                time.sleep(1)

    # 2. HTTP 全失败，再回退 CLI
    try:
        result = _call_llm_via_cli(prompt, model)

        if not result or not result.strip():
            print("Ollama CLI 返回空结果。")
            return None

        return result

    except Exception as cli_exc:
        print(f"Ollama CLI 调用失败: {cli_exc}")
        return None
