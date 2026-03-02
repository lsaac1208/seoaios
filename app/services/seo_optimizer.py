"""
SEO AIOS SEO优化服务
SEO Optimizer Service
"""

from app.utils.helpers import generate_meta_description, extract_keywords, calculate_keyword_density


class SeoOptimizer:
    """SEO优化器"""

    def __init__(self):
        pass

    def optimize_article(self, article):
        """
        优化文章SEO

        Args:
            article: Article模型实例

        Returns:
            优化建议字典
        """
        result = {
            'meta_title': None,
            'meta_description': None,
            'suggestions': [],
            'content': None
        }

        # 1. 优化标题
        if not article.meta_title or len(article.meta_title) > 60:
            # 生成新标题
            title = article.title
            if len(title) > 60:
                title = title[:57] + '...'
            result['meta_title'] = title

        # 2. 优化Meta描述
        if not article.meta_description:
            result['meta_description'] = generate_meta_description(article.content, 160)

        # 3. 内容优化建议
        content = article.content

        # 提取关键词
        keywords = extract_keywords(content, max_keywords=5)

        if keywords:
            result['suggestions'].append(f'建议使用以下关键词: {", ".join(keywords)}')

            # 检查关键词密度
            primary_keyword = keywords[0]
            density = calculate_keyword_density(content, primary_keyword)

            if density < 0.5:
                result['suggestions'].append(
                    f'关键词"{primary_keyword}"密度较低，建议在文章中适当增加出现次数'
                )
            elif density > 3.0:
                result['suggestions'].append(
                    f'关键词"{primary_keyword}"密度过高，建议适当减少'
                )

        # 4. 检查H1标签
        import re
        if '<h1' not in content.lower():
            result['suggestions'].append('建议添加H1标题标签')

        # 5. 检查图片Alt
        img_without_alt = len(re.findall(r'<img(?![^>]*alt)[^>]*>', content, re.I))
        if img_without_alt > 0:
            result['suggestions'].append(f'有{img_without_alt}个图片缺少Alt属性，建议添加')

        return result

    def optimize_page(self, page):
        """
        优化页面SEO

        Args:
            page: Page模型实例

        Returns:
            优化建议字典
        """
        result = {}

        # 优化Meta标签
        if not page.meta_title:
            result['meta_title'] = page.title[:60]

        if not page.meta_description:
            result['meta_description'] = generate_meta_description(page.content or '', 160)

        return result
