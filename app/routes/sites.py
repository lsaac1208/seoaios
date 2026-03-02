"""
SEO AIOS 站点管理路由
Site Management Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Site, SeoConfig, AiConfig, Page, Article
from app.utils.decorators import site_owner_required
from app.services.site_builder import SiteBuilder
from app.services.sitemap_generator import SitemapGenerator
import os

sites_bp = Blueprint('sites', __name__)


@sites_bp.route('/')
@login_required
def index():
    """站点列表"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)

    pagination = Site.query.filter_by(user_id=current_user.id)\
        .order_by(Site.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    sites = pagination.items

    return render_template('sites/index.html',
                         sites=sites,
                         pagination=pagination)


@sites_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """新建站点"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        domain = request.form.get('domain', '').strip()
        description = request.form.get('description', '').strip()
        keywords = request.form.get('keywords', '').strip()
        template = request.form.get('template', 'default')
        output_type = request.form.get('output_type', 'static')
        language = request.form.get('language', 'zh-CN')

        # 验证
        if not name or not domain:
            flash('请填写站点名称和域名', 'danger')
            return render_template('sites/new.html')

        # 验证域名格式
        domain = domain.lower().strip()
        if not domain.startswith(('http://', 'https://')):
            domain = 'https://' + domain

        # 检查域名是否已存在
        if Site.query.filter_by(domain=domain).first():
            flash('该域名已被使用', 'danger')
            return render_template('sites/new.html')

        # 创建站点
        site = Site(
            user_id=current_user.id,
            name=name,
            domain=domain,
            description=description,
            keywords=keywords,
            template=template,
            output_type=output_type,
            language=language,
            status='active'
        )
        db.session.add(site)
        db.session.flush()  # 获取ID

        # 创建默认SEO配置
        seo_config = SeoConfig(
            site_id=site.id,
            default_title=name,
            default_description=description,
            default_keywords=keywords
        )
        db.session.add(seo_config)

        # 创建默认AI配置
        ai_config = AiConfig(site_id=site.id)
        db.session.add(ai_config)

        # 创建默认页面
        default_pages = [
            {'title': '首页', 'slug': '', 'page_type': 'home'},
            {'title': '关于我们', 'slug': 'about', 'page_type': 'about'},
            {'title': '联系我们', 'slug': 'contact', 'page_type': 'contact'},
        ]

        for page_data in default_pages:
            page = Page(
                site_id=site.id,
                title=page_data['title'],
                slug=page_data['slug'],
                page_type=page_data['page_type'],
                status='published',
                order=default_pages.index(page_data)
            )
            db.session.add(page)

        db.session.commit()

        flash('站点创建成功', 'success')
        return redirect(url_for('sites.detail', site_id=site.id))

    templates = _get_available_templates()
    return render_template('sites/new.html', templates=templates)


@sites_bp.route('/<int:site_id>')
@login_required
@site_owner_required
def detail(site_id):
    """站点详情"""
    site = Site.query.get_or_404(site_id)

    # 统计信息
    pages_count = Page.query.filter_by(site_id=site_id).count()
    articles_count = Article.query.filter_by(site_id=site_id).count()

    # 最近的页面
    recent_pages = Page.query.filter_by(site_id=site_id)\
        .order_by(Page.updated_at.desc()).limit(5).all()

    # 最近的文章
    recent_articles = Article.query.filter_by(site_id=site_id)\
        .order_by(Article.created_at.desc()).limit(5).all()

    return render_template('sites/detail.html',
                         site=site,
                         pages_count=pages_count,
                         articles_count=articles_count,
                         recent_pages=recent_pages,
                         recent_articles=recent_articles)


@sites_bp.route('/<int:site_id>/edit', methods=['GET', 'POST'])
@login_required
@site_owner_required
def edit(site_id):
    """编辑站点"""
    site = Site.query.get_or_404(site_id)

    if request.method == 'POST':
        site.name = request.form.get('name', '').strip()
        site.description = request.form.get('description', '').strip()
        site.keywords = request.form.get('keywords', '').strip()
        site.template = request.form.get('template', 'default')
        site.output_type = request.form.get('output_type', 'static')
        site.language = request.form.get('language', 'zh-CN')
        site.timezone = request.form.get('timezone', 'Asia/Shanghai')

        new_domain = request.form.get('domain', '').strip().lower()
        if new_domain and new_domain != site.domain:
            if not new_domain.startswith(('http://', 'https://')):
                new_domain = 'https://' + new_domain
            if Site.query.filter(Site.domain == new_domain, Site.id != site_id).first():
                flash('该域名已被使用', 'danger')
                return render_template('sites/edit.html', site=site)
            site.domain = new_domain

        site.status = request.form.get('status', site.status)
        db.session.commit()

        flash('站点已更新', 'success')
        return redirect(url_for('sites.detail', site_id=site.id))

    return render_template('sites/edit.html', site=site)


@sites_bp.route('/<int:site_id>/delete', methods=['POST'])
@login_required
@site_owner_required
def delete(site_id):
    """删除站点"""
    site = Site.query.get_or_404(site_id)

    db.session.delete(site)
    db.session.commit()

    flash('站点已删除', 'success')
    return redirect(url_for('sites.index'))


@sites_bp.route('/<int:site_id>/build', methods=['POST'])
@login_required
@site_owner_required
def build(site_id):
    """构建站点"""
    site = Site.query.get_or_404(site_id)

    try:
        builder = SiteBuilder(site)
        output_path = builder.build()

        site.output_path = output_path
        db.session.commit()

        flash(f'站点构建成功，输出目录: {output_path}', 'success')
    except Exception as e:
        flash(f'构建失败: {str(e)}', 'danger')

    return redirect(url_for('sites.detail', site_id=site_id))


@sites_bp.route('/<int:site_id>/generate-sitemap', methods=['POST'])
@login_required
@site_owner_required
def generate_sitemap(site_id):
    """生成站点地图"""
    site = Site.query.get_or_404(site_id)

    try:
        generator = SitemapGenerator(site)
        sitemap_path = generator.generate()

        flash(f'站点地图已生成: {sitemap_path}', 'success')
    except Exception as e:
        flash(f'生成失败: {str(e)}', 'danger')

    return redirect(url_for('sites.detail', site_id=site_id))


@sites_bp.route('/<int:site_id>/pages')
@login_required
@site_owner_required
def pages(site_id):
    """站点页面管理"""
    site = Site.query.get_or_404(site_id)

    pages = Page.query.filter_by(site_id=site_id)\
        .order_by(Page.order, Page.created_at.desc()).all()

    return render_template('sites/pages.html', site=site, pages=pages)


@sites_bp.route('/<int:site_id>/settings')
@login_required
@site_owner_required
def settings(site_id):
    """站点设置"""
    site = Site.query.get_or_404(site_id)
    return render_template('sites/settings.html', site=site)


def _get_available_templates():
    """获取可用的模板"""
    templates_dir = current_app.config.get('TEMPLATES_DIR', 'templates/site_templates')
    templates = []

    if os.path.exists(templates_dir):
        for name in os.listdir(templates_dir):
            path = os.path.join(templates_dir, name)
            if os.path.isdir(path):
                templates.append({
                    'name': name,
                    'path': name,
                    'preview': f'/static/templates/{name}/preview.jpg'
                })

    # 添加默认模板
    templates.insert(0, {
        'name': '默认模板',
        'path': 'default',
        'preview': None
    })

    return templates
