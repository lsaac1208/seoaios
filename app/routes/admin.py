"""
SEO AIOS 管理后台路由
Admin Routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from app import db
from app.models import User, Site, Article, Keyword, Task, Setting
from app.utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@login_required
@admin_required
def index():
    """管理后台首页"""
    # 统计信息
    stats = {
        'total_users': User.query.count(),
        'total_sites': Site.query.count(),
        'total_articles': Article.query.count(),
        'total_keywords': Keyword.query.count(),
        'total_tasks': Task.query.count(),
    }

    # 最近7天数据
    week_ago = datetime.utcnow() - timedelta(days=7)
    stats['new_users'] = User.query.filter(User.created_at >= week_ago).count()
    stats['new_sites'] = Site.query.filter(Site.created_at >= week_ago).count()
    stats['new_articles'] = Article.query.filter(Article.created_at >= week_ago).count()

    # 系统状态
    system_info = {
        'python_version': '3.11+',
        'flask_version': '2.3+',
        'database': 'SQLite',
    }

    return render_template('admin/index.html', stats=stats, system_info=system_info)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """用户管理"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # 搜索
    search = request.args.get('search', '')
    query = User.query
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search))
        )

    # 分页
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('admin/users.html',
                         users=pagination.items,
                         pagination=pagination,
                         search=search)


@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """用户详情"""
    user = User.query.get_or_404(user_id)

    # 用户的站点、文章、关键词统计
    user_stats = {
        'sites': Site.query.filter_by(user_id=user_id).count(),
        'articles': Article.query.join(Site).filter(Site.user_id == user_id).count(),
        'keywords': Keyword.query.filter_by(user_id=user_id).count(),
        'tasks': Task.query.filter_by(user_id=user_id).count(),
    }

    return render_template('admin/user_detail.html', user=user, stats=user_stats)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(user_id):
    """编辑用户"""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        nickname = request.form.get('nickname', '').strip()
        email = request.form.get('email', '').strip()
        is_active = request.form.get('is_active') == 'on'
        is_admin = request.form.get('is_admin') == 'on'

        # 验证
        if email != user.email:
            existing = User.query.filter_by(email=email).first()
            if existing:
                flash('邮箱已被使用', 'danger')
                return redirect(url_for('admin.user_edit', user_id=user_id))

        user.nickname = nickname
        user.email = email
        user.is_active = is_active
        # 不允许通过界面修改自己的admin权限
        if current_user.id != user_id:
            user.is_admin = is_admin

        db.session.commit()
        flash('用户信息已更新', 'success')
        return redirect(url_for('admin.user_detail', user_id=user_id))

    return render_template('admin/user_edit.html', user=user)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def user_delete(user_id):
    """删除用户"""
    if current_user.id == user_id:
        flash('不能删除自己', 'danger')
        return redirect(url_for('admin.users'))

    user = User.query.get_or_404(user_id)

    # 删除用户的站点（ cascade 会删除文章等）
    db.session.delete(user)
    db.session.commit()

    flash(f'用户 {user.username} 已删除', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def user_toggle_status(user_id):
    """切换用户状态"""
    user = User.query.get_or_404(user_id)

    if current_user.id == user_id:
        return jsonify({'success': False, 'error': '不能修改自己的状态'})

    user.is_active = not user.is_active
    db.session.commit()

    status = '激活' if user.is_active else '禁用'
    flash(f'用户已{status}', 'success')

    return jsonify({'success': True, 'is_active': user.is_active})


@admin_bp.route('/sites')
@login_required
@admin_required
def sites():
    """站点管理"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # 搜索
    search = request.args.get('search', '')
    query = Site.query
    if search:
        query = query.filter(
            (Site.name.contains(search)) |
            (Site.domain.contains(search))
        )

    # 筛选状态
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    # 分页
    pagination = query.order_by(Site.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # 统计数据
    status_counts = db.session.query(
        Site.status,
        db.func.count(Site.id)
    ).group_by(Site.status).all()

    return render_template('admin/sites.html',
                         sites=pagination.items,
                         pagination=pagination,
                         search=search,
                         status=status,
                         status_counts=dict(status_counts))


@admin_bp.route('/sites/<int:site_id>')
@login_required
@admin_required
def site_detail(site_id):
    """站点详情"""
    site = Site.query.get_or_404(site_id)
    articles = Article.query.filter_by(site_id=site_id).limit(10).all()

    return render_template('admin/site_detail.html', site=site, articles=articles)


@admin_bp.route('/sites/<int:site_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def site_toggle_status(site_id):
    """切换站点状态"""
    site = Site.query.get_or_404(site_id)

    site.status = 'inactive' if site.status == 'active' else 'active'
    db.session.commit()

    return jsonify({'success': True, 'status': site.status})


@admin_bp.route('/articles')
@login_required
@admin_required
def articles():
    """文章管理"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # 搜索
    search = request.args.get('search', '')
    query = Article.query
    if search:
        query = query.filter(Article.title.contains(search))

    # 筛选状态
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)

    # 分页
    pagination = query.order_by(Article.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('admin/articles.html',
                         articles=pagination.items,
                         pagination=pagination,
                         search=search,
                         status=status)


@admin_bp.route('/articles/<int:article_id>/delete', methods=['POST'])
@login_required
@admin_required
def article_delete(article_id):
    """删除文章"""
    article = Article.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()

    flash('文章已删除', 'success')
    return redirect(url_for('admin.articles'))


@admin_bp.route('/tasks')
@login_required
@admin_required
def tasks():
    """任务管理"""
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # 筛选状态
    status = request.args.get('status')
    query = Task.query
    if status:
        query = query.filter_by(status=status)

    # 分页
    pagination = query.order_by(Task.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template('admin/tasks.html',
                         tasks=pagination.items,
                         pagination=pagination,
                         status=status)


@admin_bp.route('/tasks/<int:task_id>/cancel', methods=['POST'])
@login_required
@admin_required
def task_cancel(task_id):
    """取消任务"""
    task = Task.query.get_or_404(task_id)
    if task.status in ['pending', 'running']:
        task.status = 'cancelled'
        db.session.commit()
        flash('任务已取消', 'success')
    else:
        flash('无法取消该任务', 'warning')

    return redirect(url_for('admin.tasks'))


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_settings():
    """系统设置"""
    if request.method == 'POST':
        # 保存设置

        for key, value in request.form.items():
            setting = Setting.query.filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                setting = Setting(key=key, value=value)
                db.session.add(setting)

        db.session.commit()
        flash('设置已保存', 'success')
        return redirect(url_for('admin.admin_settings'))

    # 获取所有设置
    all_settings = Setting.query.all()
    settings_dict = {s.key: s.value for s in all_settings}

    return render_template('admin/settings.html', settings=settings_dict)


@admin_bp.route('/ai-settings', methods=['GET', 'POST'])
@login_required
@admin_required
def ai_settings():
    """AI配置"""
    if request.method == 'POST':
        # 保存AI设置
        ai_settings_keys = [
            'openai_api_key', 'openai_api_base', 'openai_model',
            'anthropic_api_key', 'anthropic_model',
            'deepseek_api_key', 'deepseek_model',
            'minimax_api_key', 'minimax_group_id', 'minimax_model',
            'gemini_api_key', 'gemini_model',
            'azure_api_key', 'azure_api_base', 'azure_deployment',
            'default_provider', 'temperature', 'default_article_length'
        ]

        for key in ai_settings_keys:
            value = request.form.get(key, '').strip()
            setting = Setting.query.filter_by(key=key).first()
            if setting:
                setting.value = value
            else:
                setting = Setting(key=key, value=value)
                db.session.add(setting)

        db.session.commit()
        flash('AI配置已保存', 'success')
        return redirect(url_for('admin.ai_settings'))

    # 获取所有AI设置
    all_settings = Setting.query.all()
    settings = {s.key: s.value for s in all_settings}

    return render_template('admin/ai_settings.html', settings=settings)


@admin_bp.route('/system-info')
@login_required
@admin_required
def system_info():
    """系统信息"""
    import sys
    import platform

    info = {
        'python_version': sys.version,
        'platform': platform.platform(),
        'architecture': platform.architecture(),
        'processor': platform.processor(),
    }

    return render_template('admin/system_info.html', info=info)


@admin_bp.route('/stats')
@login_required
@admin_required
def stats():
    """统计数据"""
    # 用户增长
    user_growth = []
    for i in range(30):
        date = datetime.utcnow() - timedelta(days=29-i)
        date_str = date.strftime('%Y-%m-%d')
        count = User.query.filter(
            db.func.date(User.created_at) == date_str
        ).count()
        user_growth.append({'date': date_str, 'count': count})

    # 内容增长
    content_growth = []
    for i in range(30):
        date = datetime.utcnow() - timedelta(days=29-i)
        date_str = date.strftime('%Y-%m-%d')
        count = Article.query.filter(
            db.func.date(Article.created_at) == date_str
        ).count()
        content_growth.append({'date': date_str, 'count': count})

    return jsonify({
        'user_growth': user_growth,
        'content_growth': content_growth
    })
