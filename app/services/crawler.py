"""
SEO AIOS 网页爬虫服务
Web Crawler Service
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
import json
from datetime import datetime


class WebCrawler:
    """网页爬虫"""

    def __init__(self, timeout=30, user_agent=None):
        """
        初始化爬虫

        Args:
            timeout: 请求超时时间
            user_agent: User-Agent
        """
        self.timeout = timeout
        self.user_agent = user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})

    def crawl_url(self, url, max_depth=2):
        """
        爬取单个URL

        Args:
            url: 目标URL
            max_depth: 最大爬取深度

        Returns:
            爬取结果字典
        """
        result = {
            'url': url,
            'domain': '',
            'status_code': 0,
            'title': '',
            'meta_description': '',
            'h1_tags': [],
            'content': '',
            'word_count': 0,
            'image_count': 0,
            'link_count': 0,
            'internal_links': [],
            'external_links': [],
            'images': [],
            'error': None,
            'response_time': 0
        }

        start_time = time.time()

        try:
            # 发送请求
            response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            result['status_code'] = response.status_code
            result['response_time'] = time.time() - start_time

            if response.status_code != 200:
                result['error'] = f"HTTP {response.status_code}"
                return result

            # 解析域名
            result['domain'] = urlparse(url).netloc

            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # 提取标题
            title_tag = soup.find('title')
            if title_tag:
                result['title'] = title_tag.get_text().strip()

            # 提取meta描述
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                result['meta_description'] = meta_desc.get('content', '').strip()

            # 提取H1标签
            h1_tags = soup.find_all('h1')
            result['h1_tags'] = [h1.get_text().strip() for h1 in h1_tags]

            # 提取主要内容
            # 移除脚本和样式
            for script in soup(['script', 'style']):
                script.decompose()

            # 获取body
            body = soup.find('body')
            if body:
                result['content'] = body.get_text(separator=' ', strip=True)
                result['word_count'] = len(result['content'].split())

            # 提取图片
            images = soup.find_all('img')
            result['image_count'] = len(images)
            result['images'] = [
                {
                    'src': img.get('src', ''),
                    'alt': img.get('alt', ''),
                    'title': img.get('title', '')
                }
                for img in images if img.get('src')
            ]

            # 提取链接
            links = soup.find_all('a', href=True)
            result['link_count'] = len(links)

            for link in links:
                href = link['href']
                full_url = urljoin(url, href)
                parsed = urlparse(full_url)

                # 跳过锚点和空链接
                if not parsed.netloc or parsed.scheme in ['javascript', 'mailto', 'tel']:
                    continue

                link_info = {
                    'url': full_url,
                    'text': link.get_text().strip()[:50],
                    'domain': parsed.netloc
                }

                if parsed.netloc == result['domain']:
                    result['internal_links'].append(link_info)
                else:
                    result['external_links'].append(link_info)

            # 限制链接数量
            result['internal_links'] = result['internal_links'][:50]
            result['external_links'] = result['external_links'][:20]

        except requests.exceptions.Timeout:
            result['error'] = '请求超时'
        except requests.exceptions.RequestException as e:
            result['error'] = str(e)
        except Exception as e:
            result['error'] = f"解析错误: {str(e)}"

        return result

    def crawl_site(self, base_url, max_pages=10, max_depth=2):
        """
        爬取整个站点

        Args:
            base_url: 基础URL
            max_pages: 最大爬取页面数
            max_depth: 最大深度

        Returns:
            爬取结果列表
        """
        results = []
        visited = set()
        to_crawl = [(base_url, 0)]

        domain = urlparse(base_url).netloc

        while to_crawl and len(results) < max_pages:
            url, depth = to_crawl.pop(0)

            if url in visited or depth > max_depth:
                continue

            visited.add(url)

            # 爬取页面
            result = self.crawl_url(url, max_depth)
            results.append(result)

            # 添加内部链接到爬取队列
            if depth < max_depth:
                for link in result.get('internal_links', []):
                    link_url = link['url']
                    if link_url not in visited and len(to_crawl) < max_pages * 2:
                        to_crawl.append((link_url, depth + 1))

            # 礼貌延迟
            time.sleep(1)

        return results

    def extract_structured_data(self, url):
        """
        提取结构化数据

        Args:
            url: 目标URL

        Returns:
            结构化数据列表
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            soup = BeautifulSoup(response.content, 'html.parser')

            # 查找JSON-LD
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            structured_data = []

            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    structured_data.append(data)
                except:
                    continue

            return structured_data

        except Exception as e:
            return []
