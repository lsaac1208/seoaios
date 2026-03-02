"""
SEO AIOS 模板过滤器
Template Filters
"""

from datetime import datetime, timedelta
import re
from urllib.parse import urlparse


def format_datetime(value, format='%Y-%m-%d %H:%M'):
    """格式化日期时间"""
    if value is None:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except:
            return value
    if isinstance(value, datetime):
        return value.strftime(format)
    return value


def truncate_html(text, length=200, suffix='...'):
    """截断HTML文本"""
    if not text:
        return ''
    # 简单去除HTML标签后截断
    text = re.sub(r'<[^>]+>', '', text)
    if len(text) <= length:
        return text
    return text[:length] + suffix


def domain_from_url(url):
    """从URL提取域名"""
    if not url:
        return ''
    try:
        parsed = urlparse(url)
        return parsed.netloc or parsed.path.split('/')[0]
    except:
        return ''


def file_size(bytes_value):
    """格式化文件大小"""
    if not bytes_value:
        return '0 B'
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    size = float(bytes_value)
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return f'{size:.2f} {units[i]}'


def time_ago(dt):
    """返回相对时间"""
    if not dt:
        return ''
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except:
            return dt

    now = datetime.utcnow()
    if dt.tzinfo:
        from datetime import timezone
        now = datetime.now(timezone.utc)

    delta = now - dt

    if delta < timedelta(minutes=1):
        return '刚刚'
    elif delta < timedelta(hours=1):
        return f'{int(delta.total_seconds() / 60)}分钟前'
    elif delta < timedelta(days=1):
        return f'{int(delta.total_seconds() / 3600)}小时前'
    elif delta < timedelta(days=30):
        return f'{int(delta.days)}天前'
    elif delta < timedelta(days=365):
        return f'{int(delta.days / 30)}个月前'
    else:
        return f'{int(delta.days / 365)}年前'
