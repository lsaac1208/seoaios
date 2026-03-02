"""
SEO AIOS 装饰器
Custom Decorators
"""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from app.models import Site


def site_owner_required(f):
    """
    装饰器：检查用户是否是站点的所有者
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        site_id = kwargs.get('site_id')
        if site_id:
            site = Site.query.get(site_id)
            if site and site.user_id != current_user.id:
                flash('无权访问', 'danger')
                return redirect(url_for('sites.index'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    装饰器：检查用户是否是管理员
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'info')
            return redirect(url_for('auth.login'))
        if not current_user.is_admin:
            flash('需要管理员权限', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def ajax_login_required(f):
    """
    装饰器：AJAX请求需要登录
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            from flask import jsonify
            return jsonify({'error': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function
