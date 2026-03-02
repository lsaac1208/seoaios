"""
SEO AIOS 内容改写服务
Content Rewriter Service
"""

import os


class ContentRewriter:
    """AI内容改写器"""

    def __init__(self, ai_config):
        """
        初始化改写器

        Args:
            ai_config: AiConfig模型实例
        """
        self.ai_config = ai_config

    def rewrite(self, content, rewrite_type='semantic', level=3):
        """
        改写内容

        Args:
            content: 原始内容
            rewrite_type: 改写类型 (semantic/paraphrasing/humanize)
            level: 改写程度 (1-5)

        Returns:
            改写后的内容
        """
        prompt = self._build_prompt(content, rewrite_type, level)
        result = self._call_ai(prompt)
        return result

    def _build_prompt(self, content, rewrite_type, level):
        """构建改写提示词"""
        level_descriptions = {
            1: '轻度改写，保持原意，只改变一些词汇',
            2: '中轻度改写，更换部分句子结构',
            3: '中等改写，重新组织内容但保持核心观点',
            4: '深度改写，用自己的话表达相同观点',
            5: '完全重写，保持主题但完全改变表达方式'
        }

        style_instruction = level_descriptions.get(level, level_descriptions[3])

        type_instructions = {
            'semantic': '保持原文的语义和信息，只是改写表达方式',
            'paraphrasing': '对原文进行意译，改变表达方式但保持相同含义',
            'humanize': '使内容更加自然、像人类写作，避免AI痕迹'
        }

        type_instruction = type_instructions.get(rewrite_type, type_instructions['semantic'])

        prompt = f"""请根据以下要求改写文章：

改写类型：{type_instruction}
改写程度：{style_instruction}

请直接输出改写后的内容，不要添加任何说明：
---
{content}
---
"""

        return prompt

    def _call_ai(self, prompt):
        """调用AI改写"""
        provider = self.ai_config.provider

        try:
            if provider == 'openai':
                return self._call_openai(prompt)
            elif provider == 'anthropic':
                return self._call_anthropic(prompt)
            else:
                return self._call_openai(prompt)
        except Exception as e:
            raise Exception(f"AI调用失败: {str(e)}")

    def _call_openai(self, prompt):
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
                {'role': 'system', 'content': '你是一个专业的内容改写助手，擅长将原文改写成不同的表达方式，同时保持原意。'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': self.ai_config.temperature or 0.7,
            'max_tokens': 4000
        }

        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content']

    def _call_anthropic(self, prompt):
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
            'max_tokens': 4000,
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }

        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()

        result = response.json()
        return result['content'][0]['text']
