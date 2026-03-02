"""
SEO AIOS 测试配置文件
Pytest Configuration and Fixtures
"""

import pytest
import os
import sys

# 确保项目根目录在Python路径中
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


@pytest.fixture(scope='session')
def app():
    """创建应用实例"""
    # 设置测试环境
    os.environ['FLASK_ENV'] = 'testing'

    from app import create_app
    app = create_app('testing')
    return app


@pytest.fixture(scope='function')
def app_context(app):
    """创建应用上下文"""
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def db(app_context):
    """创建数据库"""
    from app import db
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()


@pytest.fixture
def session(db):
    """创建数据库会话"""
    return db.session
