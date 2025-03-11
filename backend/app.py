from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_mail import Mail
from config import Config
from models import db
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.detect import detect_bp
from routes.history import detection_history_bp
from routes.aihelper import aihelper_bp
from routes.newsget import news_bp
from routes.read_history import read_history_bp
# 创建 Flask 应用
app = Flask(__name__, static_folder='static')
app.config.from_object(Config)

CORS(app)
mail = Mail(app)
db.init_app(app)

with app.app_context():
    db.create_all()

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(profile_bp, url_prefix='/profile')
app.register_blueprint(detect_bp, url_prefix='/api')
app.register_blueprint(detection_history_bp, url_prefix='/history')
app.register_blueprint(aihelper_bp, url_prefix='/aihelper')
app.register_blueprint(news_bp, url_prefix='/news')
app.register_blueprint(read_history_bp, url_prefix='/readhistory')

# 添加静态文件服务路由
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True)
