"""
SEO AIOS API路由
API Routes
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models import Site, Article, Page, Keyword, Task
from app import db

api_bp = Blueprint('api', __name__)


# CSRF Token
@api_bp.route('/csrf-token')
def csrf_token():
    """获取CSRF Token"""
    from flask_wtf.csrf import generate_csrf
    return jsonify({'csrf_token': generate_csrf()})


# 用户相关API
@api_bp.route('/user/info')
@login_required
def user_info():
    """获取当前用户信息"""
    return jsonify({
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'nickname': current_user.nickname,
        'is_admin': current_user.is_admin
    })


# 站点相关API
@api_bp.route('/sites')
@login_required
def get_sites():
    """获取用户站点列表"""
    sites = Site.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'domain': s.domain,
        'status': s.status,
        'template': s.template,
        'output_type': s.output_type,
        'created_at': s.created_at.isoformat() if s.created_at else None
    } for s in sites])


@api_bp.route('/sites/<int:site_id>')
@login_required
def get_site(site_id):
    """获取站点详情"""
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        return jsonify({'error': '无权访问'}), 403

    return jsonify({
        'id': site.id,
        'name': site.name,
        'domain': site.domain,
        'description': site.description,
        'keywords': site.keywords,
        'status': site.status,
        'template': site.template,
        'output_type': site.output_type,
        'language': site.language,
        'created_at': site.created_at.isoformat() if site.created_at else None,
        'updated_at': site.updated_at.isoformat() if site.updated_at else None
    })


# 文章相关API
@api_bp.route('/articles')
@login_required
def get_articles():
    """获取文章列表"""
    site_id = request.args.get('site_id', type=int)
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Article.query.filter_by(user_id=current_user.id)

    if site_id:
        query = query.filter_by(site_id=site_id)
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Article.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [{
            'id': a.id,
            'title': a.title,
            'slug': a.slug,
            'status': a.status,
            'views': a.views,
            'published_at': a.published_at.isoformat() if a.published_at else None,
            'created_at': a.created_at.isoformat() if a.created_at else None
        } for a in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@api_bp.route('/articles/<int:article_id>')
@login_required
def get_article(article_id):
    """获取文章详情"""
    article = Article.query.get_or_404(article_id)
    if article.user_id != current_user.id:
        return jsonify({'error': '无权访问'}), 403

    return jsonify({
        'id': article.id,
        'site_id': article.site_id,
        'title': article.title,
        'slug': article.slug,
        'content': article.content,
        'excerpt': article.excerpt,
        'status': article.status,
        'meta_title': article.meta_title,
        'meta_description': article.meta_description,
        'meta_keywords': article.meta_keywords,
        'views': article.views,
        'published_at': article.published_at.isoformat() if article.published_at else None,
        'created_at': article.created_at.isoformat() if article.created_at else None,
        'updated_at': article.updated_at.isoformat() if article.updated_at else None
    })


# 关键词相关API
@api_bp.route('/keywords')
@login_required
def get_keywords():
    """获取关键词列表"""
    site_id = request.args.get('site_id', type=int)

    query = Keyword.query.filter_by(user_id=current_user.id)
    if site_id:
        query = query.filter_by(site_id=site_id)

    keywords = query.order_by(Keyword.search_volume.desc()).limit(100).all()

    return jsonify([{
        'id': k.id,
        'keyword': k.keyword,
        'search_volume': k.search_volume,
        'difficulty': k.difficulty,
        'current_rank': k.current_rank,
        'status': k.status
    } for k in keywords])


# 任务相关API
@api_bp.route('/tasks')
@login_required
def get_tasks():
    """获取任务列表"""
    status = request.args.get('status')
    task_type = request.args.get('type')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    query = Task.query.filter_by(user_id=current_user.id)

    if status:
        query = query.filter_by(status=status)
    if task_type:
        query = query.filter_by(task_type=task_type)

    pagination = query.order_by(Task.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'items': [{
            'id': t.id,
            'name': t.name,
            'task_type': t.task_type,
            'status': t.status,
            'progress': t.progress,
            'message': t.message,
            'created_at': t.created_at.isoformat() if t.created_at else None
        } for t in pagination.items],
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages
    })


@api_bp.route('/tasks/<int:task_id>')
@login_required
def get_task(task_id):
    """获取任务详情"""
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return jsonify({'error': '无权访问'}), 403

    return jsonify({
        'id': task.id,
        'name': task.name,
        'task_type': task.task_type,
        'status': task.status,
        'progress': task.progress,
        'total': task.total,
        'message': task.message,
        'result': task.result,
        'error_message': task.error_message,
        'celery_task_id': task.celery_task_id,
        'created_at': task.created_at.isoformat() if task.created_at else None,
        'started_at': task.started_at.isoformat() if task.started_at else None,
        'completed_at': task.completed_at.isoformat() if task.completed_at else None
    })


# 统计API
@api_bp.route('/stats')
@login_required
def get_stats():
    """获取用户统计信息"""
    sites_count = Site.query.filter_by(user_id=current_user.id).count()
    articles_count = Article.query.filter_by(user_id=current_user.id).count()
    keywords_count = Keyword.query.filter_by(user_id=current_user.id).count()
    tasks_count = Task.query.filter_by(user_id=current_user.id).count()

    # 今日新增
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    today_articles = Article.query.filter(
        Article.user_id == current_user.id,
        db.func.date(Article.created_at) == today
    ).count()

    return jsonify({
        'sites_count': sites_count,
        'articles_count': articles_count,
        'keywords_count': keywords_count,
        'tasks_count': tasks_count,
        'today_articles': today_articles
    })


# 健康检查
@api_bp.route('/health')
def health():
    """API健康检查"""
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })


from datetime import datetime
