"""
SEO AIOS 数据分析服务
Analytics Service
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import func


class AnalyticsEngine:
    """
    数据分析引擎
    提供全面的SEO和内容分析
    """

    def __init__(self, user_id: int):
        self.user_id = user_id

    def get_dashboard_summary(self) -> Dict:
        """获取仪表板摘要"""
        from app.models import Site, Article, Keyword, Task

        # 统计站点
        total_sites = Site.query.filter_by(user_id=self.user_id).count()
        active_sites = Site.query.filter_by(user_id=self.user_id, status='active').count()

        # 统计文章
        total_articles = Article.query.join(Site).filter(Site.user_id == self.user_id).count()
        published_articles = Article.query.join(Site).filter(
            Site.user_id == self.user_id,
            Article.status == 'published'
        ).count()

        # 统计关键词
        total_keywords = Keyword.query.filter_by(user_id=self.user_id).count()

        # 统计任务
        total_tasks = Task.query.filter_by(user_id=self.user_id).count()
        completed_tasks = Task.query.filter_by(user_id=self.user_id, status='completed').count()

        return {
            'sites': {
                'total': total_sites,
                'active': active_sites
            },
            'articles': {
                'total': total_articles,
                'published': published_articles,
                'draft': total_articles - published_articles
            },
            'keywords': {
                'total': total_keywords
            },
            'tasks': {
                'total': total_tasks,
                'completed': completed_tasks,
                'pending': total_tasks - completed_tasks
            }
        }

    def get_content_performance(self, days: int = 30) -> Dict:
        """获取内容表现分析"""
        from app.models import Article, Site

        start_date = datetime.utcnow() - timedelta(days=days)

        # 按站点统计
        site_stats = db.session.query(
            Site.name,
            func.count(Article.id).label('article_count'),
            func.sum(func.cast(Article.status == 'published', db.Integer)).label('published_count')
        ).join(Article).filter(
            Site.user_id == self.user_id,
            Article.created_at >= start_date
        ).group_by(Site.id).all()

        # 趋势数据
        trend_data = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-i-1)
            date_str = date.strftime('%Y-%m-%d')

            count = Article.query.join(Site).filter(
                Site.user_id == self.user_id,
                func.date(Article.created_at) == date_str
            ).count()

            trend_data.append({
                'date': date_str,
                'articles': count
            })

        return {
            'by_site': [{'name': s[0], 'articles': s[1], 'published': s[2]} for s in site_stats],
            'trend': trend_data
        }

    def get_keyword_performance(self) -> Dict:
        """获取关键词表现"""
        from app.models import Keyword

        keywords = Keyword.query.filter_by(user_id=self.user_id).order_by(
            Keyword.search_volume.desc()
        ).limit(20).all()

        # 分类统计
        status_counts = db.session.query(
            Keyword.status,
            func.count(Keyword.id)
        ).filter(Keyword.user_id == self.user_id).group_by(Keyword.status).all()

        return {
            'top_keywords': [
                {
                    'keyword': k.keyword,
                    'search_volume': k.search_volume,
                    'difficulty': k.difficulty,
                    'rank': k.current_rank,
                    'status': k.status
                }
                for k in keywords
            ],
            'by_status': {s[0]: s[1] for s in status_counts}
        }

    def get_task_performance(self, days: int = 30) -> Dict:
        """获取任务执行分析"""
        from app.models import Task

        start_date = datetime.utcnow() - timedelta(days=days)

        # 按类型统计
        type_stats = db.session.query(
            Task.task_type,
            func.count(Task.id).label('total'),
            func.sum(func.cast(Task.status == 'completed', db.Integer)).label('completed')
        ).filter(
            Task.user_id == self.user_id,
            Task.created_at >= start_date
        ).group_by(Task.task_type).all()

        # 平均执行时间
        completed_tasks = Task.query.filter(
            Task.user_id == self.user_id,
            Task.status == 'completed',
            Task.started_at.isnot(None),
            Task.completed_at.isnot(None)
        ).all()

        avg_duration = 0
        if completed_tasks:
            total_duration = sum(
                (t.completed_at - t.started_at).total_seconds()
                for t in completed_tasks
            )
            avg_duration = total_duration / len(completed_tasks)

        return {
            'by_type': [
                {'type': s[0], 'total': s[1], 'completed': s[2]}
                for s in type_stats
            ],
            'avg_duration_seconds': avg_duration,
            'total_completed': len(completed_tasks)
        }

    def get_seo_score_trend(self, days: int = 30) -> Dict:
        """获取SEO分数趋势"""
        from app.models import Article, Site

        # 简化的SEO评分（基于文章数量和发布状态）
        scores = []

        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-i-1)
            date_str = date.strftime('%Y-%m-%d')

            # 简单计算分数
            article_count = Article.query.join(Site).filter(
                Site.user_id == self.user_id,
                func.date(Article.created_at) <= date_str
            ).count()

            score = min(article_count * 5, 100)  # 每篇文章5分，最高100分

            scores.append({
                'date': date_str,
                'score': score
            })

        return {'trend': scores}


class ReportGenerator:
    """报告生成器"""

    def __init__(self, user_id: int):
        self.analytics = AnalyticsEngine(user_id)

    def generate_dashboard_report(self) -> str:
        """生成仪表板报告"""
        data = self.analytics.get_dashboard_summary()

        report = f"""
# SEO AIOS 数据报告

生成时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}

## 站点统计
- 总站点: {data['sites']['total']}
- 活跃站点: {data['sites']['active']}

## 文章统计
- 总文章: {data['articles']['total']}
- 已发布: {data['articles']['published']}
- 草稿: {data['articles']['draft']}

## 关键词统计
- 总关键词: {data['keywords']['total']}

## 任务统计
- 总任务: {data['tasks']['total']}
- 已完成: {data['tasks']['completed']}
- 待处理: {data['tasks']['pending']}
"""
        return report

    def generate_weekly_report(self) -> Dict:
        """生成周报"""
        summary = self.analytics.get_dashboard_summary()
        content = self.analytics.get_content_performance(days=7)
        keywords = self.analytics.get_keyword_performance()
        tasks = self.analytics.get_task_performance(days=7)

        return {
            'period': '最近7天',
            'summary': summary,
            'content': content,
            'keywords': keywords,
            'tasks': tasks,
            'generated_at': datetime.utcnow().isoformat()
        }

    def generate_monthly_report(self) -> Dict:
        """生成月报"""
        summary = self.analytics.get_dashboard_summary()
        content = self.analytics.get_content_performance(days=30)
        keywords = self.analytics.get_keyword_performance()
        tasks = self.analytics.get_task_performance(days=30)
        seo_trend = self.analytics.get_seo_score_trend(days=30)

        return {
            'period': '最近30天',
            'summary': summary,
            'content': content,
            'keywords': keywords,
            'tasks': tasks,
            'seo_trend': seo_trend,
            'generated_at': datetime.utcnow().isoformat()
        }


class MetricsCalculator:
    """指标计算器"""

    @staticmethod
    def calculate_domain_authority(sites: List) -> float:
        """计算域名权威度"""
        if not sites:
            return 0.0

        score = 0

        for site in sites:
            # 基于站点年龄、内容数量等计算
            age_days = (datetime.utcnow() - site.created_at).days if site.created_at else 0
            age_score = min(age_days / 365 * 10, 30)  # 最多30分

            # 内容分数
            content_score = len(getattr(site, 'articles', [])) * 2

            score += age_score + content_score

        return min(score / len(sites), 100)

    @staticmethod
    def calculate_content_quality(article) -> Dict:
        """计算内容质量分数"""
        score = 0
        factors = []

        # 标题长度
        title = getattr(article, 'title', '')
        if 10 <= len(title) <= 60:
            score += 20
            factors.append({'name': '标题长度', 'score': 20, 'status': 'good'})
        else:
            factors.append({'name': '标题长度', 'score': 0, 'status': 'poor'})

        # Meta描述
        meta_desc = getattr(article, 'meta_description', '')
        if 50 <= len(meta_desc) <= 160:
            score += 20
            factors.append({'name': 'Meta描述', 'score': 20, 'status': 'good'})
        else:
            factors.append({'name': 'Meta描述', 'score': 0, 'status': 'poor'})

        # 内容长度
        content = getattr(article, 'content', '')
        if len(content) >= 1000:
            score += 30
            factors.append({'name': '内容长度', 'score': 30, 'status': 'good'})
        elif len(content) >= 500:
            score += 15
            factors.append({'name': '内容长度', 'score': 15, 'status': 'medium'})
        else:
            factors.append({'name': '内容长度', 'score': 0, 'status': 'poor'})

        # 关键词
        keywords = getattr(article, 'meta_keywords', '')
        if keywords and len(keywords.split(',')) >= 3:
            score += 15
            factors.append({'name': '关键词', 'score': 15, 'status': 'good'})
        else:
            factors.append({'name': '关键词', 'score': 0, 'status': 'poor'})

        # 图片
        has_images = 'img' in content.lower() or 'image' in content.lower()
        if has_images:
            score += 15
            factors.append({'name': '图片', 'score': 15, 'status': 'good'})
        else:
            factors.append({'name': '图片', 'score': 0, 'status': 'poor'})

        return {
            'total_score': score,
            'grade': MetricsCalculator._get_grade(score),
            'factors': factors
        }

    @staticmethod
    def _get_grade(score: int) -> str:
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        else:
            return 'D'


# 导入db
from app import db
