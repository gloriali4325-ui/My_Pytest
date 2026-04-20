# AI Test Generator

一个基于 Python + Ollama 的 API 测试用例生成器。

这个项目的目标是把一份简化的 API schema 配置转换成可执行的 `pytest` 测试文件。当前版本的重点不是直接让大模型输出完整测试代码，而是把生成过程拆成几个更稳定的步骤：

1. 读取 API schema
2. 让 LLM 生成结构化测试数据
3. 在本地校验并规范化测试数据
4. 根据模板拼装最终测试代码
5. 将测试文件写入 `tests/generated/`

这种设计的好处是，LLM 只负责生成“测试场景数据”，而不是一次性生成整份测试代码。这样更容易做本地校验，也更容易定位问题。

## 项目目标

- 输入：一组 API 定义
- 输出：对应的 `pytest` 测试文件
- 特点：
  - 使用 Ollama 本地模型
  - 支持根据接口 schema 自动生成正向和反向 case
  - 通过模板统一测试代码风格
  - 使用本地规则修正 LLM 生成结果，减少不稳定输出

## 当前实现思路

项目当前采用的是“半自动生成”架构：

- LLM 负责生成 JSON 格式的测试 case
- Python 代码负责：
  - 清洗输出
  - 解析 JSON
  - 补默认值
  - 修正 `expected_status`
  - 推导 `expected_fields`
  - 构建断言代码
  - 生成最终 pytest 文件

这意味着项目的核心能力并不完全依赖模型“直接写对代码”，而是更多依赖本地的生成管道和规则约束。

## 目录结构

```text
.
├── main.py
├── APIClient.py
├── conftest.py
├── pytest.ini
├── generator/
│   ├── apis.json
│   ├── assertion_builder.py
│   ├── assertion_injector.py
│   ├── code_validator.py
│   ├── file_writer.py
│   ├── llm_client.py
│   ├── output_cleaner.py
│   ├── prompt_builder.py
│   ├── schema_loader.py
│   ├── test_data_generator.py
│   ├── test_generator.py
│   ├── test_pipeline.py
│   └── test_template.py
└── tests/
    └── generated/
        ├── test_login.py
        └── test_register.py
```

## 核心流程

### 1. 程序入口

入口文件是 [`main.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/main.py)。

它做了三件事：

1. 从 `generator/apis.json` 读取 API 定义
2. 检查 Ollama 和目标模型是否可用
3. 遍历每个 API schema，调用生成管道并统计成功/失败数量

主入口并不直接处理生成细节，真正的生成工作由 `generator/test_pipeline.py` 完成。

### 2. 读取 API schema

[`generator/schema_loader.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/schema_loader.py) 负责读取 schema 文件。

当前 schema 文件是 [`generator/apis.json`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/apis.json)，每个接口定义包含：

- `method`
- `path`
- `request_fields`
- `response_fields`
- `success_rules`

其中 `success_rules` 很关键，它决定了本地代码如何判断一个 case 是成功还是失败，而不完全依赖 LLM 自己给出的 `expected_status`。

例如：

- `/login` 要求 `username` 和 `password` 必填
- `username` 最短长度为 3
- `password` 最短长度为 6
- `/register` 还额外要求 `email` 包含 `@`

### 3. 构造 Prompt

[`generator/prompt_builder.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/prompt_builder.py) 提供了两类 prompt：

- `build_test_prompt()`
- `build_data_prompt()`

当前主链路实际使用的是 `build_data_prompt()`。

它要求 LLM 返回一个 JSON 列表，列表中的每个对象必须是这样的结构：

```json
{
  "name": "short_case_name",
  "data": {"field": "value"},
  "expected_status": 200,
  "expected_fields": ["field_name"]
}
```

这个设计是整个项目稳定性的关键，因为它把模型输出限制成“结构化数据”，而不是自由生成 Python 代码。

### 4. 调用 LLM

[`generator/llm_client.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/llm_client.py) 负责和 Ollama 通信。

实现特点：

- 默认优先调用 Ollama HTTP API
- 如果 HTTP API 连续失败，会自动回退到 Ollama CLI
- 默认模型来自环境变量 `OLLAMA_MODEL`
- 默认地址来自环境变量 `OLLAMA_BASE_URL`

默认值：

- `OLLAMA_BASE_URL=http://127.0.0.1:11434`
- `OLLAMA_MODEL=qwen2.5:7b`

在真正生成前，`check_ollama_status()` 会先检查模型是否存在，避免生成流程跑到一半才失败。

### 5. 生成并规范化测试数据

[`generator/test_data_generator.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/test_data_generator.py) 是当前项目最核心的模块之一。

它的职责不是简单“拿到模型输出就直接用”，而是做了一层本地修正：

- 调用 `build_data_prompt()`
- 调用 `call_llm()`
- 使用 `clean_llm_output()` 清洗输出
- 把输出解析成 Python list
- 遍历每个 case 做规范化

规范化逻辑包括：

- 校验 case 是否是字典
- 校验 `data` 是否存在且是对象
- 自动补齐缺失请求字段的默认值
- 忽略 schema 中未定义的额外字段
- 根据 `success_rules` 推导这个 case 应该成功还是失败
- 如果 `expected_status` 不合理，则自动修正
- 根据状态码推导 `expected_fields`

项目当前不是完全相信 LLM，而是采用“LLM 生成候选数据 + 本地规则纠偏”的模式。

### 6. 构造断言

[`generator/assertion_builder.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/assertion_builder.py) 根据 `response_fields` 生成附加断言代码。

当前逻辑会为成功字段生成类型和值检查，例如：

- `string` 字段要求是 `str` 且非空
- `int` 字段要求是 `int` 且 `>= 0`

同时它会把断言包在这样的条件里：

```python
if "token" in case["expected_fields"]:
    ...
```

这样同一份模板可以同时覆盖成功 case 和失败 case，不会再把成功响应字段强行断言到失败响应上。

### 7. 使用模板拼装 pytest 文件

[`generator/test_template.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/test_template.py) 负责把：

- API 信息
- 测试数据 JSON
- 断言代码

拼成最终的 pytest 文件。

模板生成的测试基本结构如下：

```python
import pytest

test_cases = [...]

@pytest.mark.parametrize("case", test_cases)
def test_xxx(api_client, case):
    response = api_client.post("/path", json=case["data"])
    assert response.status_code == case["expected_status"]

    response_data = response.json()

    for field in case["expected_fields"]:
        assert field in response_data

    # 额外类型和值断言
```

### 8. 最终校验和写文件

[`generator/code_validator.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/code_validator.py) 会做非常基础的静态检查，确认生成代码中至少包含：

- `def test_`
- `assert`
- `api_client`

如果通过，就由 [`generator/file_writer.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/file_writer.py) 把文件写到 `tests/generated/`。

## 当前主链路中各模块的职责

### 正在使用的模块

- [`main.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/main.py)
  - 程序入口
- [`generator/schema_loader.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/schema_loader.py)
  - 读取 API schema
- [`generator/llm_client.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/llm_client.py)
  - 调用 Ollama
- [`generator/prompt_builder.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/prompt_builder.py)
  - 构造数据生成 prompt
- [`generator/test_data_generator.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/test_data_generator.py)
  - 生成并规范化测试数据
- [`generator/assertion_builder.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/assertion_builder.py)
  - 生成字段断言
- [`generator/test_template.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/test_template.py)
  - 组装最终测试代码
- [`generator/code_validator.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/code_validator.py)
  - 最终代码基本校验
- [`generator/file_writer.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/file_writer.py)
  - 写入测试文件

### 当前未进入主链路或属于早期实验的模块

- [`generator/test_generator.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/test_generator.py)
  - 让 LLM 直接生成原始测试代码
  - 当前主流程没有使用
- [`generator/assertion_injector.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/assertion_injector.py)
  - 用字符串替换的方式把断言插入已有代码
  - 当前主流程没有使用

这两个文件说明你前期探索过另一条路线：先让 LLM 生成测试代码，再注入断言。现在的主线已经演进成“先生成结构化数据，再模板化组装代码”，这个方向更稳。

## 生成结果示例

当前生成结果存放在：

- [`tests/generated/test_login.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/tests/generated/test_login.py)
- [`tests/generated/test_register.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/tests/generated/test_register.py)

这些文件展示了项目当前的输出形式：

- 使用 `pytest.mark.parametrize`
- 每个 case 包含 `name`、`data`、`expected_status`、`expected_fields`
- 统一通过 `api_client` 发请求
- 先校验状态码，再校验响应字段和字段类型

## 测试环境

项目中还提供了一个用于本地验证生成结果的假客户端 fixture：

[`conftest.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/conftest.py)

这里通过 `MagicMock` 模拟了 `/login`、`/register`、`/users` 三个接口的行为，因此你不需要真的有远程服务，也能先验证生成出来的 pytest 文件是否合理。

这对开发 AI test generator 很重要，因为你可以把问题拆成两层：

1. 生成逻辑是否正确
2. 测试执行逻辑是否正确

## 如何运行

### 1. 准备环境

你需要本地安装：

- Python 3
- `pytest`
- `requests`
- Ollama
- 一个本地已拉取的模型，例如 `qwen2.5:7b`

### 2. 配置环境变量

可选环境变量：

```bash
export OLLAMA_BASE_URL=http://127.0.0.1:11434
export OLLAMA_MODEL=qwen2.5:7b
```

### 3. 生成测试文件

```bash
python main.py
```

程序会：

- 读取 `generator/apis.json`
- 检查 Ollama 可用性
- 依次生成每个接口的测试文件
- 将结果写到 `tests/generated/`

### 4. 运行测试

```bash
pytest
```

如果只想跑生成结果：

```bash
pytest tests/generated -v -s
```

## 如何新增一个 API

只需要修改 [`generator/apis.json`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/apis.json)，增加一个新的 schema，例如：

```json
{
  "method": "POST",
  "path": "/reset-password",
  "request_fields": {
    "email": "string"
  },
  "response_fields": {
    "message": "string"
  },
  "success_rules": {
    "required_fields": ["email"],
    "contains": {
      "email": "@"
    }
  }
}
```

然后重新执行：

```bash
python main.py
```

程序会自动生成一个新的测试文件，例如：

```text
tests/generated/test_reset_password.py
```

## 当前设计的优点

- 结构清晰：LLM 调用、数据清洗、断言构建、模板渲染已经拆开
- 可调试：出了问题时可以定位是 prompt、模型输出、规则纠偏还是模板拼接的问题
- 比直接生成代码稳定：结构化 JSON 更容易做本地修复
- 易扩展：新增 API 时不需要手写测试文件
- 对新手友好：这是一个很好的 AI + 测试自动化练手项目

## 当前局限和后续可改进点

这个项目已经有一条完整主链路，但如果继续往“可维护工具”方向发展，下面这些点值得优先处理。

### 1. `clean_llm_output()` 对 JSON 输出不够专门

[`generator/output_cleaner.py`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/output_cleaner.py) 最初更像是为“清洗 Python 代码”设计的，因为它会寻找 `def test_`。

在当前主链路里，LLM 输出的是 JSON 列表，这个函数虽然还能工作，但并不够专门。更稳妥的做法是新增一个针对 JSON 的清洗器，例如：

- 去除 markdown fence
- 截取第一个 `[` 到最后一个 `]`
- 明确保证返回的是合法 JSON 文本

### 2. `code_validator.py` 只做了非常浅的校验

当前只检查字符串里有没有：

- `def test_`
- `assert`
- `api_client`

这对防止语法错误和结构错误帮助有限。后续可以加入：

- `ast.parse()` 校验语法
- 自动运行 `compile()`
- 校验 `case["data"]` 是否被正确引用
- 校验是否存在 `response.status_code` 和 `response.json()`

### 3. 成功规则目前仍然是手工配置规则

[`generator/apis.json`](/Users/lixiaowei/myProject/MyPythonProject/My_Pytest/generator/apis.json) 中的 `success_rules` 很实用，但本质上仍是手工维护。

后续可以考虑：

- 支持更丰富的规则类型
- 从 OpenAPI schema 自动导入约束
- 用 schema 驱动 `_is_success_case()`

### 4. 目前只覆盖了很基础的响应断言

当前断言主要包括：

- 字段存在
- 字段类型
- 简单非空或数值范围

后续可以扩展为：

- 错误消息断言
- 正则格式断言
- 枚举值断言
- 嵌套 JSON 结构断言
- 列表元素断言

### 5. 目前只支持较简单的 API 测试模式

现阶段更适合：

- 单接口
- 简单请求体
- 简单成功/失败规则

还不太适合：

- 多步骤业务流
- 鉴权依赖
- 复杂嵌套对象
- 动态上下文依赖
- 跨接口数据传递

## 这个项目说明了什么

这是一个很典型的“AI 辅助自动化工具”雏形。

它不是把“让大模型直接写测试代码”当成唯一目标，而是通过工程化方式控制模型输出，把不稳定部分限制在较小范围内，再由本地代码接管关键逻辑。这是一个正确的方向，也是很多真实 AI 工具最终会采用的结构。

如果继续迭代，这个项目可以逐步发展成：

- 一个 schema 驱动的测试生成器
- 一个本地 API 测试脚手架
- 一个面向接口测试学习的 AI 工程项目

## 未来可以考虑增加的功能

- 支持 `GET`、`PUT`、`DELETE`
- 支持 query params 和 path params
- 支持从 OpenAPI/Swagger 自动导入接口定义
- 支持失败用例更细粒度的错误断言
- 支持按标签或模块批量生成
- 支持生成测试报告
- 支持将生成前后的中间结果落盘，便于调试
- 支持对生成文件自动执行 pytest 验证

## 总结

这个项目已经具备一个 AI test generator 的核心骨架：

- 有 schema 输入
- 有 prompt 生成
- 有 LLM 调用
- 有本地纠偏
- 有模板化测试代码输出
- 有本地 mock fixture 验证

对于第一个 AI 测试生成项目来说，这个结构是合理的，而且方向是对的。下一步最值得做的不是继续堆 prompt，而是继续加强“本地规则、校验、可观测性和扩展性”。
