"""
SEO AIOS 高级SEO分析服务
Advanced SEO Analysis Service
"""

import re
from typing import Dict, List, Optional
from collections import Counter


class AdvancedSEOChecker:
    """
    高级SEO检查器
    提供全面的SEO分析和优化建议
    """

    def __init__(self):
        self.check_rules = self._init_check_rules()

    def _init_check_rules(self) -> Dict:
        """初始化SEO检查规则"""
        return {
            'title': {
                'name': '标题标签',
                'checks': [
                    {'rule': 'exists', 'msg': '缺少标题标签'},
                    {'rule': 'length', 'min': 10, 'max': 60, 'msg': '标题长度应在10-60个字符之间'},
                ]
            },
            'meta_description': {
                'name': 'Meta描述',
                'checks': [
                    {'rule': 'exists', 'msg': '缺少Meta描述'},
                    {'rule': 'length', 'min': 50, 'max': 160, 'msg': 'Meta描述长度应在50-160个字符之间'},
                ]
            },
            'meta_keywords': {
                'name': 'Meta关键词',
                'checks': [
                    {'rule': 'exists', 'msg': '缺少Meta关键词'},
                    {'rule': 'count', 'min': 3, 'max': 10, 'msg': '建议设置3-10个关键词'},
                ]
            },
            'headings': {
                'name': '标题结构',
                'checks': [
                    {'rule': 'has_h1', 'msg': '缺少H1标签'},
                    {'rule': 'has_h2', 'msg': '缺少H2标签'},
                ]
            },
            'content': {
                'name': '内容质量',
                'checks': [
                    {'rule': 'length', 'min': 300, 'msg': '内容过短，建议至少300字'},
                    {'rule': 'keyword_density', 'min': 0.5, 'max': 3, 'msg': '关键词密度应在0.5%-3%之间'},
                ]
            },
            'links': {
                'name': '链接优化',
                'checks': [
                    {'rule': 'has_internal', 'msg': '缺少内链'},
                ]
            },
            'images': {
                'name': '图片优化',
                'checks': [
                    {'rule': 'has_alt', 'msg': '图片缺少alt属性'},
                ]
            },
            'technical': {
                'name': '技术SEO',
                'checks': [
                    {'rule': 'has_schema', 'msg': '缺少结构化数据'},
                    {'rule': 'has_canonical', 'msg': '缺少canonical标签'},
                ]
            }
        }

    def analyze_article(self, article) -> Dict:
        """
        分析文章SEO

        Args:
            article: 文章对象

        Returns:
            SEO分析报告
        """
        # 提取内容
        title = getattr(article, 'title', '') or ''
        meta_title = getattr(article, 'meta_title', '') or ''
        meta_description = getattr(article, 'meta_description', '') or ''
        meta_keywords = getattr(article, 'meta_keywords', '') or ''
        content = getattr(article, 'content', '') or ''

        # 执行各项检查
        results = {
            'score': 0,
            'max_score': 100,
            'checks': {},
            'issues': [],
            'suggestions': [],
            'keywords': self._extract_keywords(meta_keywords, content),
            'readability': self._analyze_readability(content),
            'structure': self._analyze_structure(content)
        }

        # 标题检查
        title_result = self._check_title(title or meta_title)
        results['checks']['title'] = title_result

        # Meta描述检查
        desc_result = self._check_meta_description(meta_description)
        results['checks']['meta_description'] = desc_result

        # 关键词检查
        kw_result = self._check_keywords(meta_keywords, content)
        results['checks']['keywords'] = kw_result

        # 内容检查
        content_result = self._check_content(content)
        results['checks']['content'] = content_result

        # 结构检查
        structure_result = self._check_structure(content)
        results['checks']['structure'] = structure_result

        # 计算总分
        results['score'] = self._calculate_score(results['checks'])

        # 生成建议
        results['suggestions'] = self._generate_suggestions(results['checks'])

        return results

    def _check_title(self, title: str) -> Dict:
        """检查标题"""
        result = {'passed': False, 'score': 0, 'issues': []}

        if not title:
            result['issues'].append('缺少标题标签')
            return result

        # 长度检查
        length = len(title)
        if length < 10:
            result['issues'].append(f'标题过短 ({length}字符)，建议10-60字符')
        elif length > 60:
            result['issues'].append(f'标题过长 ({length}字符)，建议10-60字符')
        else:
            result['passed'] = True
            result['score'] = 10

        return result

    def _check_meta_description(self, description: str) -> Dict:
        """检查Meta描述"""
        result = {'passed': False, 'score': 0, 'issues': []}

        if not description:
            result['issues'].append('缺少Meta描述')
            return result

        length = len(description)
        if length < 50:
            result['issues'].append(f'Meta描述过短 ({length}字符)，建议50-160字符')
        elif length > 160:
            result['issues'].append(f'Meta描述过长 ({length}字符)，建议50-160字符')
        else:
            result['passed'] = True
            result['score'] = 10

        return result

    def _check_keywords(self, meta_keywords: str, content: str) -> Dict:
        """检查关键词"""
        result = {'passed': False, 'score': 0, 'issues': []}

        keywords = [k.strip() for k in meta_keywords.split(',') if k.strip()]

        if not keywords:
            result['issues'].append('未设置Meta关键词')
            return result

        if len(keywords) < 3:
            result['issues'].append(f'关键词数量不足 ({len(keywords)}个)，建议3-10个')
        else:
            result['passed'] = True
            result['score'] = 10

        # 检查关键词密度
        if content and keywords:
            main_keyword = keywords[0]
            density = (content.lower().count(main_keyword.lower()) / len(content.split())) * 100
            result['keyword_density'] = round(density, 2)

            if density < 0.5:
                result['issues'].append(f'主要关键词密度过低 ({density}%)，建议0.5%-3%')
            elif density > 3:
                result['issues'].append(f'主要关键词密度过高 ({density}%)，建议0.5%-3%')

        return result

    def _check_content(self, content: str) -> Dict:
        """检查内容质量"""
        result = {'passed': False, 'score': 0, 'issues': []}

        if not content:
            result['issues'].append('内容为空')
            return result

        # 长度检查
        word_count = len(content)
        if word_count < 300:
            result['issues'].append(f'内容过短 ({word_count}字符)，建议至少300字符')
        elif word_count >= 1500:
            result['passed'] = True
            result['score'] = 15
        else:
            result['passed'] = True
            result['score'] = 10

        # 检查段落
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        result['paragraphs'] = len(paragraphs)

        if len(paragraphs) < 3:
            result['issues'].append('段落过少，建议至少3个段落')

        return result

    def _check_structure(self, content: str) -> Dict:
        """检查内容结构"""
        result = {'passed': False, 'score': 0, 'issues': [], 'headings': {}}

        # 提取标题
        h1_count = len(re.findall(r'^#\s+(.+)$', content, re.MULTILINE))
        h2_count = len(re.findall(r'^##\s+(.+)$', content, re.MULTILINE))
        h3_count = len(re.findall(r'^###\s+(.+)$', content, re.MULTILINE))

        result['headings'] = {
            'h1': h1_count,
            'h2': h2_count,
            'h3': h3_count
        }

        if h1_count == 0:
            result['issues'].append('缺少H1标题')
        elif h2_count == 0:
            result['issues'].append('缺少H2标题')
        else:
            result['passed'] = True
            result['score'] = 10

        # 检查列表
        ul_count = content.count('- ') + content.count('* ')
        result['list_items'] = ul_count

        return result

    def _extract_keywords(self, meta_keywords: str, content: str) -> Dict:
        """提取关键词"""
        keywords = [k.strip() for k in meta_keywords.split(',') if k.strip()]

        # 提取内容中的高频词
        words = re.findall(r'[\u4e00-\u9fff]+', content)
        word_freq = Counter(words)
        top_words = word_freq.most_common(10)

        return {
            'target_keywords': keywords,
            'content_keywords': [w[0] for w in top_words],
            'overlap': [kw for kw in keywords if any(kw in w[0] for w in top_words)]
        }

    def _analyze_readability(self, content: str) -> Dict:
        """分析可读性"""
        if not content:
            return {'score': 0, 'level': 'unknown'}

        # 句子数
        sentences = len(re.findall(r'[。！？]', content))

        # 段落数
        paragraphs = len([p for p in content.split('\n\n') if p.strip()])

        # 平均句子长度
        words = len(content)
        avg_sentence_length = words / sentences if sentences else 0

        # 计算可读性分数
        if avg_sentence_length < 20:
            score = 90
            level = '简单'
        elif avg_sentence_length < 35:
            score = 75
            level = '中等'
        else:
            score = 60
            level = '困难'

        return {
            'score': score,
            'level': level,
            'avg_sentence_length': round(avg_sentence_length, 1),
            'sentences': sentences,
            'paragraphs': paragraphs
        }

    def _analyze_structure(self, content: str) -> Dict:
        """分析内容结构"""
        # 提取标题
        h1_titles = re.findall(r'^#\s+(.+)$', content, re.MULTILINE)
        h2_titles = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        h3_titles = re.findall(r'^###\s+(.+)$', content, re.MULTILINE)

        # 检查是否有明确的结构
        has_intro = any('介绍' in t or '前言' in t or '概述' in t for t in h2_titles)
        has_conclusion = any('总结' in t or '结论' in t for t in h2_titles)

        return {
            'h1_count': len(h1_titles),
            'h2_count': len(h2_titles),
            'h3_count': len(h3_titles),
            'has_intro': has_intro,
            'has_conclusion': has_conclusion,
            'structure_score': self._calculate_structure_score(len(h2_titles), has_intro, has_conclusion)
        }

    def _calculate_structure_score(self, h2_count: int, has_intro: bool, has_conclusion: bool) -> int:
        """计算结构分数"""
        score = 0

        if h2_count >= 3:
            score += 30
        elif h2_count >= 1:
            score += 20

        if has_intro:
            score += 35
        if has_conclusion:
            score += 35

        return min(score, 100)

    def _calculate_score(self, checks: Dict) -> int:
        """计算总分"""
        total = 0

        # 标题 (10分)
        if checks.get('title', {}).get('passed'):
            total += 10

        # Meta描述 (10分)
        if checks.get('meta_description', {}).get('passed'):
            total += 10

        # 关键词 (10分)
        if checks.get('keywords', {}).get('passed'):
            total += 10

        # 内容 (15分)
        if checks.get('content', {}).get('passed'):
            total += 15

        # 结构 (10分)
        if checks.get('structure', {}).get('passed'):
            total += 10

        # 可读性 (10分)
        total += 10  # 基础分

        # 技术项 (25分)
        total += 25  # 基础分

        return min(total, 100)

    def _generate_suggestions(self, checks: Dict) -> List[str]:
        """生成优化建议"""
        suggestions = []

        for check_name, result in checks.items():
            if not result.get('passed'):
                for issue in result.get('issues', []):
                    suggestions.append(f"【{check_name}】{issue}")

        return suggestions


class SEOReportGenerator:
    """SEO报告生成器"""

    def generate_report(self, analysis: Dict, article_title: str = '') -> str:
        """
        生成SEO报告

        Args:
            analysis: 分析结果
            article_title: 文章标题

        Returns:
            格式化的报告
        """
        score = analysis.get('score', 0)
        grade = self._get_grade(score)

        report = f"""
# SEO分析报告

## 总体评分
- **总分**: {score}/100
- **等级**: {grade}

## 检查结果
"""

        for check_name, result in analysis.get('checks', {}).items():
            status = "✅ 通过" if result.get('passed') else "❌ 未通过"
            report += f"\n### {check_name} - {status}\n"
            if result.get('issues'):
                for issue in result['issues']:
                    report += f"- {issue}\n"

        if analysis.get('suggestions'):
            report += "\n## 优化建议\n"
            for i, suggestion in enumerate(analysis['suggestions'], 1):
                report += f"{i}. {suggestion}\n"

        return report

    def _get_grade(self, score: int) -> str:
        """根据分数获取等级"""
        if score >= 90:
            return 'A+ (优秀)'
        elif score >= 80:
            return 'A (良好)'
        elif score >= 70:
            return 'B (中等)'
        elif score >= 60:
            return 'C (及格)'
        else:
            return 'D (需改进)'
