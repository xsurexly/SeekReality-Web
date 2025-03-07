from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False,unique=True)
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

#用于ai助手的对话和检测历史记录
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

class ReadHistory(db.Model):
    """阅读历史记录表"""
    __tablename__ = 'read_history'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), db.ForeignKey('users.username', ondelete='CASCADE'), nullable=False)  # 设置为外键
    news_id = db.Column(db.String(50), db.ForeignKey('news_table.id', ondelete='CASCADE'))
    read_time = db.Column(db.Integer, default=0)  # 阅读时长（秒）
    last_read_at = db.Column(db.DateTime, default=datetime.utcnow)  # 最后阅读时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 首次阅读时间

    # 关联关系
    user = db.relationship('User', backref=db.backref('read_histories', lazy=True))
    news = db.relationship('Newslist', backref=db.backref('read_histories', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'news_id': self.news_id,
            'read_time': self.read_time,
            'last_read_at': self.last_read_at,
            'created_at': self.created_at,
        }
#用于新闻信息的存储和阅读信息的存储
class Newslist(db.Model):
    __tablename__ = 'news_table'

    id = db.Column(db.String(50), primary_key=True)
    ctime = db.Column(db.DateTime, nullable=True)
    title = db.Column(db.String(255), nullable=False)
    source = db.Column(db.String(255), nullable=True)
    content = db.Column(db.Text, nullable=True)
    picUrl = db.Column(db.String(255), nullable=True)
    url = db.Column(db.String(255), nullable=True)
    fake_score = db.Column(db.Float, default=0.0)  # 虚假度评分 (0-1)
    category = db.Column(db.String(255), nullable=True)#新闻类型的label
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'ctime': self.ctime.strftime('%Y-%m-%d %H:%M') if self.ctime else None,
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'picUrl': self.picUrl,
            'url': self.url,
            'fake_score': self.fake_score,
            'category': self.category,
        }

class Newsread(db.Model):
    __tablename__ = 'readnews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 确保这里设置了 autoincrement=True
    username = db.Column(db.String(50), nullable=False)
    news_id = db.Column(db.String(50), db.ForeignKey('news_table.id', ondelete='CASCADE'))
    is_finished = db.Column(db.Boolean, default=False)  # 是否读完
    is_favorite = db.Column(db.Boolean, default=False)  # 是否收藏

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'username': self.username,
            'news_id': self.news_id,
            'is_finished': self.is_finished,
            'is_favorite': self.is_favorite,
        }
