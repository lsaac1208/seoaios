"""
SEO AIOS CSRF保护工具
CSRF Protection Utilities
"""

from flask_wtf.csrf import generate_csrf


def get_csrf_token():
    """获取CSRF Token的辅助函数"""
    from flask import session
    return generate_csrf()
