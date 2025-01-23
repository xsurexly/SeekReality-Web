from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.detect import detect_bp
from routes.history import history_bp

# 创建 Flask 应用
app = Flask(__name__)
app.config.from_object(Config)

# 初始化数据库
db.init_app(app)

# 注册蓝图
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(profile_bp, url_prefix='/profile')
app.register_blueprint(detect_bp, url_prefix='/api')
app.register_blueprint(history_bp, url_prefix='/api')

# 数据库初始化和表创建（如果没有表时）
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
