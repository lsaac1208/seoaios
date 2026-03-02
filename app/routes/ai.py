"""
SEO AIOS AI功能路由
AI Features Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Site, Article, AiConfig, Keyword
from app.services.content_generator import ContentGenerator
from app.services.content_rewriter import ContentRewriter
from app.services.crawler import WebCrawler

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/content/generate', methods=['GET', 'POST'])
@login_required
def generate_content():
    """AI生成内容"""
    if request.method == 'POST':
        site_id = request.form.get('site_id', type=int)
        topic = request.form.get('topic', '').strip()
        keywords = request.form.get('keywords', '').strip()
        length = request.form.get('length', type=int, default=1500)
        style = request.form.get('style', 'informative')

        if not site_id or not topic:
            flash('请填写主题', 'danger')
            return redirect(url_for('ai.generate_content'))

        site = Site.query.get_or_404(site_id)
        if site.user_id != current_user.id:
            flash('无权操作', 'danger')
            return redirect(url_for('ai.generate_content'))

        try:
            ai_config = site.ai_config or AiConfig(provider='openai')
            generator = ContentGenerator(ai_config)

            result = generator.generate(
                topic=topic,
                keywords=keywords.split(',') if keywords else [],
                length=length,
                style=style
            )

            return render_template('ai/generate_result.html',
                               site=site,
                               topic=topic,
                               result=result)

        except Exception as e:
            flash(f'生成失败: {str(e)}', 'danger')

    sites = Site.query.filter_by(user_id=current_user.id).all()
    keywords = Keyword.query.filter_by(user_id=current_user.id).limit(10).all()

    return render_template('ai/generate.html', sites=sites, keywords=keywords)


@ai_bp.route('/content/rewrite', methods=['GET', 'POST'])
@login_required
def rewrite_content():
    """AI改写内容"""
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        rewrite_type = request.form.get('rewrite_type', 'semantic')
        level = request.form.get('level', type=int, default=3)

        if not content:
            flash('请输入要改写的内容', 'danger')
            return redirect(url_for('ai.rewrite_content'))

        try:
            # 使用默认配置
            ai_config = AiConfig(provider='openai')
            rewriter = ContentRewriter(ai_config)

            result = rewriter.rewrite(
                content=content,
                rewrite_type=rewrite_type,
                level=level
            )

            return render_template('ai/rewrite_result.html',
                               original_content=content,
                               result=result)

        except Exception as e:
            flash(f'改写失败: {str(e)}', 'danger')

    return render_template('ai/rewrite.html')


@ai_bp.route('/content/save-article', methods=['POST'])
@login_required
def save_article():
    """保存生成的article为文章"""
    site_id = request.form.get('site_id', type=int)
    title = request.form.get('title', '').strip()
    content = request.form.get('content', '').strip()
    meta_title = request.form.get('meta_title', '').strip()
    meta_description = request.form.get('meta_description', '').strip()
    meta_keywords = request.form.get('meta_keywords', '').strip()

    if not site_id or not title or not content:
        return jsonify({'success': False, 'message': '请填写必填项'})

    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作'})

    # 生成slug
    from app.utils.helpers import slugify
    slug = slugify(title)

    # 确保slug唯一
    base_slug = slug
    counter = 1
    while Article.query.filter_by(site_id=site_id, slug=slug).first():
        slug = f'{base_slug}-{counter}'
        counter += 1

    article = Article(
        site_id=site_id,
        user_id=current_user.id,
        title=title,
        slug=slug,
        content=content,
        excerpt=content[:200],
        meta_title=meta_title,
        meta_description=meta_description,
        meta_keywords=meta_keywords,
        status='draft'
    )

    db.session.add(article)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': '文章已保存',
        'article_id': article.id
    })


@ai_bp.route('/crawl', methods=['GET', 'POST'])
@login_required
def crawl():
    """内容抓取"""
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        site_id = request.form.get('site_id', type=int)
        max_depth = request.form.get('max_depth', type=int, default=2)

        if not url:
            flash('请输入要抓取的URL', 'danger')
            return redirect(url_for('ai.crawl'))

        try:
            crawler = WebCrawler()
            result = crawler.crawl_url(url, max_depth=max_depth)

            return render_template('ai/crawl_result.html',
                               url=url,
                               result=result)

        except Exception as e:
            flash(f'抓取失败: {str(e)}', 'danger')

    sites = Site.query.filter_by(user_id=current_user.id).all()
    return render_template('ai/crawl.html', sites=sites)


@ai_bp.route('/crawl-and-rewrite', methods=['POST'])
@login_required
def crawl_and_rewrite():
    """抓取并改写"""
    url = request.form.get('url', '').strip()
    site_id = request.form.get('site_id', type=int)

    if not url or not site_id:
        flash('请填写URL和目标站点', 'danger')
        return redirect(url_for('ai.crawl'))

    site = Site.query.get_or_404(site_id)
    if site.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('ai.crawl'))

    try:
        # 抓取内容
        crawler = WebCrawler()
        crawl_result = crawler.crawl_url(url)

        if not crawl_result.get('content'):
            flash('无法获取内容', 'danger')
            return redirect(url_for('ai.crawl'))

        # 改写内容
        ai_config = site.ai_config or AiConfig(provider='openai')
        rewriter = ContentRewriter(ai_config)
        rewritten = rewriter.rewrite(crawl_result['content'], rewrite_type='semantic')

        # 保存为文章
        from app.utils.helpers import slugify
        title = crawl_result.get('title', 'Untitled')
        slug = slugify(title)

        article = Article(
            site_id=site_id,
            user_id=current_user.id,
            title=title,
            slug=slug,
            content=rewritten,
            excerpt=rewritten[:200],
            source_url=url,
            source_name=crawl_result.get('domain'),
            is_rewritten=True,
            original_content=crawl_result['content'],
            status='draft'
        )

        db.session.add(article)
        db.session.commit()

        flash('内容抓取并改写成功', 'success')
        return redirect(url_for('articles.edit', article_id=article.id))

    except Exception as e:
        flash(f'处理失败: {str(e)}', 'danger')
        return redirect(url_for('ai.crawl'))


@ai_bp.route('/settings/<int:site_id>', methods=['GET', 'POST'])
@login_required
def settings(site_id):
    """AI配置"""
    site = Site.query.get_or_404(site_id)

    if site.user_id != current_user.id:
        flash('无权操作', 'danger')
        return redirect(url_for('sites.index'))

    ai_config = site.ai_config

    if request.method == 'POST':
        ai_config.provider = request.form.get('provider', 'openai')

        # OpenAI配置
        if request.form.get('openai_api_key'):
            ai_config.openai_api_key = request.form.get('openai_api_key')
        ai_config.openai_api_base = request.form.get('openai_api_base', '').strip()
        ai_config.openai_model = request.form.get('openai_model', 'gpt-3.5-turbo')

        # Anthropic配置
        if request.form.get('anthropic_api_key'):
            ai_config.anthropic_api_key = request.form.get('anthropic_api_key')
        ai_config.anthropic_model = request.form.get('anthropic_model', 'claude-3-haiku-20240307')

        # 内容生成配置
        ai_config.default_article_length = int(request.form.get('default_article_length', 1500))
        ai_config.default_title_length = int(request.form.get('default_title_length', 60))
        ai_config.default_description_length = int(request.form.get('default_description_length', 160))
        ai_config.temperature = float(request.form.get('temperature', 0.7))
        ai_config.rewrite_style = request.form.get('rewrite_style', 'semantic')
        ai_config.rewrite_level = int(request.form.get('rewrite_level', 3))

        db.session.commit()

        flash('AI配置已保存', 'success')
        return redirect(url_for('ai.settings', site_id=site_id))

    return render_template('ai/settings.html', site=site, ai_config=ai_config)


@ai_bp.route('/batch/generate', methods=['GET', 'POST'])
@login_required
def batch_generate():
    """批量生成内容"""
    if request.method == 'POST':
        site_id = request.form.get('site_id', type=int)
        keywords_text = request.form.get('keywords', '').strip()
        count = request.form.get('count', type=int, default=5)

        if not site_id or not keywords_text:
            flash('请填写关键词', 'danger')
            return redirect(url_for('ai.batch_generate'))

        keywords = [k.strip() for k in keywords_text.split('\n') if k.strip()]

        # 创建批量任务
        from app.models import Task
        task = Task(
            user_id=current_user.id,
            site_id=site_id,
            name=f'批量生成{count}篇文章',
            task_type='generate',
            config={'keywords': keywords[:count]},
            status='pending'
        )

        db.session.add(task)
        db.session.commit()

        # TODO: 触发Celery任务
        flash('批量生成任务已创建', 'success')
        return redirect(url_for('tasks.detail', task_id=task.id))

    sites = Site.query.filter_by(user_id=current_user.id).all()
    keywords = Keyword.query.filter_by(user_id=current_user.id).limit(20).all()

    return render_template('ai/batch_generate.html', sites=sites, keywords=keywords)
