# SEO AIOS - Automated SEO Content Factory

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.3+-green?style=for-the-badge&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge">
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge">
</p>

SEO AIOS (Automated SEO Content Factory) is a powerful open-source SEO automation tool that helps you automatically generate SEO-optimized content, build websites, and manage your digital presence with AI-powered capabilities.

## Features

### Core Features
- **Site Management** - Create and manage multiple websites with customizable templates
- **AI Content Generation** - Generate SEO-optimized articles using OpenAI or Anthropic
- **Content Rewriting** - Rewrite existing content with AI for uniqueness
- **Web Crawling** - Scrape and extract content from any website
- **SEO Analysis** - Comprehensive on-page and technical SEO analysis
- **Task Scheduling** - Schedule automated content generation and publishing tasks

### AI Integration
- OpenAI (GPT-3.5, GPT-4)
- Anthropic (Claude 3)
- Configurable per-site AI settings
- Batch content generation

### SEO Tools
- Meta tag optimization
- Sitemap generation
- Robots.txt management
- Schema.org markup
- Keyword tracking
- Technical SEO checks

## Installation

### Prerequisites
- Python 3.11+
- Redis (for Celery task queue)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/lsaac1208/seoaios.git
cd seoaios
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Initialize database:
```bash
python run.py
# The database will be created automatically
```

6. Run the application:
```bash
python run.py
```

7. Open browser: http://localhost:5000

### Default Login
- Username: `admin`
- Password: `Wl$19891208`

## Project Structure

```
seoaios/
├── app/
│   ├── routes/          # URL routes
│   │   ├── main.py      # Dashboard, pages
│   │   ├── auth.py      # Login, register
│   │   ├── sites.py     # Site management
│   │   ├── articles.py  # Article management
│   │   ├── ai.py        # AI generation
│   │   ├── seo.py       # SEO tools
│   │   ├── tasks.py     # Task scheduling
│   │   └── api.py       # REST API
│   ├── services/        # Business logic
│   │   ├── site_builder.py
│   │   ├── content_generator.py
│   │   ├── content_rewriter.py
│   │   ├── crawler.py
│   │   ├── seo_analyzer.py
│   │   └── ...
│   ├── templates/       # Jinja2 templates
│   └── models.py       # SQLAlchemy models
├── tests/              # Test suite
├── config.py           # Configuration
└── run.py              # Entry point
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | random |
| `DATABASE_URL` | SQLite database path | `instance/seoaios.db` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/stats` | Statistics |
| GET | `/api/sites` | List sites |
| GET | `/api/articles` | List articles |
| GET | `/api/keywords` | List keywords |
| GET | `/api/tasks` | List tasks |

## Technology Stack

- **Backend**: Flask 2.3+, SQLAlchemy
- **Auth**: Flask-Login, Flask-WTF
- **Task Queue**: Celery + Redis
- **AI**: OpenAI, Anthropic
- **Frontend**: Bootstrap 5, jQuery

## Development

### Run Tests
```bash
python run_tests.py
```

### Run Full Test Suite
```bash
python test_full.py
```

## License

MIT License - See [LICENSE](./LICENSE) for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- 🐛 Issues: https://github.com/lsaac1208/seoaios/issues

---

<p align="center">Made with ❤️ for SEO professionals</p>
