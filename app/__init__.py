"""
SEO AIOS - 应用工厂模块
Automated SEO Content Factory - Application Factory
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_cors import CORS
from config import config_by_name

# 初始化扩展
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def setup_logging(app: Flask):
    """配置日志"""
    if not app.debug:
        # 创建日志目录
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)

        # 文件日志
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'seoaios.log'),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('SEO AIOS startup')


def create_app(config_name: str = 'development') -> Flask:
    """
    创建Flask应用实例

    Args:
        config_name: 配置名称 (development/production/testing)

    Returns:
        Flask应用实例
    """
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )

    # 加载配置
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 配置登录
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    login_manager.session_protection = 'strong'

    # 注册user_loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # 配置日志
    setup_logging(app)

    # 注册蓝图
    register_blueprints(app)

    # 创建数据库表
    with app.app_context():
        db.create_all()

    # 注册模板过滤器
    register_template_filters(app)

    # 注册shell上下文
    register_shell_context(app)

    return app


def register_blueprints(app: Flask):
    """注册蓝图"""
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.sites import sites_bp
    from app.routes.articles import articles_bp
    from app.routes.seo import seo_bp
    from app.routes.ai import ai_bp
    from app.routes.tasks import tasks_bp
    from app.routes.api import api_bp

    # 前台页面蓝图
    app.register_blueprint(main_bp)

    # 认证蓝图
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # 站点管理蓝图
    app.register_blueprint(sites_bp, url_prefix='/sites')

    # 文章管理蓝图
    app.register_blueprint(articles_bp, url_prefix='/articles')

    # SEO优化蓝图
    app.register_blueprint(seo_bp, url_prefix='/seo')

    # AI功能蓝图
    app.register_blueprint(ai_bp, url_prefix='/ai')

    # 任务调度蓝图
    app.register_blueprint(tasks_bp, url_prefix='/tasks')

    # API蓝图
    app.register_blueprint(api_bp, url_prefix='/api')


def register_template_filters(app: Flask):
    """注册模板过滤器"""
    from app.utils.filters import (
        format_datetime,
        truncate_html,
        domain_from_url,
        file_size,
        time_ago
    )

    # 注册过滤器 - 使用正确的名称
    app.jinja_env.filters['format_datetime'] = format_datetime
    app.jinja_env.filters['truncate_html'] = truncate_html
    app.jinja_env.filters['domain'] = domain_from_url
    app.jinja_env.filters['filesize'] = file_size
    app.jinja_env.filters['time_ago'] = time_ago


def register_shell_context(app: Flask):
    """注册shell上下文"""
    @app.shell_context_processor
    def make_shell_context():
        from app.models import User, Site, Article, Keyword, Task, SeoConfig, AiConfig
        return {
            'db': db,
            'User': User,
            'Site': Site,
            'Article': Article,
            'Keyword': Keyword,
            'Task': Task,
            'SeoConfig': SeoConfig,
            'AiConfig': AiConfig
        }
