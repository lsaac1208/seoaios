"""
SEO AIOS 辅助函数
Helper Functions
"""

import re
import unicodedata
from urllib.parse import urlparse, urljoin


def slugify(text, max_length=200):
    """
    将文本转换为URL友好的slug

    Args:
        text: 输入文本
        max_length: 最大长度

    Returns:
        slug字符串
    """
    if not text:
        return ''

    # 移除重音符号
    text = unicodedata.normalize('NFKD', text)
    text = ''.join([c for c in text if not unicodedata.combining(c)])

    # 转小写
    text = text.lower()

    # 替换特殊字符
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    text = text.strip('-')

    # 截断
    if len(text) > max_length:
        text = text[:max_length].rsplit('-', 1)[0]

    return text


def validate_url(url):
    """
    验证URL格式

    Args:
        url: URL字符串

    Returns:
        布尔值
    """
    if not url:
        return False
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def get_domain(url):
    """
    从URL提取域名

    Args:
        url: URL字符串

    Returns:
        域名
    """
    if not url:
        return ''
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except:
        return ''


def is_internal_link(url, base_domain):
    """
    判断是否为内部链接

    Args:
        url: 链接URL
        base_domain: 基础域名

    Returns:
        布尔值
    """
    if not url or not base_domain:
        return False

    parsed = urlparse(url)
    if parsed.netloc:
        return parsed.netloc == base_domain or parsed.netloc.endswith('.' + base_domain)
    return True


def extract_keywords(text, min_length=2, max_keywords=10):
    """
    从文本中提取关键词

    Args:
        text: 输入文本
        min_length: 最小关键词长度
        max_keywords: 最大关键词数量

    Returns:
        关键词列表
    """
    if not text:
        return []

    # 简单实现 - 可以使用TF-IDF等更复杂方法
    import re
    from collections import Counter

    # 分词
    words = re.findall(r'\b\w+\b', text.lower())

    # 过滤停用词
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what',
        'which', 'who', 'whom', 'when', 'where', 'why', 'how', 'all', 'each',
        'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
        'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
        'very', 'just', '也', '的', '了', '在', '是', '我', '有', '和', '就',
        '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要',
        '去', '你', '会', '着', '没有', '看', '好', '自己', '这'
    }

    # 过滤
    words = [w for w in words if len(w) >= min_length and w not in stop_words]

    # 统计频率
    counter = Counter(words)

    # 返回top关键词
    return [word for word, count in counter.most_common(max_keywords)]


def calculate_readability(text):
    """
    计算文本可读性得分

    Args:
        text: 输入文本

    Returns:
        可读性得分(0-100)
    """
    if not text:
        return 0

    import re

    # 句子数
    sentences = re.split(r'[.!?。！？]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    sentence_count = len(sentences) or 1

    # 单词数
    words = re.findall(r'\b\w+\b', text)
    word_count = len(words) or 1

    # 字符数
    char_count = len(text.replace(' ', ''))

    # 平均句子长度
    avg_sentence_length = word_count / sentence_count

    # 平均单词长度
    avg_word_length = char_count / word_count

    # 简单的可读性公式
    score = 100 - (avg_sentence_length * 0.5) - (avg_word_length * 10)

    return max(0, min(100, int(score)))


def generate_meta_description(content, max_length=160):
    """
    从内容生成meta description

    Args:
        content: 文章内容
        max_length: 最大长度

    Returns:
        meta description
    """
    if not content:
        return ''

    # 移除HTML标签
    import re
    text = re.sub(r'<[^>]+>', '', content)

    # 移除多余空白
    text = ' '.join(text.split())

    # 截断
    if len(text) > max_length:
        text = text[:max_length].rsplit(' ', 1)[0] + '...'

    return text


def calculate_keyword_density(text, keyword):
    """
    计算关键词密度

    Args:
        text: 文本内容
        keyword: 关键词

    Returns:
        密度百分比
    """
    if not text or not keyword:
        return 0.0

    import re

    # 分词
    words = re.findall(r'\b\w+\b', text.lower())
    total_words = len(words)

    if total_words == 0:
        return 0.0

    # 计算关键词出现次数
    keyword_lower = keyword.lower()
    keyword_count = sum(1 for w in words if keyword_lower in w)

    return round((keyword_count / total_words) * 100, 2)


def format_file_size(size_bytes):
    """
    格式化文件大小

    Args:
        size_bytes: 字节数

    Returns:
        格式化的大小字符串
    """
    if not size_bytes:
        return '0 B'

    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    size = float(size_bytes)

    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1

    return f'{size:.2f} {units[i]}'


def generate_random_string(length=32):
    """
    生成随机字符串

    Args:
        length: 长度

    Returns:
        随机字符串
    """
    import secrets
    import string

    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))
