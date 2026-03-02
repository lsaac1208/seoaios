"""
SEO AIOS 内容生成服务
Content Generator Service
"""

import os
import json


class ContentGenerator:
    """AI内容生成器"""

    def __init__(self, ai_config):
        """
        初始化生成器

        Args:
            ai_config: AiConfig模型实例
        """
        self.ai_config = ai_config

    def generate(self, topic, keywords=None, length=1500, style='informative'):
        """
        生成文章内容

        Args:
            topic: 主题
            keywords: 关键词列表
            length: 内容长度
            style: 写作风格

        Returns:
            生成的内容字典
        """
        # 构建prompt
        prompt = self._build_prompt(topic, keywords, length, style)

        # 调用AI生成
        content = self._call_ai(prompt, length)

        # 解析结果
        result = self._parse_result(content, topic, keywords)

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
