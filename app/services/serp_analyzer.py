"""
SEO AIOS SERP分析服务
SERP Analysis Service
借鉴 SEO Writing.ai 的 SERP 分析功能
"""

import requests
import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup


class SERPAnalyzer:
    """
    SERP (搜索引擎结果页面) 分析器
    分析竞争对手排名，优化内容策略
    """

    def __init__(self, api_key: str = None):
        """
        初始化SERP分析器

        Args:
            api_key: 可选的API密钥 (DataForSEO, SerpApi等)
        """
        self.api_key = api_key
        self.search_engine = 'baidu'  # 默认百度，可切换google

    def analyze_keyword(self, keyword: str, num_results: int = 10) -> Dict:
        """
        分析关键词的SERP

        Args:
            keyword: 目标关键词
            num_results: 分析结果数量

        Returns:
            SERP分析报告
        """
        results = self._fetch_serp(keyword, num_results)

        if not results:
            return {'error': 'Failed to fetch SERP results'}

        analysis = {
            'keyword': keyword,
            'search_engine': self.search_engine,
            'total_results': len(results),
            'results': results,
            'analysis': self._analyze_results(results),
            'content_opportunities': self._find_content_opportunities(results),
            'recommended_length': self._estimate_ideal_length(results)
        }

        return analysis

    def _fetch_serp(self, keyword: str, num_results: int) -> List[Dict]:
        """获取SERP结果"""
        # 优先使用API
        if self.api_key:
            return self._fetch_via_api(keyword, num_results)

        # 否则使用爬虫
        return self._scrape_serp(keyword, num_results)

    def _fetch_via_api(self, keyword: str, num_results: int) -> List[Dict]:
        """通过API获取SERP结果"""
        # 这里可以集成 DataForSEO, SerpApi 等服务
        # 示例使用 DataForSEO API
        url = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"

        payload = [{
            "keyword": keyword,
            "language_code": "zh-CN",
            "location_code": 2012,  # 中国
            "device": "desktop",
            "num_results": num_results
        }]

        headers = {
            'Authorization': f'Basic {self.api_key}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            data = response.json()

            results = []
            if data.get('tasks'):
                for task in data['tasks']:
                    if task.get('result'):
                        for item in task['result'][0]['items'][:num_results]:
                            results.append({
                                'title': item.get('title', ''),
                                'url': item.get('url', ''),
                                'snippet': item.get('snippet', ''),
                                'rank': item.get('rank_group', 0) + 1
                            })

            return results

        except Exception as e:
            # API失败时回退到爬虫
            return self._scrape_serp(keyword, num_results)

    def _scrape_serp(self, keyword: str, num_results: int) -> List[Dict]:
        """爬取SERP结果 (以百度为例)"""
        results = []

        try:
            if self.search_engine == 'baidu':
                url = f"https://www.baidu.com/s?wd={keyword}&pn={(num_results // 10) * 10}"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')

                # 百度结果解析
                for result in soup.select('.result')[:num_results]:
                    title_elem = result.select_one('.t')
                    snippet_elem = result.select_one('.c-abstract')
                    url_elem = result.select_one('a')

                    if title_elem:
                        results.append({
                            'title': title_elem.get_text(strip=True),
                            'url': url_elem.get('href', '') if url_elem else '',
                            'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                            'rank': len(results) + 1
                        })

        except Exception as e:
            # 如果爬虫失败，返回模拟数据用于测试
            results = self._get_mock_results(keyword, num_results)

        return results

    def _get_mock_results(self, keyword: str, num_results: int) -> List[Dict]:
        """返回模拟结果（用于测试）"""
        return [
            {
                'title': f'{keyword} - 最佳解决方案 | 示例站点A',
                'url': f'https://example-a.com/{keyword}',
                'snippet': f'深入分析{keyword}的完整指南，包含实用技巧和最佳实践。',
                'rank': i + 1
            }
            for i in range(min(num_results, 5))
        ]

    def _analyze_results(self, results: List[Dict]) -> Dict:
        """分析SERP结果特征"""
        titles = [r.get('title', '') for r in results]
        snippets = [r.get('snippet', '') for r in results]

        # 提取常见词汇
        common_words = self._extract_common_words(titles + snippets)

        # 分析内容类型
        content_types = self._classify_content_type(results)

        # 分析标题模式
        title_patterns = self._analyze_title_patterns(titles)

        return {
            'common_keywords': common_words[:10],
            'content_types': content_types,
            'title_patterns': title_patterns,
            'avg_title_length': sum(len(t) for t in titles) / len(titles) if titles else 0,
            'avg_snippet_length': sum(len(s) for s in snippets) / len(snippets) if snippets else 0
        }

    def _extract_common_words(self, texts: List[str]) -> List[str]:
        """提取高频词汇"""
        from collections import Counter
        import re

        # 简单的中文分词（实际应使用jieba）
        words = []
        for text in texts:
            # 提取中文词
            chinese_words = re.findall(r'[\u4e00-\u9fff]+', text)
            words.extend(chinese_words)

        # 统计词频
        counter = Counter(words)
        return [word for word, count in counter.most_common(20)]

    def _classify_content_type(self, results: List[Dict]) -> Dict:
        """分类内容类型"""
        types = {
            'blog': 0,
            'news': 0,
            'product': 0,
            'video': 0,
            'forum': 0,
            'official': 0
        }

        for result in results:
            url = result.get('url', '').lower()
            title = result.get('title', '').lower()

            if 'blog' in url or 'article' in url:
                types['blog'] += 1
            elif 'news' in url or 'new' in title:
                types['news'] += 1
            elif 'product' in url or 'shop' in url:
                types['product'] += 1
            elif 'video' in url or 'youtube' in url:
                types['video'] += 1
            elif 'forum' in url or 'zhidao' in url:
                types['forum'] += 1
            elif '.gov' in url or '.edu' in url:
                types['official'] += 1

        return types

    def _analyze_title_patterns(self, titles: List[str]) -> List[str]:
        """分析标题模式"""
        patterns = []

        for title in titles:
            if '最佳' in title or 'Top' in title or 'top' in title:
                patterns.append('listicle')
            elif '指南' in title or '教程' in title or 'how to' in title.lower():
                patterns.append('tutorial')
            elif '评测' in title or '对比' in title or 'review' in title.lower():
                patterns.append('review')
            elif '是什么' in title or 'what' in title.lower():
                patterns.append('definition')

        return list(set(patterns))

    def _find_content_opportunities(self, results: List[Dict]) -> List[Dict]:
        """发现内容机会"""
        opportunities = []

        # 分析竞争对手的不足
        snippets = [r.get('snippet', '') for r in results]

        # 检查是否有视频内容
        has_video = any('视频' in s for s in snippets)
        if not has_video:
            opportunities.append({
                'type': 'video',
                'suggestion': '竞争对手缺少视频内容，可添加视频提升排名'
            })

        # 检查内容深度
        avg_length = sum(len(s) for s in snippets) / len(snippets) if snippets else 0
        if avg_length < 200:
            opportunities.append({
                'type': 'comprehensive',
                'suggestion': '竞争对手内容较短，可提供更详细的内容'
            })

        # 检查FAQ
        has_faq = any('？' in s or '?' in s for s in snippets)
        if not has_faq:
            opportunities.append({
                'type': 'faq',
                'suggestion': '可添加FAQ部分，解答用户常见问题'
            })

        return opportunities

    def _estimate_ideal_length(self, results: List[Dict]) -> Dict:
        """估算理想内容长度"""
        snippets = [r.get('snippet', '') for r in results]

        if not snippets:
            return {'min': 1000, 'optimal': 1500, 'max': 3000}

        avg_snippet = sum(len(s) for s in snippets) / len(snippets)

        # 基于摘要长度估算全文长度（通常正文是摘要的5-10倍）
        optimal = int(avg_snippet * 7)

        return {
            'min': int(optimal * 0.7),
            'optimal': optimal,
            'max': int(optimal * 1.5)
        }

    def generate_content_brief(self, keyword: str) -> Dict:
        """
        生成内容简报

        Args:
            keyword: 目标关键词

        Returns:
            内容创作简报
        """
        analysis = self.analyze_keyword(keyword)

        if 'error' in analysis:
            return analysis

        brief = {
            'keyword': keyword,
            'title_suggestions': self._generate_title_suggestions(analysis),
            'outline_suggestions': self._generate_outline(analysis),
            'word_count': analysis['recommended_length'],
            'must_include': analysis['analysis']['common_keywords'][:5],
            'content_type': self._determine_best_content_type(analysis),
            'competing_sites': [r['title'] for r in analysis['results'][:3]],
            'opportunities': analysis['content_opportunities']
        }

        return brief

    def _generate_title_suggestions(self, analysis: Dict) -> List[str]:
        """生成标题建议"""
        keyword = analysis['keyword']
        patterns = analysis['analysis'].get('title_patterns', [])

        suggestions = []

        if 'listicle' in patterns:
            suggestions.append(f'{keyword}的{5}个最佳方法')
        if 'tutorial' in patterns:
            suggestions.append(f'{keyword}完整指南')
        if 'review' in patterns:
            suggestions.append(f'{keyword}深度评测')
        if 'definition' in patterns:
            suggestions.append(f'什么是{keyword}？')

        # 默认建议
        if not suggestions:
            suggestions = [
                f'{keyword}：全面指南',
                f'关于{keyword}你需要知道的',
                f'{keyword}的最佳实践'
            ]

        return suggestions[:5]

    def _generate_outline(self, analysis: Dict) -> List[str]:
        """生成文章大纲建议"""
        keyword = analysis['keyword']
        content_types = analysis['analysis'].get('content_types', {})

        outline = [
            f'什么是{keyword}？',
            f'{keyword}的重要性',
            f'{keyword}的核心要素',
            f'如何开始{keyword}',
            f'常见问题解答'
        ]

        # 根据内容类型调整
        if content_types.get('blog', 0) > content_types.get('news', 0):
            outline.insert(2, f'{keyword}的最佳实践')

        if content_types.get('product', 0) > 0:
            outline.insert(3, f'{keyword}产品推荐')

        return outline

    def _determine_best_content_type(self, analysis: Dict) -> str:
        """确定最佳内容类型"""
        content_types = analysis['analysis'].get('content_types', {})

        if not content_types:
            return 'blog_post'

        # 找出最常见的内容类型
        best_type = max(content_types, key=content_types.get)

        type_mapping = {
            'blog': 'blog_post',
            'news': 'news_article',
            'product': 'product_review',
            'video': 'how_to_guide',
            'forum': 'faq'
        }

        return type_mapping.get(best_type, 'blog_post')
