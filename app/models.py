"""
SEO AIOS 数据库模型
Automated SEO Content Factory - Database Models
"""

from datetime import datetime
from typing import List
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db
import json


class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(80))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # 关联
    sites = db.relationship('Site', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    articles = db.relationship('Article', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    keywords = db.relationship('Keyword', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Site(db.Model):
    """站点模型"""
    __tablename__ = 'sites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    domain = db.Column(db.String(500), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    keywords = db.Column(db.Text)  # 逗号分隔
    template = db.Column(db.String(50), default='default')
    status = db.Column(db.String(20), default='active')  # active, inactive, pending
    output_type = db.Column(db.String(20), default='static')  # static, dynamic
    output_path = db.Column(db.String(500))
    language = db.Column(db.String(10), default='zh-CN')
    timezone = db.Column(db.String(50), default='Asia/Shanghai')
    favicon = db.Column(db.String(500))
    logo = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # SEO配置
    seo_config_id = db.Column(db.Integer, db.ForeignKey('seo_configs.id'))
    ai_config_id = db.Column(db.Integer, db.ForeignKey('ai_configs.id'))

    # 关联
    pages = db.relationship('Page', backref='site', lazy='dynamic', cascade='all, delete-orphan')
    articles = db.relationship('Article', backref='site', lazy='dynamic', cascade='all, delete-orphan')
    seo_config = db.relationship('SeoConfig', backref='site', uselist=False, cascade='all, delete-orphan', foreign_keys='SeoConfig.site_id')
    ai_config = db.relationship('AiConfig', backref='site', uselist=False, cascade='all, delete-orphan', foreign_keys='AiConfig.site_id')

    def get_keywords_list(self):
        """获取关键词列表"""
        if self.keywords:
            return [k.strip() for k in self.keywords.split(',') if k.strip()]
        return []

    def __repr__(self):
        return f'<Site {self.name}>'


class Page(db.Model):
    """页面模型"""
    __tablename__ = 'pages'

    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text)
    template = db.Column(db.String(50))
    page_type = db.Column(db.String(20))  # home, page, article, category, tag, about, contact
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(500))
    meta_keywords = db.Column(db.String(500))
    featured_image = db.Column(db.String(500))
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    order = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)

    # 关联
    seo_data = db.relationship('PageSeoData', backref='page', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Page {self.title}>'


class PageSeoData(db.Model):
    """页面SEO数据"""
    __tablename__ = 'page_seo_data'

    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'), nullable=False, index=True)
    h1_tags = db.Column(db.Text)  # JSON格式存储
    headings_structure = db.Column(db.Text)  # JSON格式存储
    internal_links = db.Column(db.Text)  # JSON格式存储
    external_links = db.Column(db.Text)  # JSON格式存储
    images_count = db.Column(db.Integer, default=0)
    images_with_alt = db.Column(db.Integer, default=0)
    word_count = db.Column(db.Integer, default=0)
    keyword_density = db.Column(db.Float, default=0.0)
    schema_markup = db.Column(db.Text)  # JSON-LD
    last_analyzed = db.Column(db.DateTime)

    def get_h1_tags(self):
        if self.h1_tags:
            return json.loads(self.h1_tags)
        return []

    def set_h1_tags(self, tags):
        self.h1_tags = json.dumps(tags)

    def __repr__(self):
        return f'<PageSeoData {self.id}>'


class Article(db.Model):
    """文章模型"""
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(500))
    featured_image = db.Column(db.String(500))
    status = db.Column(db.String(20), default='draft')  # draft, published, scheduled, archived
    visibility = db.Column(db.String(20), default='public')  # public, private, password
    password = db.Column(db.String(100))
    allow_comments = db.Column(db.Boolean, default=True)
    comment_count = db.Column(db.Integer, default=0)

    # SEO字段
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(500))
    meta_keywords = db.Column(db.String(500))

    # 分类和标签
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    tags = db.Column(db.String(500))  # 逗号分隔

    # 来源信息
    source_url = db.Column(db.String(500))
    source_name = db.Column(db.String(200))
    is_rewritten = db.Column(db.Boolean, default=False)
    original_content = db.Column(db.Text)

    # 统计
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)

    # 时间
    published_at = db.Column(db.DateTime)
    scheduled_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联
    category = db.relationship('Category', backref='articles')
    seo_data = db.relationship('ArticleSeoData', backref='article', uselist=False, cascade='all, delete-orphan')

    def get_tags_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(',') if t.strip()]
        return []

    def __repr__(self):
        return f'<Article {self.title}>'


class ArticleSeoData(db.Model):
    """文章SEO数据"""
    __tablename__ = 'article_seo_data'

    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False, index=True)

    # 内容分析
    word_count = db.Column(db.Integer, default=0)
    heading_count = db.Column(db.Integer, default=0)
    paragraph_count = db.Column(db.Integer, default=0)
    image_count = db.Column(db.Integer, default=0)
    image_with_alt_count = db.Column(db.Integer, default=0)
    link_count = db.Column(db.Integer, default=0)
    internal_link_count = db.Column(db.Integer, default=0)
    external_link_count = db.Column(db.Integer, default=0)

    # 关键词分析
    primary_keyword = db.Column(db.String(200))
    keyword_density = db.Column(db.Float, default=0.0)
    keyword_in_title = db.Column(db.Boolean, default=False)
    keyword_in_meta = db.Column(db.Boolean, default=False)
    keyword_in_first_para = db.Column(db.Boolean, default=False)
    keyword_in_headings = db.Column(db.Boolean, default=False)

    # SEO得分
    seo_score = db.Column(db.Float, default=0.0)
    readability_score = db.Column(db.Float, default=0.0)

    # 结构化数据
    schema_markup = db.Column(db.Text)  # JSON-LD

    last_analyzed = db.Column(db.DateTime)

    def __repr__(self):
        return f'<ArticleSeoData {self.id}>'


class Category(db.Model):
    """分类模型"""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.String(500))
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联
    parent = db.relationship('Category', remote_side=[id], backref='children')
    seo_config = db.relationship('CategorySeoConfig', backref='category', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Category {self.name}>'


class CategorySeoConfig(db.Model):
    """分类SEO配置"""
    __tablename__ = 'category_seo_configs'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, index=True)
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.String(500))
    meta_keywords = db.Column(db.String(500))
    schema_markup = db.Column(db.Text)

    def __repr__(self):
        return f'<CategorySeoConfig {self.id}>'


class Keyword(db.Model):
    """关键词模型"""
    __tablename__ = 'keywords'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=True, index=True)
    keyword = db.Column(db.String(200), nullable=False, index=True)
    search_volume = db.Column(db.Integer, default=0)  # 搜索量
    difficulty = db.Column(db.Float, default=0.0)  # 竞争难度
    cpc = db.Column(db.Float, default=0.0)  # CPC
    intent = db.Column(db.String(50))  # informational, navigational, transactional, commercial

    # 跟踪数据
    current_rank = db.Column(db.Integer, default=0)
    previous_rank = db.Column(db.Integer, default=0)
    rank_changed = db.Column(db.Integer, default=0)
    last_checked = db.Column(db.DateTime)

    # 状态
    status = db.Column(db.String(20), default='active')  # active, paused, removed
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Keyword {self.keyword}>'


class Task(db.Model):
    """任务模型"""
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=True, index=True)

    name = db.Column(db.String(200), nullable=False)
    task_type = db.Column(db.String(50), nullable=False)  # crawl, generate, publish, analyze, backup
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed, cancelled
    priority = db.Column(db.Integer, default=5)  # 1-10

    # 任务配置
    config = db.Column(db.Text)  # JSON格式存储任务配置
    schedule = db.Column(db.String(100))  # cron表达式

    # 进度
    progress = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    message = db.Column(db.String(500))

    # 结果
    result = db.Column(db.Text)
    error_message = db.Column(db.Text)

    # Celery任务ID
    celery_task_id = db.Column(db.String(100))

    # 时间
    scheduled_at = db.Column(db.DateTime)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关联
    user = db.relationship('User', backref=db.backref('tasks', lazy='dynamic'))
    site = db.relationship('Site', backref=db.backref('tasks', lazy='dynamic'))

    def get_config(self):
        if self.config:
            return json.loads(self.config)
        return {}

    def set_config(self, config_dict):
        self.config = json.dumps(config_dict)

    def __repr__(self):
        return f'<Task {self.name}>'


class SeoConfig(db.Model):
    """SEO配置模型"""
    __tablename__ = 'seo_configs'

    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False, index=True, unique=True)

    # 基础SEO
    default_title = db.Column(db.String(200))
    default_description = db.Column(db.String(500))
    default_keywords = db.Column(db.String(500))

    # robots.txt
    robots_txt = db.Column(db.Text)
    allow_robots = db.Column(db.Boolean, default=True)

    # 站点地图
    enable_sitemap = db.Column(db.Boolean, default=True)
    sitemap_priority = db.Column(db.Float, default=0.8)

    # 结构化数据
    enable_schema = db.Column(db.Boolean, default=True)
    schema_type = db.Column(db.String(50), default='Organization')  # Organization, WebSite, Blog, Article

    # Open Graph
    og_enabled = db.Column(db.Boolean, default=True)
    og_image = db.Column(db.String(500))

    # Twitter Card
    twitter_card_enabled = db.Column(db.Boolean, default=True)
    twitter_card_type = db.Column(db.String(20), default='summary_large_image')

    # Canonical
    auto_canonical = db.Column(db.Boolean, default=True)

    # 重定向
    trailing_slash = db.Column(db.String(10))  # none, always, no-redirect
    www_redirect = db.Column(db.Boolean, default=False)

    # 面包屑
    breadcrumb_separator = db.Column(db.String(10), default='›')
    breadcrumb_home = db.Column(db.String(50), default='首页')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SeoConfig {self.id}>'


class AiConfig(db.Model):
    """AI配置模型"""
    __tablename__ = 'ai_configs'

    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=False, index=True, unique=True)

    # Provider配置
    provider = db.Column(db.String(50), default='openai')  # openai, anthropic, deepseek, gemini, azure, custom

    # OpenAI配置
    openai_api_key = db.Column(db.String(255))
    openai_api_base = db.Column(db.String(255))
    openai_model = db.Column(db.String(50), default='gpt-3.5-turbo')

    # Anthropic配置
    anthropic_api_key = db.Column(db.String(255))
    anthropic_model = db.Column(db.String(50), default='claude-3-haiku-20240307')

    # DeepSeek配置
    deepseek_api_key = db.Column(db.String(255))
    deepseek_model = db.Column(db.String(50), default='deepseek-chat')

    # Gemini配置
    gemini_api_key = db.Column(db.String(255))
    gemini_model = db.Column(db.String(50), default='gemini-pro')

    # Azure OpenAI配置
    azure_api_key = db.Column(db.String(255))
    azure_api_base = db.Column(db.String(255))
    azure_deployment = db.Column(db.String(50))
    azure_api_version = db.Column(db.String(50), default='2024-02-01')

    # 自定义API配置
    custom_api_key = db.Column(db.String(255))
    custom_api_base = db.Column(db.String(255))
    custom_model = db.Column(db.String(50))

    # 内容生成配置
    default_article_length = db.Column(db.Integer, default=1500)
    default_title_length = db.Column(db.Integer, default=60)
    default_description_length = db.Column(db.Integer, default=160)
    temperature = db.Column(db.Float, default=0.7)
    top_p = db.Column(db.Float, default=1.0)
    max_tokens = db.Column(db.Integer, default=4000)

    # 改写配置
    rewrite_style = db.Column(db.String(50), default='semantic')  # semantic, paraphrasing, humanize
    rewrite_level = db.Column(db.Integer, default=3)  # 1-5

    # Prompt模板
    generation_prompt = db.Column(db.Text)
    rewrite_prompt = db.Column(db.Text)

    # 高级配置
    enable_cache = db.Column(db.Boolean, default=True)
    cache_ttl = db.Column(db.Integer, default=3600)  # 缓存时间（秒）
    enable_streaming = db.Column(db.Boolean, default=False)  # 流式输出
    fallback_provider = db.Column(db.String(50))  # 备用提供商

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_available_providers(self) -> List[dict]:
        """获取可用的AI提供商列表"""
        providers = [
            {'id': 'openai', 'name': 'OpenAI', 'models': ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo']},
            {'id': 'anthropic', 'name': 'Anthropic Claude', 'models': ['claude-3-5-sonnet-20241022', 'claude-3-opus-20240229', 'claude-3-haiku-20240307']},
            {'id': 'deepseek', 'name': 'DeepSeek', 'models': ['deepseek-chat', 'deepseek-coder']},
            {'id': 'gemini', 'name': 'Google Gemini', 'models': ['gemini-1.5-pro', 'gemini-1.5-flash', 'gemini-pro']},
            {'id': 'azure', 'name': 'Azure OpenAI', 'models': ['gpt-4o', 'gpt-4-turbo', 'gpt-35-turbo']},
            {'id': 'custom', 'name': '自定义API', 'models': []},
        ]
        return providers

    def __repr__(self):
        return f'<AiConfig {self.id}>'


class CrawlLog(db.Model):
    """爬虫日志"""
    __tablename__ = 'crawl_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'), nullable=True, index=True)

    url = db.Column(db.String(1000), nullable=False)
    domain = db.Column(db.String(500), nullable=False, index=True)
    status_code = db.Column(db.Integer)
    title = db.Column(db.String(200))
    meta_description = db.Column(db.String(500))
    h1_tags = db.Column(db.Text)
    word_count = db.Column(db.Integer)
    image_count = db.Column(db.Integer)
    link_count = db.Column(db.Integer)
    external_links = db.Column(db.Text)  # JSON
    internal_links = db.Column(db.Text)  # JSON

    # 错误信息
    error_message = db.Column(db.Text)
    error_count = db.Column(db.Integer, default=0)

    # 响应时间
    response_time = db.Column(db.Float, default=0.0)

    # 爬取深度
    depth = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CrawlLog {self.url}>'


class Setting(db.Model):
    """系统设置"""
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False, unique=True, index=True)
    value = db.Column(db.Text)
    value_type = db.Column(db.String(20), default='string')  # string, int, float, bool, json
    description = db.Column(db.String(500))
    category = db.Column(db.String(50), default='general')
    is_public = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_value(self):
        """获取解析后的值"""
        if self.value_type == 'int':
            return int(self.value or 0)
        elif self.value_type == 'float':
            return float(self.value or 0)
        elif self.value_type == 'bool':
            return self.value in ('true', 'True', '1', 'yes')
        elif self.value_type == 'json':
            return json.loads(self.value or '{}')
        return self.value

    def set_value(self, value):
        """设置值"""
        if isinstance(value, bool):
            self.value_type = 'bool'
            self.value = 'true' if value else 'false'
        elif isinstance(value, (int, float)):
            self.value_type = type(value).__name__
            self.value = str(value)
        elif isinstance(value, dict):
            self.value_type = 'json'
            self.value = json.dumps(value)
        else:
            self.value = str(value)

    def __repr__(self):
        return f'<Setting {self.key}>'
