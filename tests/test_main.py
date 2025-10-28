"""
文件处理预制件测试

测试文件解析功能，确保 API 封装正常工作。
"""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.main import parse_file


class TestParseFile:
    """测试文件解析功能"""

    @pytest.fixture
    def workspace(self):
        """创建临时工作空间"""
        temp_dir = tempfile.mkdtemp()
        workspace_path = Path(temp_dir)

        # 创建目录结构
        inputs_dir = workspace_path / "data" / "inputs"
        inputs_dir.mkdir(parents=True)

        # 创建测试输入文件（模拟 PDF）
        test_file = inputs_dir / "test.pdf"
        test_file.write_bytes(b"Mock PDF content")

        # 切换到工作空间
        original_cwd = os.getcwd()
        os.chdir(workspace_path)

        yield workspace_path

        # 清理
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)

    def test_parse_file_success(self, workspace):
        """测试成功解析文件"""
        # Mock API 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'code': 200,
            'message': 'success',
            'content': '# Test Document\n\nThis is a test.'
        }

        with patch('requests.post', return_value=mock_response):
            result = parse_file()

        assert result["success"] is True
        assert result["message"] == "文件解析成功"
        assert "# Test Document" in result["content"]
        assert result["input_file"] == "test.pdf"
        assert result["output_file"] == "test_parsed.md"

        # 验证输出文件存在
        output_files = list((workspace / "data/outputs").glob("*"))
        assert len(output_files) == 1
        assert output_files[0].name == "test_parsed.md"
        assert "# Test Document" in output_files[0].read_text(encoding="utf-8")

    def test_parse_file_no_input(self, workspace):
        """测试没有输入文件"""
        # 删除所有输入文件
        for f in (workspace / "data/inputs").glob("*"):
            f.unlink()

        result = parse_file()

        assert result["success"] is False
        assert result["error_code"] == "NO_INPUT_FILE"
        assert "未找到输入文件" in result["error"]

    def test_parse_file_api_error(self, workspace):
        """测试 API 返回错误"""
        # Mock API 错误响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'code': 500,
            'message': 'Internal server error'
        }

        with patch('requests.post', return_value=mock_response):
            result = parse_file()

        assert result["success"] is False
        assert result["error_code"] == "PARSE_FAILED"
        assert "Internal server error" in result["error"]

    def test_parse_file_timeout(self, workspace):
        """测试请求超时"""
        import requests

        with patch('requests.post', side_effect=requests.exceptions.Timeout):
            result = parse_file()

        assert result["success"] is False
        assert result["error_code"] == "TIMEOUT"
        assert "超时" in result["error"]

    def test_parse_file_connection_error(self, workspace):
        """测试连接错误"""
        import requests

        with patch('requests.post', side_effect=requests.exceptions.ConnectionError):
            result = parse_file()

        assert result["success"] is False
        assert result["error_code"] == "CONNECTION_ERROR"
        assert "无法连接" in result["error"]

    def test_parse_file_http_error(self, workspace):
        """测试 HTTP 错误"""
        import requests

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)

        with patch('requests.post', return_value=mock_response):
            result = parse_file()

        assert result["success"] is False
        assert result["error_code"] == "HTTP_ERROR"
        assert "HTTP 错误" in result["error"]
