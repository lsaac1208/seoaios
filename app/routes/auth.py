"""
SEO AIOS 认证路由
Authentication Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from app import db
from app.models import User
from app.utils.decorators import admin_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        if not username or not password:
            flash('请输入用户名和密码', 'danger')
            return render_template('auth/login.html')

        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('账户已被禁用', 'danger')
                return render_template('auth/login.html')

            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()

            flash(f'欢迎回来, {user.nickname or user.username}!', 'success')

            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.index')
            return redirect(next_page)
        else:
            flash('用户名或密码错误', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """注册页面"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password2 = request.form.get('password2', '')
        nickname = request.form.get('nickname', '').strip()

        # 验证
        if not username or not email or not password:
            flash('请填写所有必填项', 'danger')
            return render_template('auth/register.html')

        if password != password2:
            flash('两次输入的密码不一致', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('密码长度至少6位', 'danger')
            return render_template('auth/register.html')

        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('邮箱已被注册', 'danger')
            return render_template('auth/register.html')

        # 创建用户
        user = User(
            username=username,
            email=email,
            nickname=nickname or username
        )
        user.set_password(password)

        # 如果是第一个用户，设为管理员
        if User.query.count() == 0:
            user.is_admin = True
            user.is_active = True

        db.session.add(user)
        db.session.commit()

        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """退出登录"""
    logout_user()
    flash('您已退出登录', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """个人资料"""
    if request.method == 'POST':
        nickname = request.form.get('nickname', '').strip()
        email = request.form.get('email', '').strip()
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        new_password2 = request.form.get('new_password2', '')

        # 验证邮箱
        if email != current_user.email:
            if User.query.filter_by(email=email).first():
                flash('邮箱已被使用', 'danger')
                return render_template('auth/profile.html')
            current_user.email = email

        # 更新密码
        if new_password:
            if not current_password:
                flash('请输入当前密码', 'danger')
                return render_template('auth/profile.html')
            if not current_user.check_password(current_password):
                flash('当前密码错误', 'danger')
                return render_template('auth/profile.html')
            if new_password != new_password2:
                flash('两次输入的密码不一致', 'danger')
                return render_template('auth/profile.html')
            if len(new_password) < 6:
                flash('新密码长度至少6位', 'danger')
                return render_template('auth/profile.html')
            current_user.set_password(new_password)

        # 更新其他信息
        current_user.nickname = nickname
        db.session.commit()

        flash('资料已更新', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')


@auth_bp.route('/password/reset', methods=['GET', 'POST'])
def password_reset_request():
    """密码重置请求"""
    # TODO: 实现邮件发送功能
    flash('密码重置功能开发中', 'info')
    return redirect(url_for('auth.login'))
