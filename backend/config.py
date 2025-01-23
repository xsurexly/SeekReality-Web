import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:123456@localhost/fake_news_db'
    UPLOAD_FOLDER = 'uploads/'  # 上传文件夹路径
    SECRET_KEY = 'your_secret_key'  # 用于 session 加密等