"""
SEO AIOS 配置模块
Automated SEO Content Factory Configuration
"""

import os
from datetime import timedelta


class Config:
    """基础配置"""

    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///seoaios.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # 分页配置
    ITEMS_PER_PAGE = 20

    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # 开发环境设为False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # 上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'svg', 'ico'}

    # Celery配置
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_ENABLE_UTC = False
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 30 * 60  # 30分钟

    # Redis配置
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')

    # AI配置
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENAI_API_BASE = os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-3.5-turbo')

    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
    ANTHROPIC_MODEL = os.environ.get('ANTHROPIC_MODEL', 'claude-3-haiku-20240307')

    # 默认AI Provider
    DEFAULT_AI_PROVIDER = os.environ.get('DEFAULT_AI_PROVIDER', 'openai')

    # 内容生成配置
    DEFAULT_ARTICLE_LENGTH = int(os.environ.get('DEFAULT_ARTICLE_LENGTH', 1500))
    DEFAULT_TITLE_LENGTH = int(os.environ.get('DEFAULT_TITLE_LENGTH', 60))
    DEFAULT_DESCRIPTION_LENGTH = int(os.environ.get('DEFAULT_DESCRIPTION_LENGTH', 160))

    # 爬虫配置
    CRAWL_TIMEOUT = int(os.environ.get('CRAWL_TIMEOUT', 30))
    CRAWL_MAX_DEPTH = int(os.environ.get('CRAWL_MAX_DEPTH', 3))
    CRAWL_DELAY = float(os.environ.get('CRAWL_DELAY', 1.0))  # 请求间隔(秒)
    CRAWL_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

    # 站点生成配置
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'site_templates')

    # 调度配置
    SCHEDULER_API_ENABLED = True

    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'seoaios.log')


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost/seoaios')


class TestingConfig(Config):
    """测试环境配置"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key'
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_ECHO = False


# 配置字典
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """获取当前环境配置"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)
