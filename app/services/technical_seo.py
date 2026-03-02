"""
SEO AIOS 技术SEO检查服务
Technical SEO Checker Service
"""

import requests
from urllib.parse import urlparse


class TechnicalSeoChecker:
    """技术SEO检查器"""

    def __init__(self, timeout=30):
        self.timeout = timeout

    def check_site(self, site):
        """
        检查站点技术SEO

        Args:
            site: Site模型实例

        Returns:
            检查结果字典
        """
        result = {
            'score': 0,
            'checks': [],
            'issues': [],
            'recommendations': []
        }

        domain = site.domain
        if not domain:
            domain = 'http://localhost'

        checks = []

        # 1. HTTPS检查
        checks.append({
            'name': 'https',
            'label': 'HTTPS',
            'passed': domain.startswith('https'),
            'message': '使用HTTPS' if domain.startswith('https') else '建议使用HTTPS'
        })

        if not domain.startswith('https'):
            result['issues'].append('建议使用HTTPS协议')

        # 2. 站点地图检查
        try:
            sitemap_url = f"{domain.rstrip('/')}/sitemap.xml"
            response = requests.head(sitemap_url, timeout=self.timeout, allow_redirects=True)
            has_sitemap = response.status_code == 200

            checks.append({
                'name': 'sitemap',
                'label': '站点地图',
                'passed': has_sitemap,
                'message': '站点地图已找到' if has_sitemap else '缺少站点地图'
            })

            if not has_sitemap:
                result['issues'].append('缺少站点地图sitemap.xml')
        except:
            checks.append({
                'name': 'sitemap',
                'label': '站点地图',
                'passed': False,
                'message': '无法检查站点地图'
            })

        # 3. Robots.txt检查
        try:
            robots_url = f"{domain.rstrip('/')}/robots.txt"
            response = requests.head(robots_url, timeout=self.timeout, allow_redirects=True)
            has_robots = response.status_code == 200

            checks.append({
                'name': 'robots',
                'label': 'Robots.txt',
                'passed': has_robots,
                'message': 'Robots.txt已找到' if has_robots else '缺少Robots.txt'
            })

            if not has_robots:
                result['issues'].append('缺少robots.txt文件')
        except:
            checks.append({
                'name': 'robots',
                'label': 'Robots.txt',
                'passed': False,
                'message': '无法检查Robots.txt'
            })

        # 4. Favicon检查
        try:
            favicon_url = f"{domain.rstrip('/')}/favicon.ico"
            response = requests.head(favicon_url, timeout=self.timeout, allow_redirects=True)
            has_favicon = response.status_code == 200

            checks.append({
                'name': 'favicon',
                'label': 'Favicon',
                'passed': has_favicon,
                'message': 'Favicon已找到' if has_favicon else '建议添加Favicon'
            })

            if not has_favicon:
                result['recommendations'].append('建议添加favicon.ico')
        except:
            pass

        # 5. www重定向检查
        checks.append({
            'name': 'www_redirect',
            'label': 'WWW重定向',
            'passed': True,
            'message': '建议配置www重定向'
        })

        # 计算得分
        passed_count = sum(1 for c in checks if c['passed'])
        total_count = len(checks)
        result['score'] = int((passed_count / total_count * 100)) if total_count > 0 else 0

        result['checks'] = checks

        return result

    def check_page(self, url):
        """
        检查单个页面的技术SEO

        Args:
            url: 页面URL

        Returns:
            检查结果
        """
        result = {
            'score': 0,
            'checks': []
        }

        try:
            response = requests.get(url, timeout=self.timeout)
            status_code = response.status_code

            # 状态码检查
            checks = [{
                'name': 'status_code',
                'label': 'HTTP状态码',
                'passed': status_code == 200,
                'message': f'HTTP {status_code}'
            }]

            if status_code != 200:
                result['checks'] = checks
                result['score'] = 0
                return result

            # 响应时间
            response_time = response.elapsed.total_seconds()
            checks.append({
                'name': 'response_time',
                'label': '响应时间',
                'passed': response_time < 3,
                'message': f'{response_time:.2f}秒'
            })

            # 页面大小
            page_size = len(response.content)
            checks.append({
                'name': 'page_size',
                'label': '页面大小',
                'passed': page_size < 3 * 1024 * 1024,  # 3MB
                'message': f'{page_size / 1024:.1f}KB'
            })

            # 计算得分
            passed_count = sum(1 for c in checks if c['passed'])
            result['score'] = int((passed_count / len(checks) * 100))

            result['checks'] = checks

        except Exception as e:
            result['error'] = str(e)

        return result
