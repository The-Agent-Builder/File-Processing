"""
文件处理预制件

封装文件解析 API，支持将 PDF、Markdown、图片等文件解析为纯文本（Markdown 格式）。

📁 文件路径约定：
- 输入文件：data/inputs/<文件名>
- 输出文件：data/outputs/<文件名>

API 地址：http://10.0.0.111:31475
"""

import requests
from pathlib import Path
from typing import Dict

# 固定路径常量
# v3.0: 文件组按 manifest 中的 key 组织（这里是 "input"）
DATA_INPUTS = Path("data/inputs/input")
DATA_OUTPUTS = Path("data/outputs")

# API 配置
API_BASE_URL = "http://10.0.0.111:31475"


def parse_file() -> Dict:
    """
    解析文件为 Markdown 格式的纯文本

    支持的文件格式：
    - PDF 文档
    - Markdown 文件
    - 图片（PNG, JPG, JPEG 等）
    - 其他文档格式

    文件会被自动从 data/inputs/ 读取，解析结果写入 data/outputs/

    Returns:
        包含解析结果的字典
        - success: 操作是否成功
        - message: 状态消息
        - content: 解析后的 Markdown 内容（成功时）
        - error: 错误信息（失败时）
        - error_code: 错误代码（失败时）

    Examples:
        >>> # 假设 data/inputs/ 下有一个 document.pdf
        >>> result = parse_file()
        >>> print(result["content"])  # 输出解析后的 Markdown 文本
    """
    try:
        # 检查输入文件
        input_files = list(DATA_INPUTS.glob("*"))
        if not input_files:
            return {
                "success": False,
                "error": "未找到输入文件",
                "error_code": "NO_INPUT_FILE"
            }

        # 获取第一个文件
        input_file = input_files[0]

        # 构造 API 请求
        url = f"{API_BASE_URL}/parse"

        # 打开文件并发送请求
        with open(input_file, 'rb') as f:
            files = {'file': (input_file.name, f, 'application/octet-stream')}
            params = {
                'format': 'md',  # 输出格式为 Markdown
                'cache': True
            }

            # 发送请求
            response = requests.post(url, files=files, params=params, timeout=300)
            response.raise_for_status()

        # 解析响应
        result = response.json()

        # 检查响应状态
        if result.get('code') != 200:
            return {
                "success": False,
                "error": result.get('message', '解析失败'),
                "error_code": "PARSE_FAILED"
            }

        # 获取解析内容
        content = result.get('content', '')

        # 确保输出目录存在
        DATA_OUTPUTS.mkdir(parents=True, exist_ok=True)

        # 保存解析结果到输出文件
        output_filename = f"{input_file.stem}_parsed.md"
        output_path = DATA_OUTPUTS / output_filename
        output_path.write_text(content, encoding='utf-8')

        return {
            "success": True,
            "message": "文件解析成功",
            "content": content,
            "input_file": input_file.name,
            "output_file": output_filename
        }

    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "请求超时，文件可能过大或服务器响应缓慢",
            "error_code": "TIMEOUT"
        }

    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": f"无法连接到服务器 {API_BASE_URL}",
            "error_code": "CONNECTION_ERROR"
        }

    except requests.exceptions.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP 错误: {e.response.status_code} - {e.response.text}",
            "error_code": "HTTP_ERROR"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "UNEXPECTED_ERROR"
        }
