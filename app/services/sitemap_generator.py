"""
SEO AIOS 站点地图生成器
Sitemap Generator Service
"""

import os
from datetime import datetime


class SitemapGenerator:
    """站点地图生成器"""

    def __init__(self, site):
        """
        初始化生成器

        Args:
            site: Site模型实例
        """
        self.site = site

    def generate(self):
        """
        生成站点地图

        Returns:
            站点地图文件路径
        """
        from app.models import Page, Article

        pages = Page.query.filter_by(
            site_id=self.site.id,
            status='published'
        ).all()

        articles = Article.query.filter_by(
            site_id=self.site.id,
            status='published'
        ).all()

        # 构建URL列表
        urls = []

        # 首页
        urls.append({
            'loc': self.site.domain or '/',
            'changefreq': 'daily',
            'priority': '1.0',
            'lastmod': datetime.utcnow().strftime('%Y-%m-%d')
        })

        # 页面
        for page in pages:
            if page.slug:
                loc = f"{self.site.domain.rstrip('/')}/{page.slug}"
            else:
                continue

            urls.append({
                'loc': loc,
                'changefreq': 'weekly',
                'priority': '0.8',
                'lastmod': (page.updated_at or page.created_at).strftime('%Y-%m-%d') if page.updated_at or page.created_at else None
            })

        # 文章
        for article in articles:
            loc = f"{self.site.domain.rstrip('/')}/articles/{article.slug}"

            urls.append({
                'loc': loc,
                'changefreq': 'monthly',
                'priority': '0.6',
                'lastmod': (article.updated_at or article.published_at or article.created_at).strftime('%Y-%m-%d') if article.updated_at or article.published_at or article.created_at else None
            })

        # 生成XML
        xml = self._generate_xml(urls)

        # 保存文件
        output_dir = self.site.output_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'output',
            str(self.site.id)
        )

        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, 'sitemap.xml')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml)

        return file_path

    def _generate_xml(self, urls):
        """生成XML内容"""
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

        for url in urls:
            xml += '  <url>\n'
            xml += f'    <loc>{self._escape_xml(url["loc"])}</loc>\n'

            if url.get('lastmod'):
                xml += f'    <lastmod>{url["lastmod"]}</lastmod>\n'

            xml += f'    <changefreq>{url["changefreq"]}</changefreq>\n'
            xml += f'    <priority>{url["priority"]}</priority>\n'
            xml += '  </url>\n'

        xml += '</urlset>'

        return xml

    def _escape_xml(self, text):
        """转义XML特殊字符"""
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&apos;')
        return text
