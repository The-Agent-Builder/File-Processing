"""
文件处理预制件模块导出

这个文件定义了预制件对外暴露的函数列表。
"""

from .main import parse_file

__all__ = [
    "parse_file",
]
