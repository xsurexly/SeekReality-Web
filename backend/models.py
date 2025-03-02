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

class newslist(db.Model):
    __tablename__ = 'news_table'

    id = db.Column(db.String(50), primary_key=True)  # 使用字符串类型以匹配API返回的ID
    ctime = db.Column(db.DateTime, nullable=True)
    title = db.Column(db.String(255), nullable=False)
    source = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    picUrl = db.Column(db.String(255), nullable=True)  # 图片URL
    url = db.Column(db.String(255), nullable=True)      # 新闻链接

    def __repr__(self):
        return f"<News {self.title}>"

# 数据库模型：存储对话记录
class Conversation(db.Model):
    """对话记录表"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    user_message = db.Column(db.String(1000), nullable=False)
    assistant_message = db.Column(db.String(1000), nullable=False)
    mode = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # 添加反向引用
    records = db.relationship('Record', backref='conversation', lazy=True)

class Record(db.Model):
    """检测记录表"""
    __tablename__ = 'records'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 显式设置自增
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id', ondelete='SET NULL'), nullable=True)
    username = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)  # 检测的新闻内容
    detection_mode = db.Column(db.String(20), nullable=False)  # 'analysis' 或 'model'
    score = db.Column(db.Integer)  # 真实性评分
    result = db.Column(db.Boolean)  # True为真实，False为虚假
    confidence = db.Column(db.Float)  # 置信度
    detailed_analysis = db.Column(db.Text)  # 详细分析
    evidence = db.Column(db.Text)  # 相关事实依据
    summary = db.Column(db.Text)  # 总结
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'username': self.username,
            'content': self.content,
            'detection_mode': self.detection_mode,
            'score': self.score,
            'result': self.result,
            'confidence': self.confidence,
            'detailed_analysis': self.detailed_analysis,
            'evidence': self.evidence,
            'summary': self.summary,
            'created_at': self.created_at.isoformat()
        }