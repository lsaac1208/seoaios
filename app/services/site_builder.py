"""
SEO AIOS 站点构建服务
Site Builder Service
"""

import os
import shutil
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from flask import current_app


class SiteBuilder:
    """站点构建器"""

    def __init__(self, site):
        """
        初始化构建器

        Args:
            site: Site模型实例
        """
        self.site = site
        self.output_dir = current_app.config.get('OUTPUT_DIR', 'output')
        self.templates_dir = current_app.config.get('TEMPLATES_DIR', 'templates/site_templates')

    def build(self):
        """
        构建站点

        Returns:
            输出目录路径
        """
        # 创建输出目录
        output_path = os.path.join(self.output_dir, str(self.site.id))
        os.makedirs(output_path, exist_ok=True)

        # 获取模板
        template_name = self.site.template or 'default'
        template_path = os.path.join(self.templates_dir, template_name)

        if not os.path.exists(template_path):
            template_path = os.path.join(self.templates_dir, 'default')

        # 初始化Jinja2
        env = Environment(
            loader=FileSystemLoader(template_path),
            autoescape=select_autoescape(['html', 'xml'])
        )

        # 添加自定义过滤器
        env.filters['slugify'] = self._slugify
        env.filters['domain'] = self._domain

        # 生成首页
        self._generate_homepage(env, output_path)

        # 生成页面
        self._generate_pages(env, output_path)

        # 生成文章页面
        self._generate_articles(env, output_path)

        # 生成sitemap
        self._generate_sitemap(output_path)

        # 生成robots.txt
        self._generate_robots(output_path)

        return output_path

    def _generate_homepage(self, env, output_path):
        """生成首页"""
        from app.models import Page, Article

        # 获取首页
        home_page = Page.query.filter_by(
            site_id=self.site.id,
            page_type='home'
        ).first()

        # 获取最新文章
        recent_articles = Article.query.filter_by(
            site_id=self.site.id,
            status='published'
        ).order_by(Article.published_at.desc()).limit(10).all()

        # 渲染模板
        try:
            template = env.get_template('home.html')
        except:
            try:
                template = env.get_template('index.html')
            except:
                template = env.get_template('page.html')

        content = template.render(
            site=self.site,
            page=home_page,
            articles=recent_articles,
            pages=Page.query.filter_by(site_id=self.site.id, status='published').all(),
            now=datetime.utcnow()
        )

        # 写入文件
        with open(os.path.join(output_path, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(content)

    def _generate_pages(self, env, output_path):
        """生成页面"""
        from app.models import Page

        pages = Page.query.filter_by(
            site_id=self.site.id,
            status='published'
        ).all()

        try:
            template = env.get_template('page.html')
        except:
            template = env.get_template('default.html')

        for page in pages:
            content = template.render(
                site=self.site,
                page=page,
                pages=pages,
                now=datetime.utcnow()
            )

            # 根据slug确定文件名
            if page.slug:
                page_dir = os.path.join(output_path, page.slug)
                os.makedirs(page_dir, exist_ok=True)
                with open(os.path.join(page_dir, 'index.html'), 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                with open(os.path.join(output_path, 'index.html'), 'w', encoding='utf-8') as f:
                    f.write(content)

    def _generate_articles(self, env, output_path):
        """生成文章页面"""
        from app.models import Article

        articles = Article.query.filter_by(
            site_id=self.site.id,
            status='published'
        ).all()

        # 创建文章目录
        articles_dir = os.path.join(output_path, 'articles')
        os.makedirs(articles_dir, exist_ok=True)

        try:
            template = env.get_template('article.html')
        except:
            template = env.get_template('post.html')

        for article in articles:
            content = template.render(
                site=self.site,
                article=article,
                now=datetime.utcnow()
            )

            # 生成静态文件
            file_path = os.path.join(articles_dir, f'{article.slug}.html')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

    def _generate_sitemap(self, output_path):
        """生成站点地图"""
        from app.models import Page, Article

        pages = Page.query.filter_by(
            site_id=self.site.id,
            status='published'
        ).all()

        articles = Article.query.filter_by(
            site_id=self.site.id,
            status='published'
        ).all()

        urls = []

        # 首页
        urls.append({
            'loc': self.site.domain or '/',
            'changefreq': 'daily',
            'priority': '1.0'
        })

        # 页面
        for page in pages:
            if page.slug:
                urls.append({
                    'loc': f'{self.site.domain}/{page.slug}',
                    'changefreq': 'weekly',
                    'priority': '0.8'
                })

        # 文章
        for article in articles:
            urls.append({
                'loc': f'{self.site.domain}/articles/{article.slug}',
                'changefreq': 'monthly',
                'priority': '0.6'
            })

        # 生成XML
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

        for url in urls:
            xml += '  <url>\n'
            xml += f'    <loc>{url["loc"]}</loc>\n'
            xml += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
            xml += f'    <priority>{url["priority"]}</priority>\n'
            xml += '  </url>\n'

        xml += '</urlset>'

        with open(os.path.join(output_path, 'sitemap.xml'), 'w', encoding='utf-8') as f:
            f.write(xml)

    def _generate_robots(self, output_path):
        """生成robots.txt"""
        from app.models import SeoConfig

        seo_config = self.site.seo_config

        content = "User-agent: *\n"

        if seo_config and not seo_config.allow_robots:
            content += "Disallow: /\n"
        else:
            content += "Allow: /\n"
            content += f"Sitemap: {self.site.domain}/sitemap.xml\n"

        with open(os.path.join(output_path, 'robots.txt'), 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def _slugify(text):
        """slugify过滤器"""
        import re
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text

    @staticmethod
    def _domain(url):
        """提取域名"""
        from urllib.parse import urlparse
        if url:
            return urlparse(url).netloc
        return ''
