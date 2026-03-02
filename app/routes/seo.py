"""
SEO AIOS SEO优化路由
SEO Optimization Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Site, Article, Page, SeoConfig, Keyword
from app.services.seo_analyzer import SeoAnalyzer
from app.services.seo_optimizer import SeoOptimizer
from app.services.technical_seo import TechnicalSeoChecker

seo_bp = Blueprint('seo', __name__)


@seo_bp.route('/dashboard')
@login_required
def dashboard():
    """SEO仪表盘"""
    sites = Site.query.filter_by(user_id=current_user.id).all()
    site_id = request.args.get('site_id', type=int)

    if not sites:
        flash('请先创建站点', 'info')
        return redirect(url_for('sites.new'))

    if not site_id:
        site_id = sites[0].id

    site = Site.query.get_or_404(site_id)

    # SEO统计
    articles = Article.query.filter_by(site_id=site_id).all()
    pages = Page.query.filter_by(site_id=site_id).all()

    # 关键词
    keywords = Keyword.query.filter(
        Keyword.user_id == current_user.id,
        Keyword.site_id == site_id
    ).order_by(Keyword.search_volume.desc()).limit(20).all()

    return render_template('seo/dashboard.html',
                         sites=sites,
                         current_site=site,
                         articles_count=len(articles),
                         pages_count=len(pages),
                         keywords=keywords)


@seo_bp.route('/analyze/article/<int:article_id>', methods=['GET', 'POST'])
@login_required
def analyze_article(article_id):
    """分析文章SEO"""
    article = Article.query.get_or_404(article_id)

    if article.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('articles.index'))

    analyzer = SeoAnalyzer()

    if request.method == 'POST':
        result = analyzer.analyze_article(article)
        return jsonify(result)

    # 显示分析结果
    result = analyzer.analyze_article(article)
    return render_template('seo/article_analysis.html',
                         article=article,
                         result=result)


@seo_bp.route('/analyze/page/<int:page_id>', methods=['GET', 'POST'])
@login_required
def analyze_page(page_id):
    """分析页面SEO"""
    page = Page.query.get_or_404(page_id)

    # 检查权限
    site = Site.query.get(page.site_id)
    if site.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('sites.pages', site_id=page.site_id))

    analyzer = SeoAnalyzer()

    if request.method == 'POST':
        result = analyzer.analyze_page(page)
        return jsonify(result)

    result = analyzer.analyze_page(page)
    return render_template('seo/page_analysis.html',
                         page=page,
                         result=result)


@seo_bp.route('/analyze/site/<int:site_id>', methods=['GET', 'POST'])
@login_required
def analyze_site(site_id):
    """分析站点SEO"""
    site = Site.query.get_or_404(site_id)

    if site.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('sites.index'))

    checker = TechnicalSeoChecker()

    if request.method == 'POST':
        result = checker.check_site(site)
        return jsonify(result)

    result = checker.check_site(site)
    return render_template('seo/site_analysis.html',
                         site=site,
                         result=result)


@seo_bp.route('/optimize/article/<int:article_id>', methods=['POST'])
@login_required
def optimize_article(article_id):
    """优化文章SEO"""
    article = Article.query.get_or_404(article_id)

    if article.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('articles.index'))

    optimizer = SeoOptimizer()

    try:
        result = optimizer.optimize_article(article)

        # 更新文章
        if result.get('meta_title'):
            article.meta_title = result['meta_title']
        if result.get('meta_description'):
            article.meta_description = result['meta_description']
        if result.get('suggestions'):
            article.content = result.get('content', article.content)

        db.session.commit()

        flash('SEO优化完成', 'success')
    except Exception as e:
        flash(f'优化失败: {str(e)}', 'danger')

    return redirect(url_for('seo.analyze_article', article_id=article_id))


@seo_bp.route('/keywords')
@login_required
def keywords():
    """关键词管理"""
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config.get('ITEMS_PER_PAGE', 20)
    site_id = request.args.get('site_id', type=int)

    query = Keyword.query.filter_by(user_id=current_user.id)

    if site_id:
        query = query.filter_by(site_id=site_id)

    pagination = query.order_by(Keyword.search_volume.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    keywords = pagination.items

    sites = Site.query.filter_by(user_id=current_user.id).all()

    return render_template('seo/keywords.html',
                         keywords=keywords,
                         pagination=pagination,
                         sites=sites,
                         current_site_id=site_id)


@seo_bp.route('/keywords/add', methods=['POST'])
@login_required
def add_keyword():
    """添加关键词"""
    keyword = request.form.get('keyword', '').strip()
    site_id = request.form.get('site_id', type=int)

    if not keyword:
        flash('请输入关键词', 'danger')
        return redirect(url_for('seo.keywords'))

    # 检查是否已存在
    existing = Keyword.query.filter_by(
        user_id=current_user.id,
        keyword=keyword
    ).first()

    if existing:
        flash('关键词已存在', 'warning')
        return redirect(url_for('seo.keywords'))

    new_keyword = Keyword(
        user_id=current_user.id,
        site_id=site_id,
        keyword=keyword
    )

    db.session.add(new_keyword)
    db.session.commit()

    flash('关键词添加成功', 'success')
    return redirect(url_for('seo.keywords'))


@seo_bp.route('/keywords/<int:keyword_id>/delete', methods=['POST'])
@login_required
def delete_keyword(keyword_id):
    """删除关键词"""
    keyword = Keyword.query.get_or_404(keyword_id)

    if keyword.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('seo.keywords'))

    db.session.delete(keyword)
    db.session.commit()

    flash('关键词已删除', 'success')
    return redirect(url_for('seo.keywords'))


@seo_bp.route('/settings/<int:site_id>', methods=['GET', 'POST'])
@login_required
def settings(site_id):
    """SEO设置"""
    site = Site.query.get_or_404(site_id)

    if site.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('sites.index'))

    seo_config = site.seo_config

    if request.method == 'POST':
        seo_config.default_title = request.form.get('default_title', '').strip()
        seo_config.default_description = request.form.get('default_description', '').strip()
        seo_config.default_keywords = request.form.get('default_keywords', '').strip()
        seo_config.allow_robots = request.form.get('allow_robots', 'on') == 'on'
        seo_config.enable_sitemap = request.form.get('enable_sitemap', 'on') == 'on'
        seo_config.sitemap_priority = float(request.form.get('sitemap_priority', 0.8))
        seo_config.enable_schema = request.form.get('enable_schema', 'on') == 'on'
        seo_config.schema_type = request.form.get('schema_type', 'Organization')
        seo_config.og_enabled = request.form.get('og_enabled', 'on') == 'on'
        seo_config.twitter_card_enabled = request.form.get('twitter_card_enabled', 'on') == 'on'

        db.session.commit()

        flash('SEO设置已保存', 'success')
        return redirect(url_for('seo.settings', site_id=site_id))

    return render_template('seo/settings.html', site=site, seo_config=seo_config)


@seo_bp.route('/check-robots/<int:site_id>')
@login_required
def check_robots(site_id):
    """检查robots.txt"""
    site = Site.query.get_or_404(site_id)

    if site.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('sites.index'))

    # 获取站点的robots.txt
    from app.services.robots_generator import RobotsGenerator
    generator = RobotsGenerator(site)
    robots_content = generator.generate()

    return render_template('seo/robots.html',
                         site=site,
                         robots_content=robots_content)
