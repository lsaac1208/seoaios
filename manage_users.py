#!/usr/bin/env python
"""
SEO AIOS 用户管理命令行工具
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User


def create_admin(username='admin', password='admin123', email='admin@example.com'):
    """创建管理员用户"""
    app = create_app()

    with app.app_context():
        # 检查用户是否已存在
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"用户 {username} 已存在")
            # 更新密码
            user.set_password(password)
            user.email = email
            user.is_admin = True
            user.is_active = True
            db.session.commit()
            print(f"已更新用户 {username} 的密码和权限")
        else:
            # 创建新用户
            user = User(
                username=username,
                email=email,
                nickname=username
            )
            user.set_password(password)
            user.is_admin = True
            user.is_active = True
            db.session.add(user)
            db.session.commit()
            print(f"已创建管理员用户: {username}")

        print(f"\n登录信息:")
        print(f"  用户名: {username}")
        print(f"  密码: {password}")
        print(f"  邮箱: {email}")


def create_user(username, password, email, is_admin=False):
    """创建普通用户"""
    app = create_app()

    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"用户 {username} 已存在，更新密码...")
            user.set_password(password)
            user.email = email
            user.is_admin = is_admin
            db.session.commit()
        else:
            user = User(
                username=username,
                email=email,
                nickname=username
            )
            user.set_password(password)
            user.is_admin = is_admin
            user.is_active = True
            db.session.add(user)
            db.session.commit()
            print(f"已创建用户: {username} (管理员: {is_admin})")


def list_users():
    """列出所有用户"""
    app = create_app()

    with app.app_context():
        users = User.query.all()
        print(f"\n{'ID':<5} {'用户名':<15} {'邮箱':<30} {'管理员':<10} {'激活':<10}")
        print("-" * 75)
        for u in users:
            print(f"{u.id:<5} {u.username:<15} {u.email:<30} {'是' if u.is_admin else '否':<10} {'是' if u.is_active else '否':<10}")


def reset_password(username, new_password):
    """重置用户密码"""
    app = create_app()

    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            print(f"用户 {username} 不存在")
            return

        user.set_password(new_password)
        db.session.commit()
        print(f"已重置用户 {username} 的密码")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法:")
        print("  python manage_users.py admin [密码]     - 创建/重置管理员")
        print("  python manage_users.py create 用户名 密码 邮箱 [admin] - 创建用户")
        print("  python manage_users.py list                - 列出所有用户")
        print("  python manage_users.py reset 用户名 新密码  - 重置密码")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'admin':
        password = sys.argv[2] if len(sys.argv) > 2 else 'admin123'
        create_admin('admin', password, 'admin@example.com')
    elif command == 'create':
        if len(sys.argv) < 5:
            print("用法: python manage_users.py create 用户名 密码 邮箱 [admin]")
            sys.exit(1)
        username = sys.argv[2]
        password = sys.argv[3]
        email = sys.argv[4]
        is_admin = len(sys.argv) > 5 and sys.argv[5] == 'admin'
        create_user(username, password, email, is_admin)
    elif command == 'list':
        list_users()
    elif command == 'reset':
        if len(sys.argv) < 4:
            print("用法: python manage_users.py reset 用户名 新密码")
            sys.exit(1)
        username = sys.argv[2]
        new_password = sys.argv[3]
        reset_password(username, new_password)
    else:
        print(f"未知命令: {command}")
        sys.exit(1)
