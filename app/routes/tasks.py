"""
SEO AIOS 任务调度路由
Task Scheduling Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Task, Site
from app.utils.decorators import site_owner_required
from datetime import datetime, timedelta

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/')
@login_required
def index():
    """任务列表"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    task_type = request.args.get('type')
    status = request.args.get('status')

    query = Task.query.filter_by(user_id=current_user.id)

    if task_type:
        query = query.filter_by(task_type=task_type)
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Task.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    tasks = pagination.items

    # 统计
    stats = {
        'pending': Task.query.filter_by(user_id=current_user.id, status='pending').count(),
        'running': Task.query.filter_by(user_id=current_user.id, status='running').count(),
        'completed': Task.query.filter_by(user_id=current_user.id, status='completed').count(),
        'failed': Task.query.filter_by(user_id=current_user.id, status='failed').count(),
    }

    return render_template('tasks/index.html',
                         tasks=tasks,
                         pagination=pagination,
                         stats=stats,
                         current_type=task_type,
                         current_status=status)


@tasks_bp.route('/<int:task_id>')
@login_required
def detail(task_id):
    """任务详情"""
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash('无权访问', 'danger')
        return redirect(url_for('tasks.index'))

    return render_template('tasks/detail.html', task=task)


@tasks_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """创建任务"""
    if request.method == 'POST':
        site_id = request.form.get('site_id', type=int)
        name = request.form.get('name', '').strip()
        task_type = request.form.get('task_type', '').strip()
        schedule = request.form.get('schedule', '').strip()

        # 任务配置
        config = {}
        if task_type == 'crawl':
            config['url'] = request.form.get('crawl_url', '').strip()
            config['max_depth'] = request.form.get('crawl_depth', 2)
        elif task_type == 'generate':
            config['keywords'] = request.form.get('keywords', '').strip().split('\n')
            config['count'] = request.form.get('count', 5)
        elif task_type == 'publish':
            config['site_id'] = site_id
        elif task_type == 'analyze':
            config['site_id'] = site_id

        if not name or not task_type:
            flash('请填写任务名称和类型', 'danger')
            return redirect(url_for('tasks.create'))

        task = Task(
            user_id=current_user.id,
            site_id=site_id,
            name=name,
            task_type=task_type,
            schedule=schedule if schedule else None,
            config=config,
            status='pending'
        )

        db.session.add(task)
        db.session.commit()

        flash('任务创建成功', 'success')
        return redirect(url_for('tasks.detail', task_id=task.id))

    sites = Site.query.filter_by(user_id=current_user.id).all()

    return render_template('tasks/create.html', sites=sites)


@tasks_bp.route('/<int:task_id>/run', methods=['POST'])
@login_required
def run(task_id):
    """立即运行任务"""
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('tasks.index'))

    if task.status == 'running':
        flash('任务正在运行中', 'warning')
        return redirect(url_for('tasks.detail', task_id=task_id))

    # 更新任务状态
    task.status = 'pending'
    task.started_at = None
    task.completed_at = None
    task.error_message = None
    db.session.commit()

    # 触发任务执行
    try:
        from app.services.task_executor import TaskExecutor
        executor = TaskExecutor()
        executor.execute_task(task.id)

        flash('任务已开始执行', 'success')
    except Exception as e:
        flash(f'启动任务失败: {str(e)}', 'danger')

    return redirect(url_for('tasks.detail', task_id=task_id))


@tasks_bp.route('/<int:task_id>/cancel', methods=['POST'])
@login_required
def cancel(task_id):
    """取消任务"""
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('tasks.index'))

    if task.status not in ['pending', 'running']:
        flash('任务无法取消', 'warning')
        return redirect(url_for('tasks.detail', task_id=task_id))

    task.status = 'cancelled'
    db.session.commit()

    flash('任务已取消', 'success')
    return redirect(url_for('tasks.detail', task_id=task_id))


@tasks_bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
def delete(task_id):
    """删除任务"""
    task = Task.query.get_or_404(task_id)

    if task.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('tasks.index'))

    db.session.delete(task)
    db.session.commit()

    flash('任务已删除', 'success')
    return redirect(url_for('tasks.index'))


@tasks_bp.route('/schedule')
@login_required
def schedule():
    """定时任务调度"""
    # 获取已配置定时运行的任务
    scheduled_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.schedule.isnot(None),
        Task.status.in_(['pending', 'completed'])
    ).order_by(Task.name).all()

    return render_template('tasks/schedule.html', scheduled_tasks=scheduled_tasks)


@tasks_bp.route('/logs')
@login_required
def logs():
    """任务日志"""
    task_id = request.args.get('task_id', type=int)

    if task_id:
        task = Task.query.get_or_404(task_id)
        if task.user_id != current_user.id:
            flash('无权访问', 'danger')
            return redirect(url_for('tasks.logs'))
        return render_template('tasks/logs.html', task=task)

    # 获取最近的失败任务
    failed_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.status == 'failed'
    ).order_by(Task.updated_at.desc()).limit(20).all()

    return render_template('tasks/logs.html', failed_tasks=failed_tasks)
