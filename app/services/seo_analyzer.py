"""
SEO AIOS SEO分析服务
SEO Analyzer Service
"""

import re
from app.utils.helpers import calculate_keyword_density, calculate_readability, extract_keywords


class SeoAnalyzer:
    """SEO分析器"""

    def analyze_article(self, article):
        """
        分析文章SEO

        Args:
            article: Article模型实例

        Returns:
            分析结果字典
        """
        result = {
            'score': 0,
            'issues': [],
            'suggestions': [],
            'details': {}
        }

        # 基础检查
        checks = []

        # 1. 标题检查
        if article.title:
            checks.append({
                'name': 'title',
                'label': '标题',
                'passed': True,
                'message': f'标题长度: {len(article.title)}字符'
            })

            if len(article.title) > 60:
                result['issues'].append('标题过长（建议60字符以内）')
            if len(article.title) < 30:
                result['issues'].append('标题过短（建议30字符以上）')
        else:
            checks.append({
                'name': 'title',
                'label': '标题',
                'passed': False,
                'message': '缺少标题'
            })
            result['issues'].append('缺少标题')

        # 2. Meta描述检查
        if article.meta_description:
            checks.append({
                'name': 'meta_description',
                'label': 'Meta描述',
                'passed': True,
                'message': f'Meta描述长度: {len(article.meta_description)}字符'
            })

            if len(article.meta_description) > 160:
                result['issues'].append('Meta描述过长（建议160字符以内）')
            if len(article.meta_description) < 120:
                result['issues'].append('Meta描述过短（建议120字符以上）')
        else:
            checks.append({
                'name': 'meta_description',
                'label': 'Meta描述',
                'passed': False,
                'message': '缺少Meta描述'
            })
            result['issues'].append('缺少Meta描述')

        # 3. 内容检查
        content = article.content
        if content:
            word_count = len(content.split())
            checks.append({
                'name': 'content_length',
                'label': '内容长度',
                'passed': word_count >= 300,
                'message': f'字数: {word_count}'
            })

            if word_count < 300:
                result['issues'].append(f'内容过短（当前{word_count}字，建议300字以上）')

            # 4. 关键词密度分析
            primary_keyword = article.meta_keywords.split(',')[0].strip() if article.meta_keywords else ''

            if primary_keyword:
                keyword_density = calculate_keyword_density(content, primary_keyword)
                checks.append({
                    'name': 'keyword_density',
                    'label': '关键词密度',
                    'passed': 0.5 <= keyword_density <= 3.0,
                    'message': f'"{primary_keyword}" 密度: {keyword_density}%'
                })

                if keyword_density < 0.5:
                    result['issues'].append(f'关键词密度过低（当前{keyword_density}%，建议0.5-3%）')
                elif keyword_density > 3.0:
                    result['issues'].append(f'关键词密度过高（当前{keyword_density}%，建议0.5-3%）')

            # 5. 标题标签检查
            h1_count = len(re.findall(r'<h1[^>]*>(.*?)</h1>', content, re.I))
            h2_count = len(re.findall(r'<h2[^>]*>(.*?)</h2>', content, re.I))

            checks.append({
                'name': 'headings',
                'label': '标题标签',
                'passed': h1_count >= 1,
                'message': f'H1: {h1_count}, H2: {h2_count}'
            })

            if h1_count == 0:
                result['issues'].append('缺少H1标题标签')

            # 6. 图片Alt检查
            img_with_alt = len(re.findall(r'<img[^>]+alt=["\']([^"\']+)["\']', content, re.I))
            img_without_alt = len(re.findall(r'<img(?![^>]*alt)[^>]*>', content, re.I))

            checks.append({
                'name': 'images_alt',
                'label': '图片Alt',
                'passed': img_without_alt == 0,
                'message': f'有Alt: {img_with_alt}, 无Alt: {img_without_alt}'
            })

            if img_without_alt > 0:
                result['issues'].append(f'{img_without_alt}个图片缺少Alt属性')

            # 7. 可读性检查
            readability = calculate_readability(content)
            checks.append({
                'name': 'readability',
                'label': '可读性',
                'passed': readability >= 60,
                'message': f'得分: {readability}'
            })

            if readability < 60:
                result['issues'].append(f'可读性较差（得分{readability}，建议60分以上）')

            # 8. 内部链接检查
            internal_links = len(re.findall(r'<a[^>]+href=["\']https?://[^"\']+["\']', content, re.I))

            checks.append({
                'name': 'internal_links',
                'label': '内部链接',
                'passed': internal_links >= 2,
                'message': f'链接数: {internal_links}'
            })

            if internal_links < 2:
                result['issues'].append('建议添加更多内部链接')

        else:
            checks.append({
                'name': 'content',
                'label': '内容',
                'passed': False,
                'message': '文章内容为空'
            })
            result['issues'].append('文章内容为空')

        # 计算得分
        passed_count = sum(1 for c in checks if c['passed'])
        total_count = len(checks)
        result['score'] = int((passed_count / total_count * 100)) if total_count > 0 else 0

        result['details']['checks'] = checks

        # 生成建议
        if result['score'] >= 80:
            result['suggestions'].append('SEO表现良好，继续保持！')
        elif result['score'] >= 60:
            result['suggestions'].append('SEO表现一般，建议修复以上问题以提升排名')
        else:
            result['suggestions'].append('SEO表现较差，建议优先解决以上问题')

        return result

    def analyze_page(self, page):
        """
        分析页面SEO

        Args:
            page: Page模型实例

        Returns:
            分析结果字典
        """
        result = {
            'score': 0,
            'issues': [],
            'suggestions': []
        }

        checks = []

        # 标题检查
        if page.title:
            checks.append({'passed': True, 'message': f'标题长度: {len(page.title)}字符'})
        else:
            checks.append({'passed': False, 'message': '缺少标题'})
            result['issues'].append('缺少标题')

        # Meta描述检查
        if page.meta_description:
            checks.append({'passed': True, 'message': f'Meta描述长度: {len(page.meta_description)}字符'})
        else:
            checks.append({'passed': False, 'message': '缺少Meta描述'})
            result['issues'].append('缺少Meta描述')

        # 计算得分
        passed_count = sum(1 for c in checks if c['passed'])
        total_count = len(checks)
        result['score'] = int((passed_count / total_count * 100)) if total_count > 0 else 0

        return result

    def analyze_keyword_position(self, keyword, site):
        """
        分析关键词排名

        Args:
            keyword: 关键词
            site: Site实例

        Returns:
            排名信息
        """
        # TODO: 集成搜索引擎查询API
        return {
            'keyword': keyword,
            'position': 0,
            'search_volume': 0,
            'difficulty': 0,
            'last_checked': None
        }
