# SEO AIOS - 自动化SEO内容工厂

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.3+-green?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge">
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge">
</p>

SEO AIOS (Automated SEO Content Factory) 是一款强大的开源 SEO 自动化工具，帮助您自动生成 SEO 优化内容、构建网站，并通过 AI 能力管理您的数字形象。

## 功能特性

### 核心功能
- **站点管理** - 创建和管理多个网站，支持自定义模板
- **AI 内容生成** - 使用 OpenAI 或 Anthropic 生成 SEO 优化文章
- **内容改写** - 使用 AI 改写现有内容以提高独特性
- **网页抓取** - 从任何网站抓取和提取内容
- **SEO 分析** - 全面的页面和技术 SEO 分析
- **任务调度** - 自动化内容生成和发布任务

### AI 集成
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude 3)
- 每个站点可独立配置 AI 设置
- 批量内容生成

### SEO 工具
- Meta 标签优化
- 网站地图生成
- Robots.txt 管理
- Schema.org 结构化数据
- 关键词跟踪
- 技术 SEO 检查

## 快速开始

### 环境要求
- Python 3.11+
- Redis (用于 Celery 任务队列)

### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/lsaac1208/seoaios.git
cd seoaios
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境：
```bash
cp .env.example .env
# 编辑 .env 文件设置您的配置
```

5. 初始化数据库：
```bash
python run.py
# 数据库将自动创建
```

6. 运行应用：
```bash
python run.py
```

7. 打开浏览器：http://localhost:5000

### 默认登录信息
- 用户名：`admin`
- 密码：`Wl$19891208`

## 项目结构

```
seoaios/
├── app/
│   ├── routes/          # URL 路由
│   │   ├── main.py     # 仪表盘、页面
│   │   ├── auth.py     # 登录、注册
│   │   ├── sites.py    # 站点管理
│   │   ├── articles.py # 文章管理
│   │   ├── ai.py       # AI 生成
│   │   ├── seo.py      # SEO 工具
│   │   ├── tasks.py    # 任务调度
│   │   └── api.py      # REST API
│   ├── services/       # 业务逻辑
│   │   ├── site_builder.py
│   │   ├── content_generator.py
│   │   ├── content_rewriter.py
│   │   ├── crawler.py
│   │   ├── seo_analyzer.py
│   │   └── ...
│   ├── templates/      # Jinja2 模板
│   └── models.py       # SQLAlchemy 模型
├── tests/              # 测试套件
├── config.py           # 配置文件
└── run.py              # 入口文件
```

## 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | Flask 密钥 | 随机生成 |
| `DATABASE_URL` | SQLite 数据库路径 | `instance/seoaios.db` |
| `REDIS_URL` | Redis 连接地址 | `redis://localhost:6379/0` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 | - |

## API 接口

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/stats` | 统计数据 |
| GET | `/api/sites` | 站点列表 |
| GET | `/api/articles` | 文章列表 |
| GET | `/api/keywords` | 关键词列表 |
| GET | `/api/tasks` | 任务列表 |

## 技术栈

- **后端**: Flask 2.3+, SQLAlchemy
- **认证**: Flask-Login, Flask-WTF
- **任务队列**: Celery + Redis
- **AI**: OpenAI, Anthropic
- **前端**: Bootstrap 5, jQuery

## 开发测试

### 运行测试
```bash
python run_tests.py
```

### 运行完整测试
```bash
python test_full.py
```

## 许可证

MIT 许可证 - 详见 [LICENSE](./LICENSE)

## 贡献指南

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

## 问题反馈

- 🐛 问题反馈：https://github.com/lsaac1208/seoaios/issues

---

<p align="center">❤️ 为 SEO 从业者打造</p>
