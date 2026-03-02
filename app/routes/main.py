"""
SEO AIOS 主路由
Main Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Site, Article, Keyword, Task

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """首页"""
    if current_user.is_authenticated:
        # 获取统计信息
        sites_count = Site.query.filter_by(user_id=current_user.id).count()
        articles_count = Article.query.filter_by(user_id=current_user.id).count()
        keywords_count = Keyword.query.filter_by(user_id=current_user.id).count()

        # 最近的文章
        recent_articles = Article.query.filter_by(
            user_id=current_user.id
        ).order_by(Article.created_at.desc()).limit(5).all()

        # 活跃任务
        active_tasks = Task.query.filter(
            Task.user_id == current_user.id,
            Task.status.in_(['pending', 'running'])
        ).order_by(Task.created_at.desc()).limit(5).all()

        return render_template('main/dashboard.html',
                            sites_count=sites_count,
                            articles_count=articles_count,
                            keywords_count=keywords_count,
                            recent_articles=recent_articles,
                            active_tasks=active_tasks)
    return render_template('main/index.html')


@main_bp.route('/about')
def about():
    """关于页面"""
    return render_template('main/about.html')


@main_bp.route('/features')
def features():
    """功能页面"""
    return render_template('main/features.html')


@main_bp.route('/pricing')
def pricing():
    """价格页面"""
    return render_template('main/pricing.html')


@main_bp.route('/docs')
def docs():
    """文档页面"""
    return render_template('main/docs.html')


@main_bp.route('/health')
def health():
    """健康检查"""
    from flask import jsonify
    return jsonify({'status': 'ok', 'version': '1.0.0'})
