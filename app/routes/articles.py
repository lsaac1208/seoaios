"""
SEO AIOS 文章管理路由
Article Management Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Article, Category, Site, ArticleSeoData
from app.utils.decorators import site_owner_required
from datetime import datetime

articles_bp = Blueprint('articles', __name__)


@articles_bp.route('/')
@login_required
def index():
    """文章列表"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    site_id = request.args.get('site_id', type=int)
    status = request.args.get('status')
    category_id = request.args.get('category_id', type=int)

    query = Article.query.filter_by(user_id=current_user.id)

    if site_id:
        query = query.filter_by(site_id=site_id)
    if status:
        query = query.filter_by(status=status)
    if category_id:
        query = query.filter_by(category_id=category_id)

    pagination = query.order_by(Article.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    articles = pagination.items

    # 获取用户的站点列表用于筛选
    sites = Site.query.filter_by(user_id=current_user.id).all()

    return render_template('articles/index.html',
                         articles=articles,
                         pagination=pagination,
                         sites=sites,
                         current_site_id=site_id,
                         current_status=status)


@articles_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """新建文章"""
    if request.method == 'POST':
        site_id = request.form.get('site_id', type=int)
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        excerpt = request.form.get('excerpt', '').strip()
        category_id = request.form.get('category_id', type=int)
        tags = request.form.get('tags', '').strip()
        status = request.form.get('status', 'draft')
        allow_comments = request.form.get('allow_comments', 'on') == 'on'

        # SEO字段
        meta_title = request.form.get('meta_title', '').strip()
        meta_description = request.form.get('meta_description', '').strip()
        meta_keywords = request.form.get('meta_keywords', '').strip()

        # 验证
        if not site_id or not title or not content:
            flash('请填写必填项', 'danger')
            return redirect(url_for('articles.new'))

        # 验证站点所有权
        site = Site.query.get_or_404(site_id)
        if site.user_id != current_user.id:
            flash('无权操作', 'danger')
            return redirect(url_for('articles.index'))

        # 生成slug
        from app.utils.helpers import slugify
        slug = slugify(title)
        # 确保slug唯一
        base_slug = slug
        counter = 1
        while Article.query.filter_by(site_id=site_id, slug=slug).first():
            slug = f'{base_slug}-{counter}'
            counter += 1

        # 创建文章
        article = Article(
            site_id=site_id,
            user_id=current_user.id,
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt or content[:200],
            category_id=category_id,
            tags=tags,
            status=status,
            allow_comments=allow_comments,
            meta_title=meta_title or title,
            meta_description=meta_description,
            meta_keywords=meta_keywords
        )

        if status == 'published':
            article.published_at = datetime.utcnow()

        db.session.add(article)
        db.session.commit()

        flash('文章创建成功', 'success')
        return redirect(url_for('articles.edit', article_id=article.id))

    # 获取用户的站点列表
    sites = Site.query.filter_by(user_id=current_user.id).all()
    categories = []
    if sites:
        categories = Category.query.filter_by(site_id=sites[0].id).all()

    return render_template('articles/new.html', sites=sites, categories=categories)


@articles_bp.route('/<int:article_id>')
@login_required
def detail(article_id):
    """文章详情"""
    article = Article.query.get_or_404(article_id)

    if article.user_id != current_user.id:
        flash('无权访问', 'danger')
        return redirect(url_for('articles.index'))

    return render_template('articles/detail.html', article=article)


@articles_bp.route('/<int:article_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(article_id):
    """编辑文章"""
    article = Article.query.get_or_404(article_id)

    if article.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('articles.index'))

    if request.method == 'POST':
        article.title = request.form.get('title', '').strip()
        article.content = request.form.get('content', '').strip()
        article.excerpt = request.form.get('excerpt', '').strip()
        article.category_id = request.form.get('category_id', type=int) or None
        article.tags = request.form.get('tags', '').strip()
        article.status = request.form.get('status', 'draft')
        article.allow_comments = request.form.get('allow_comments', 'on') == 'on'

        # SEO字段
        article.meta_title = request.form.get('meta_title', '').strip()
        article.meta_description = request.form.get('meta_description', '').strip()
        article.meta_keywords = request.form.get('meta_keywords', '').strip()

        # 处理发布时间
        if article.status == 'published' and not article.published_at:
            article.published_at = datetime.utcnow()
        elif article.status == 'draft':
            article.published_at = None

        db.session.commit()

        flash('文章已更新', 'success')
        return redirect(url_for('articles.edit', article_id=article.id))

    sites = Site.query.filter_by(user_id=current_user.id).all()
    categories = Category.query.filter_by(site_id=article.site_id).all() if article.site_id else []

    return render_template('articles/edit.html',
                         article=article,
                         sites=sites,
                         categories=categories)


@articles_bp.route('/<int:article_id>/delete', methods=['POST'])
@login_required
def delete(article_id):
    """删除文章"""
    article = Article.query.get_or_404(article_id)

    if article.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('articles.index'))

    db.session.delete(article)
    db.session.commit()

    flash('文章已删除', 'success')
    return redirect(url_for('articles.index'))


@articles_bp.route('/<int:article_id>/publish', methods=['POST'])
@login_required
def publish(article_id):
    """发布文章"""
    article = Article.query.get_or_404(article_id)

    if article.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('articles.index'))

    article.status = 'published'
    article.published_at = datetime.utcnow()
    db.session.commit()

    flash('文章已发布', 'success')
    return redirect(url_for('articles.detail', article_id=article.id))


@articles_bp.route('/<int:article_id>/unpublish', methods=['POST'])
@login_required
def unpublish(article_id):
    """取消发布文章"""
    article = Article.query.get_or_404(article_id)

    if article.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('articles.index'))

    article.status = 'draft'
    db.session.commit()

    flash('文章已取消发布', 'success')
    return redirect(url_for('articles.detail', article_id=article.id))


@articles_bp.route('/<int:article_id>/analyze', methods=['POST'])
@login_required
def analyze(article_id):
    """分析文章SEO"""
    from app.services.seo_analyzer import SeoAnalyzer

    article = Article.query.get_or_404(article_id)

    if article.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('articles.index'))

    try:
        analyzer = SeoAnalyzer()
        result = analyzer.analyze_article(article)

        flash(f'SEO分析完成，得分: {result.get("score", 0)}', 'success')
    except Exception as e:
        flash(f'分析失败: {str(e)}', 'danger')

    return redirect(url_for('articles.detail', article_id=article_id))


@articles_bp.route('/categories')
@login_required
def categories():
    """分类管理"""
    site_id = request.args.get('site_id', type=int)

    if site_id:
        categories = Category.query.filter_by(site_id=site_id).order_by(Category.order).all()
    else:
        categories = Category.query.join(Site).filter(Site.user_id == current_user.id)\
            .order_by(Category.order).all()

    sites = Site.query.filter_by(user_id=current_user.id).all()

    return render_template('articles/categories.html',
                         categories=categories,
                         sites=sites,
                         current_site_id=site_id)


@articles_bp.route('/categories/new', methods=['POST'])
@login_required
def new_category():
    """新建分类"""
    site_id = request.form.get('site_id', type=int)
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    parent_id = request.form.get('parent_id', type=int) or None

    if not site_id or not name:
        flash('请填写必填项', 'danger')
        return redirect(url_for('articles.categories'))

    # 验证站点所有权
    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('articles.categories'))

    # 生成slug
    from app.utils.helpers import slugify
    slug = slugify(name)

    category = Category(
        site_id=site_id,
        name=name,
        slug=slug,
        description=description,
        parent_id=parent_id
    )

    db.session.add(category)
    db.session.commit()

    flash('分类创建成功', 'success')
    return redirect(url_for('articles.categories', site_id=site_id))


@articles_bp.route('/categories/<int:category_id>/edit', methods=['POST'])
@login_required
def edit_category(category_id):
    """编辑分类"""
    category = Category.query.get_or_404(category_id)

    # 验证站点所有权
    site = Site.query.get(category.site_id)
    if site.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('articles.categories'))

    category.name = request.form.get('name', '').strip()
    category.description = request.form.get('description', '').strip()
    category.parent_id = request.form.get('parent_id', type=int) or None

    db.session.commit()

    flash('分类已更新', 'success')
    return redirect(url_for('articles.categories', site_id=category.site_id))


@articles_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    """删除分类"""
    category = Category.query.get_or_404(category_id)

    site_id = category.site_id

    # 验证站点所有权
    site = Site.query.get(site_id)
    if site.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('articles.categories'))

    db.session.delete(category)
    db.session.commit()

    flash('分类已删除', 'success')
    return redirect(url_for('articles.categories', site_id=site_id))
