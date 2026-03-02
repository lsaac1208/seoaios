"""
SEO AIOS - Automated SEO Content Factory
Run the application
"""

import os
from app import create_app

# 创建应用实例
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # 确保上传目录存在
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)
    os.makedirs(app.config.get('OUTPUT_DIR', 'output'), exist_ok=True)

    # 启动应用
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', True)
    )
