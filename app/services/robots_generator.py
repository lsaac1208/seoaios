"""
SEO AIOS Robots.txt生成器
Robots.txt Generator Service
"""

import os


class RobotsGenerator:
    """Robots.txt生成器"""

    def __init__(self, site):
        """
        初始化生成器

        Args:
            site: Site模型实例
        """
        self.site = site

    def generate(self):
        """
        生成robots.txt

        Returns:
            robots.txt内容
        """
        seo_config = self.site.seo_config

        lines = []

        # User-agent
        lines.append('User-agent: *')

        # Allow/Disallow
        if seo_config and not seo_config.allow_robots:
            lines.append('Disallow: /')
        else:
            lines.append('Allow: /')

        # Sitemap
        if self.site.domain:
            lines.append(f'Sitemap: {self.site.domain.rstrip("/")}/sitemap.xml')

        # 自定义规则
        if seo_config and seo_config.robots_txt:
            lines.append('')
            lines.append(seo_config.robots_txt)

        return '\n'.join(lines)

    def save(self):
        """
        保存robots.txt到文件

        Returns:
            文件路径
        """
        content = self.generate()

        output_dir = self.site.output_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'output',
            str(self.site.id)
        )

        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, 'robots.txt')

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return file_path
