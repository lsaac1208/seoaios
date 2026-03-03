"""
SEO AIOS WordPress 发布服务
WordPress Publishing Service
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime


class WordPressPublisher:
    """
    WordPress发布器
    支持发布文章、页面到WordPress
    """

    def __init__(self, site_url: str, username: str, app_password: str):
        """
        初始化WordPress发布器

        Args:
            site_url: WordPress站点URL
            username: 用户名
            app_password: WordPress应用密码
        """
        self.site_url = site_url.rstrip('/')
        self.username = username
        self.app_password = app_password
        self.api_url = f"{self.site_url}/wp-json/wp/v2"
        self.auth = (username, app_password)

    def publish_article(self, article, categories: List[int] = None,
                       tags: List[int] = None, featured_media: int = None,
                       status: str = 'draft') -> Dict:
        """
        发布文章

        Args:
            article: 文章对象
            categories: 分类ID列表
            tags: 标签ID列表
            featured_media: 特色图片ID
            status: 发布状态 (draft/publish/pending)

        Returns:
            发布结果
        """
        # 构建文章数据
        post_data = {
            'title': article.title,
            'content': article.content,
            'status': status,
            'slug': article.slug,
        }

        # 添加摘要
        if hasattr(article, 'excerpt') and article.excerpt:
            post_data['excerpt'] = article.excerpt

        # 添加分类
        if categories:
            post_data['categories'] = categories

        # 添加标签
        if tags:
            post_data['tags'] = tags

        # 添加特色图片
        if featured_media:
            post_data['featured_media'] = featured_media

        # 添加SEO meta（使用Rank Math或Yoast格式）
        if hasattr(article, 'meta_title') or hasattr(article, 'meta_description'):
            post_data['meta'] = {}
            if hasattr(article, 'meta_title') and article.meta_title:
                post_data['meta']['rank_math_title'] = article.meta_title
            if hasattr(article, 'meta_description') and article.meta_description:
                post_data['meta']['rank_math_description'] = article.meta_description
            if hasattr(article, 'meta_keywords') and article.meta_keywords:
                post_data['meta']['rank_math_focus_keyword'] = article.meta_keywords.split(',')[0]

        try:
            response = requests.post(
                f"{self.api_url}/posts",
                json=post_data,
                auth=self.auth,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            return {
                'success': True,
                'post_id': result['id'],
                'post_url': result['link'],
                'status': result['status']
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }

    def update_article(self, post_id: int, article, status: str = None) -> Dict:
        """
        更新文章

        Args:
            post_id: WordPress文章ID
            article: 文章对象
            status: 新状态

        Returns:
            更新结果
        """
        post_data = {
            'title': article.title,
            'content': article.content,
        }

        if status:
            post_data['status'] = status

        if hasattr(article, 'slug'):
            post_data['slug'] = article.slug

        try:
            response = requests.post(
                f"{self.api_url}/posts/{post_id}",
                json=post_data,
                auth=self.auth,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            return {
                'success': True,
                'post_id': result['id'],
                'post_url': result['link']
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }

    def delete_article(self, post_id: int, force: bool = False) -> Dict:
        """
        删除文章

        Args:
            post_id: WordPress文章ID
            force: 强制删除（绕过回收站）

        Returns:
            删除结果
        """
        try:
            response = requests.delete(
                f"{self.api_url}/posts/{post_id}",
                params={'force': force},
                auth=self.auth,
                timeout=30
            )
            response.raise_for_status()

            return {'success': True, 'deleted': True}

        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': str(e)}

    def upload_media(self, image_path: str, title: str = None) -> Dict:
        """
        上传媒体文件

        Args:
            image_path: 图片路径或URL
            title: 媒体标题

        Returns:
            上传结果
        """
        try:
            # 如果是URL，先下载图片
            if image_path.startswith('http'):
                response = requests.get(image_path, timeout=30)
                image_content = response.content
                filename = image_path.split('/')[-1]
            else:
                with open(image_path, 'rb') as f:
                    image_content = f.read()
                filename = os.path.basename(image_path)

            # 上传到WordPress
            files = {'file': (filename, image_content)}
            data = {}
            if title:
                data['title'] = title

            response = requests.post(
                f"{self.api_url}/media",
                files=files,
                data=data,
                auth=self.auth,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            return {
                'success': True,
                'media_id': result['id'],
                'url': result['source_url']
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_categories(self) -> List[Dict]:
        """获取所有分类"""
        try:
            response = requests.get(
                f"{self.api_url}/categories",
                auth=self.auth,
                timeout=30
            )
            response.raise_for_status()

            return [{'id': c['id'], 'name': c['name']} for c in response.json()]

        except Exception:
            return []

    def get_tags(self) -> List[Dict]:
        """获取所有标签"""
        try:
            response = requests.get(
                f"{self.api_url}/tags",
                auth=self.auth,
                timeout=30
            )
            response.raise_for_status()

            return [{'id': t['id'], 'name': t['name']} for t in response.json()]

        except Exception:
            return []

    def create_category(self, name: str, description: str = None) -> Dict:
        """创建分类"""
        try:
            data = {'name': name}
            if description:
                data['description'] = description

            response = requests.post(
                f"{self.api_url}/categories",
                json=data,
                auth=self.auth,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()
            return {'success': True, 'category_id': result['id']}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def test_connection(self) -> Dict:
        """测试连接"""
        try:
            response = requests.get(
                f"{self.api_url}/users/me",
                auth=self.auth,
                timeout=10
            )

            if response.status_code == 200:
                user = response.json()
                return {
                    'success': True,
                    'user': user['name'],
                    'roles': user['roles']
                }
            else:
                return {'success': False, 'error': f'HTTP {response.status_code}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}


class WordPressSiteManager:
    """
    WordPress站点管理器
    管理多个WordPress站点的连接
    """

    def __init__(self):
        self.sites = {}

    def add_site(self, name: str, site_url: str, username: str, app_password: str):
        """添加WordPress站点"""
        self.sites[name] = {
            'url': site_url,
            'username': username,
            'password': app_password,
            'publisher': WordPressPublisher(site_url, username, app_password)
        }

    def get_publisher(self, name: str) -> Optional[WordPressPublisher]:
        """获取发布器"""
        if name in self.sites:
            return self.sites[name]['publisher']
        return None

    def list_sites(self) -> List[Dict]:
        """列出所有站点"""
        return [
            {'name': name, 'url': info['url']}
            for name, info in self.sites.items()
        ]
