"""
SEO AIOS 测试配置
"""

import os
import tempfile


class TestConfig:
    """测试配置"""
    TESTING = True
    WTF_CSRF_ENABLED = False

    # 使用内存数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 密钥
    SECRET_KEY = 'test-secret-key'

    # 会话
    SESSION_COOKIE_SECURE = False

    # 测试不需要Celery
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

    # AI配置 (使用mock)
    OPENAI_API_KEY = 'test-key'
    ANTHROPIC_API_KEY = 'test-key'

    # 上传目录
    UPLOAD_FOLDER = tempfile.mkdtemp()
    OUTPUT_DIR = tempfile.mkdtemp()

    # 爬虫配置
    CRAWL_TIMEOUT = 5
    CRAWL_MAX_DEPTH = 1
