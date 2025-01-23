from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(200), nullable=True)  # 存储头像的路径
    
    def __repr__(self):
        return f"<User {self.username}>"


class DetectionHistory(db.Model):
    __tablename__ = 'detection_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    detection_type = db.Column(db.String(50), nullable=False)  # "text" or "file"
    detection_content = db.Column(db.Text, nullable=True)     # Text content for detection
    file_path = db.Column(db.String(255), nullable=True)      # File path for uploaded files
    result = db.Column(db.String(50), nullable=False)         # Detection result
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)  # Time of detection