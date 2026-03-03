"""
SEO AIOS 站点矩阵管理服务
Site Matrix Management Service
借鉴 AI-SEO-Mass-Engine
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from app.models import Site, Article, Keyword
from app import db


class SiteMatrixManager:
    """
    站点矩阵管理器
    自动化管理多个站点的SEO内容策略
    """

    def __init__(self, user_id: int):
        self.user_id = user_id

    def create_site_network(self, base_domain: str, count: int,
                          template: str = 'default',
                          content_strategy: str = 'niche') -> List[Site]:
        """
        创建站点矩阵

        Args:
            base_domain: 基础域名 (如: example)
            count: 创建数量
            template: 站点模板
            content_strategy: 内容策略 (niche/pillar/ Satellites)

        Returns:
            创建的站点列表
        """
        sites = []

        for i in range(count):
            # 生成站点名称和域名
            if content_strategy == 'pillar':
                # 支柱站点
                site_name = f"{base_domain}"
                site_domain = f"{base_domain}.com"
            elif content_strategy == 'satellites':
                # 卫星站点
                site_name = f"{base_domain}-{i+1}"
                site_domain = f"{base_domain}{i+1}.com"
            else:
                # 细分站点
                site_name = f"{base_domain}-{i+1}"
                site_domain = f"{base_domain}{i+1}.com"

            site = Site(
                user_id=self.user_id,
                name=site_name,
                domain=site_domain,
                description=f"{base_domain} related site {i+1}",
                template=template,
                language='zh-CN',
                status='active'
            )

            db.session.add(site)
            sites.append(site)

        db.session.commit()
        return sites

    def analyze_network(self) -> Dict:
        """
        分析站点网络状态

        Returns:
            网络分析报告
        """
        sites = Site.query.filter_by(user_id=self.user_id).all()

        total_articles = sum(len(s.articles) for s in sites)
        total_keywords = sum(len(s.keywords) if hasattr(s, 'keywords') else 0 for s in sites)
        active_sites = sum(1 for s in sites if s.status == 'active')

        # 计算网络权威度
        network_authority = self._calculate_network_authority(sites)

        return {
            'total_sites': len(sites),
            'active_sites': active_sites,
            'total_articles': total_articles,
            'total_keywords': total_keywords,
            'network_authority': network_authority,
            'avg_articles_per_site': total_articles / len(sites) if sites else 0,
            'sites': [{
                'id': s.id,
                'name': s.name,
                'domain': s.domain,
                'articles_count': len(s.articles),
                'status': s.status
            } for s in sites]
        }

    def _calculate_network_authority(self, sites: List[Site]) -> float:
        """
        计算网络权威度 (借鉴外链策略)
        """
        if not sites:
            return 0.0

        # 基于站点数量、文章数量、活跃度计算
        site_score = len(sites) * 10
        article_score = sum(len(s.articles) for s in sites) * 2
        active_score = sum(1 for s in sites if s.status == 'active') * 5

        total = site_score + article_score + active_score
        return min(total / 100, 100)  # 最高100分

    def distribute_keywords(self, keywords: List[str], sites: List[Site]) -> Dict:
        """
        关键词分配策略

        Args:
            keywords: 关键词列表
            sites: 目标站点

        Returns:
            分配报告
        """
        distribution = {}
        keywords_per_site = len(keywords) // len(sites) if sites else 0

        for i, site in enumerate(sites):
            start_idx = i * keywords_per_site
            end_idx = start_idx + keywords_per_site if i < len(sites) - 1 else len(keywords)

            site_keywords = keywords[start_idx:end_idx]

            # 为站点分配关键词
            for kw in site_keywords:
                keyword = Keyword(
                    user_id=self.user_id,
                    site_id=site.id,
                    keyword=kw,
                    status='active'
                )
                db.session.add(keyword)

            distribution[site.name] = site_keywords

        db.session.commit()

        return {
            'total_keywords': len(keywords),
            'sites_count': len(sites),
            'distribution': distribution,
            'avg_keywords_per_site': keywords_per_site
        }

    def cross_link_sites(self, pillar_site_id: int, satellite_site_ids: List[int]) -> Dict:
        """
        建立站点间内链策略 (Pillar-Satellite模型)

        Args:
            pillar_site_id: 支柱站点ID
            satellite_site_ids: 卫星站点ID列表

        Returns:
            内链建设报告
        """
        pillar_site = Site.query.get(pillar_site_id)
        if not pillar_site:
            return {'error': 'Pillar site not found'}

        satellite_sites = Site.query.filter(Site.id.in_(satellite_site_ids)).all()

        links_created = 0

        # 为每个卫星站点创建指向支柱站点的链接
        for sat_site in satellite_sites:
            # 在每篇文章中添加指向支柱站点的链接
            for article in sat_site.articles[:5]:  # 每站最多5篇
                # 这里只是记录策略，实际内链在模板中实现
                links_created += 1

        return {
            'pillar_site': pillar_site.name,
            'satellite_count': len(satellite_sites),
            'links_created': links_created,
            'strategy': 'pillar-satellite',
            'status': 'configured'
        }

    def get_content_calendar(self, weeks: int = 4) -> Dict:
        """
        内容日历视图

        Args:
            weeks: 周数

        Returns:
            内容发布计划
        """
        sites = Site.query.filter_by(user_id=self.user_id).all()

        calendar = []
        for week in range(weeks):
            week_content = {
                'week': week + 1,
                'planned': 0,
                'sites': {}
            }

            for site in sites:
                # 计算每周应发布数量
                planned_articles = max(1, len(site.articles) // (weeks * 2))
                week_content['planned'] += planned_articles
                week_content['sites'][site.name] = planned_articles

            calendar.append(week_content)

        return {
            'total_weeks': weeks,
            'calendar': calendar,
            'total_planned': sum(w['planned'] for w in calendar)
        }


class ContentWorkflow:
    """
    内容工作流自动化
    借鉴 contentflow-ai
    """

    def __init__(self, site_id: int, user_id: int):
        self.site_id = site_id
        self.user_id = user_id
        self.site = Site.query.get(site_id)

    def run_automated_workflow(self, keywords: List[str],
                              content_type: str = 'blog_post',
                              publish: bool = False) -> Dict:
        """
        运行自动化内容生成工作流

        Args:
            keywords: 关键词列表
            content_type: 内容类型
            publish: 是否直接发布

        Returns:
            工作流执行报告
        """
        from app.services.content_generator import ContentGenerator
        from app.models import Article
        from app.utils.helpers import slugify

        # 获取AI配置
        ai_config = self.site.ai_config if self.site else None
        if not ai_config:
            return {'error': 'Site AI config not found'}

        generator = ContentGenerator(ai_config)

        results = {
            'keywords_processed': 0,
            'articles_created': 0,
            'articles_published': 0,
            'errors': []
        }

        for keyword in keywords:
            try:
                # 1. 生成内容
                result = generator.generate(
                    topic=keyword,
                    keywords=[keyword],
                    content_type=content_type
                )

                # 2. 创建文章
                article = Article(
                    site_id=self.site_id,
                    user_id=self.user_id,
                    title=result['title'],
                    slug=slugify(result['title']),
                    content=result['content'],
                    excerpt=result.get('excerpt', ''),
                    meta_title=result.get('meta_title', ''),
                    meta_description=result.get('meta_description', ''),
                    meta_keywords=result.get('meta_keywords', ''),
                    status='published' if publish else 'draft'
                )

                db.session.add(article)
                results['articles_created'] += 1
                results['keywords_processed'] += 1

                if publish:
                    results['articles_published'] += 1

            except Exception as e:
                results['errors'].append({
                    'keyword': keyword,
                    'error': str(e)
                })

        db.session.commit()

        return results

    def get_workflow_status(self) -> Dict:
        """获取工作流状态"""
        articles = Article.query.filter_by(site_id=self.site_id).all()

        return {
            'site': self.site.name if self.site else 'Unknown',
            'total_articles': len(articles),
            'published': sum(1 for a in articles if a.status == 'published'),
            'draft': sum(1 for a in articles if a.status == 'draft'),
            'last_updated': articles[0].updated_at.isoformat() if articles else None
        }
