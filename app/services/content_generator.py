"""
SEO AIOS 内容生成服务
Content Generator Service
"""

import os
import json
import re
from typing import Dict, List, Optional


# 内容类型模板
CONTENT_TYPES = {
    'blog_post': {
        'name': '博客文章',
        'description': '深入分析、教程、指南类文章',
        'prompt_template': '请生成一篇详细的博客文章，结构包括：引言、主体分析、结论'
    },
    'product_review': {
        'name': '产品评测',
        'description': '产品功能介绍、优缺点分析、购买建议',
        'prompt_template': '请生成一篇详细的产品评测，包含：产品概述、功能特点、优缺点、适用人群、评分'
    },
    'news_article': {
        'name': '新闻资讯',
        'description': '最新资讯、事件报道、行业动态',
        'prompt_template': '请生成一篇新闻报道，包含：标题、导语、详细报道、背景、展望'
    },
    'how_to_guide': {
        'name': '操作指南',
        'description': '步骤教程、操作说明、问题解决',
        'prompt_template': '请生成一篇操作指南，包含：概述、准备工作、详细步骤、注意事项、常见问题'
    },
    'comparison': {
        'name': '对比分析',
        'description': '产品对比、方案比较、选型建议',
        'prompt_template': '请生成一篇对比分析，包含：对比对象、对比维度、详细对比、结论建议'
    },
    'faq': {
        'name': '问答文章',
        'description': '常见问题解答、FAQ页面',
        'prompt_template': '请生成FAQ问答内容，每个问题对应一个详细解答'
    },
    'landing_page': {
        'name': '着陆页',
        'description': '营销落地页、销售页面',
        'prompt_template': '请生成营销着陆页，包含：痛点描述、解决方案、产品优势、客户见证、行动号召'
    }
}

# 写作风格
WRITING_STYLES = {
    'professional': {'name': '专业正式', 'temperature': 0.5},
    'friendly': {'name': '友好亲切', 'temperature': 0.7},
    'casual': {'name': '轻松随意', 'temperature': 0.8},
    'humorous': {'name': '幽默风趣', 'temperature': 0.9},
    'academic': {'name': '学术严谨', 'temperature': 0.4},
    'persuasive': {'name': '说服性', 'temperature': 0.7}
}

# 内容长度预设
LENGTH_PRESETS = {
    'short': {'words': 500, 'description': '短文 (~500字)'},
    'medium': {'words': 1000, 'description': '中等 (~1000字)'},
    'long': {'words': 1500, 'description': '长文 (~1500字)'},
    'extended': {'words': 2500, 'description': '超长 (~2500字)'},
    'comprehensive': {'words': 5000, 'description': '全面 (~5000字)'}
}


class ContentGenerator:
    """AI内容生成器"""

    def __init__(self, ai_config):
        """
        初始化生成器

        Args:
            ai_config: AiConfig模型实例
        """
        self.ai_config = ai_config

    def generate(self, topic, keywords=None, length=1500, style='informative', content_type='blog_post'):
        """
        生成文章内容

        Args:
            topic: 主题
            keywords: 关键词列表
            length: 内容长度
            style: 写作风格
            content_type: 内容类型

        Returns:
            生成的内容字典
        """
        # 获取内容类型模板
        type_template = CONTENT_TYPES.get(content_type, CONTENT_TYPES['blog_post'])

        # 构建prompt
        prompt = self._build_prompt(topic, keywords, length, style, type_template)

        # 调用AI生成
        content = self._call_ai(prompt, length)

        # 解析结果
        result = self._parse_result(content, topic, keywords)

        # 添加SEO元素
        result = self._add_seo_elements(result, keywords)

        return result

    def generate_batch(self, topics: List[str], keywords_list: List[List[str]] = None,
                      length: int = 1500, style: str = 'professional',
                      content_type: str = 'blog_post') -> List[Dict]:
        """
        批量生成内容 (借鉴 AI-SEO-Mass-Engine)

        Args:
            topics: 主题列表
            keywords_list: 关键词列表（每个主题对应一组关键词）
            length: 内容长度
            style: 写作风格
            content_type: 内容类型

        Returns:
            生成的内容列表
        """
        results = []

        for i, topic in enumerate(topics):
            keywords = keywords_list[i] if keywords_list and i < len(keywords_list) else None

            try:
                result = self.generate(topic, keywords, length, style, content_type)
                result['topic'] = topic
                result['status'] = 'success'
                results.append(result)
            except Exception as e:
                results.append({
                    'topic': topic,
                    'status': 'error',
                    'error': str(e)
                })

        return results

    def generate_with_serp_analysis(self, topic: str, keywords: List[str],
                                   target_keywords: List[str]) -> Dict:
        """
        基于SERP分析生成内容 (借鉴 SEO Writing.ai)

        Args:
            topic: 主题
            keywords: 目标关键词
            target_keywords: 需要优化的关键词

        Returns:
            优化后的内容
        """
        # 基础生成
        result = self.generate(topic, keywords, content_type='blog_post')

        # 基于SERP分析优化内容
        optimized = self._optimize_for_serp(result, target_keywords)

        return optimized

    def _optimize_for_serp(self, content: Dict, target_keywords: List[str]) -> Dict:
        """根据SERP分析优化内容"""
        result = content.copy()
        result['serp_optimization'] = {
            'keyword_density': self._calculate_keyword_density(content['content'], target_keywords),
            'headings_optimized': self._optimize_headings(content['content'], target_keywords),
            'readability_score': self._calculate_readability(content['content'])
        }
        return result

    def _calculate_keyword_density(self, content: str, keywords: List[str]) -> Dict:
        """计算关键词密度"""
        density_map = {}
        for kw in keywords:
            count = content.lower().count(kw.lower())
            density = (count / len(content.split())) * 100 if content else 0
            density_map[kw] = {
                'count': count,
                'density': round(density, 2)
            }
        return density_map

    def _optimize_headings(self, content: str, keywords: List[str]) -> Dict:
        """优化标题结构"""
        headings = re.findall(r'<h[2-3]>(.*?)</h[2-3]>', content)
        keyword_in_headings = sum(1 for h in headings if any(kw.lower() in h.lower() for kw in keywords))

        return {
            'total_headings': len(headings),
            'keyword_in_headings': keyword_in_headings,
            'optimized': keyword_in_headings >= len(headings) * 0.5 if headings else False
        }

    def _calculate_readability(self, content: str) -> Dict:
        """计算可读性分数（基于中文特点简化）"""
        sentences = content.count('。') + content.count('！') + content.count('？')
        words = len(content)

        if sentences == 0:
            return {'score': 0, 'level': 'unknown'}

        avg_sentence_length = words / sentences

        if avg_sentence_length < 20:
            level = 'easy'
            score = 90
        elif avg_sentence_length < 35:
            level = 'medium'
            score = 75
        else:
            level = 'difficult'
            score = 60

        return {'score': score, 'level': level}

    def generate_multilingual(self, topic: str, keywords: List[str],
                            target_languages: List[str], length: int = 1500) -> Dict:
        """
        多语言内容生成

        Args:
            topic: 主题
            keywords: 关键词
            target_languages: 目标语言列表 ['zh', 'en', 'ja', 'ko']
            length: 内容长度

        Returns:
            多语言内容字典
        """
        language_names = {
            'zh': '中文',
            'en': 'English',
            'ja': '日本語',
            'ko': '한국어'
        }

        results = {}

        for lang in target_languages:
            prompt = self._build_multilingual_prompt(topic, keywords, length, lang)
            content = self._call_ai(prompt, length)
            parsed = self._parse_result(content, topic, keywords)
            results[lang] = {
                'language': language_names.get(lang, lang),
                'content': parsed
            }

        return results

    def _build_multilingual_prompt(self, topic: str, keywords: List[str],
                                   length: int, language: str) -> str:
        """构建多语言提示词"""
        keywords_str = ', '.join(keywords) if keywords else ''

        lang_instruction = {
            'en': 'Please write in English.',
            'ja': 'Please write in Japanese.',
            'ko': 'Please write in Korean.',
            'zh': '请用中文输出。'
        }

        prompt = f"""{lang_instruction.get(language, '')}

请根据以下要求生成一篇SEO友好的文章：

主题：{topic}
关键词：{keywords_str}
长度：约{length}字

请生成以下内容：
1. 标题（Title）
2. Meta描述（Meta Description）：160字以内
3. 文章内容

格式如下：
---
TITLE: [标题]
META: [Meta描述]
CONTENT:
[文章内容]
---
"""
        return prompt

    def _add_seo_elements(self, result: Dict, keywords: List[str]) -> Dict:
        """添加SEO元素"""
        if not keywords:
            return result

        # 添加结构化数据提示
        result['structured_data'] = {
            '@context': 'https://schema.org',
            '@type': 'Article',
            'headline': result.get('title', ''),
            'keywords': ', '.join(keywords),
            'description': result.get('meta_description', '')
        }

        return result

    def _build_prompt(self, topic, keywords, length, style):
        """构建生成提示词"""
        keywords_str = ', '.join(keywords) if keywords else ''

        prompt = f"""请根据以下要求生成一篇SEO友好的文章：

主题：{topic}
关键词：{keywords_str}
长度：约{length}字
风格：{style}

请生成以下内容：
1. 标题（Title）：简洁明了，包含主要关键词
2. Meta描述（Meta Description）：160字以内，包含核心关键词
3. 文章内容：结构清晰，段落分明，适当使用标题标签

请用中文输出，格式如下：
---
TITLE: [标题]
META: [Meta描述]
CONTENT:
[文章内容]
---
"""

        return prompt

    def _call_ai(self, prompt, length):
        """调用AI生成内容"""
        provider = self.ai_config.provider

        try:
            if provider == 'openai':
                return self._call_openai(prompt, length)
            elif provider == 'anthropic':
                return self._call_anthropic(prompt, length)
            else:
                return self._call_openai(prompt, length)
        except Exception as e:
            raise Exception(f"AI调用失败: {str(e)}")

    def _call_openai(self, prompt, length):
        """调用OpenAI API"""
        api_key = self.ai_config.openai_api_key or os.environ.get('OPENAI_API_KEY')
        api_base = self.ai_config.openai_api_base or os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
        model = self.ai_config.openai_model or 'gpt-3.5-turbo'

        if not api_key:
            raise Exception("请配置OpenAI API Key")

        import requests

        url = f"{api_base}/chat/completions"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': '你是一个专业的SEO内容写作助手，擅长生成高质量、SEO友好的文章。'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': self.ai_config.temperature or 0.7,
            'max_tokens': min(length * 2, 4000)
        }

        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content']

    def _call_anthropic(self, prompt, length):
        """调用Anthropic API"""
        api_key = self.ai_config.anthropic_api_key or os.environ.get('ANTHROPIC_API_KEY')
        model = self.ai_config.anthropic_model or 'claude-3-haiku-20240307'

        if not api_key:
            raise Exception("请配置Anthropic API Key")

        import requests

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            'x-api-key': api_key,
            'anthropic-version': '2023-06-01',
            'Content-Type': 'application/json'
        }

        data = {
            'model': model,
            'max_tokens': min(length * 2, 4000),
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }

        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()

        result = response.json()
        return result['content'][0]['text']

    def _parse_result(self, content, topic, keywords):
        """解析AI返回的结果"""
        lines = content.split('\n')

        title = ''
        meta_description = ''
        article_content = ''

        current_section = 'content'
        for line in lines:
            line = line.strip()
            if line.startswith('TITLE:'):
                title = line.replace('TITLE:', '').strip()
                current_section = 'meta'
            elif line.startswith('META:'):
                meta_description = line.replace('META:', '').strip()
                current_section = 'content'
            elif line.startswith('CONTENT:') or current_section == 'content':
                if line not in ['CONTENT:', '---']:
                    article_content += line + '\n'

        # 如果解析失败，使用默认值
        if not title:
            title = f"关于{topic}的全面指南"
        if not meta_description:
            meta_description = f"本文深入探讨{topic}，为您提供全面的信息和指导。"
        if not article_content:
            article_content = content

        # 生成slug
        from app.utils.helpers import slugify
        slug = slugify(title)

        # 提取简介
        excerpt = article_content[:200] + '...' if len(article_content) > 200 else article_content

        return {
            'title': title,
            'slug': slug,
            'meta_title': title,
            'meta_description': meta_description,
            'meta_keywords': ', '.join(keywords) if keywords else '',
            'content': article_content,
            'excerpt': excerpt,
            'keywords': keywords or []
        }
