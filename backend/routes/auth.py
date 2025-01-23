from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

# 注册功能
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    # 检查是否已有用户名
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': '用户名已存在'}), 400
    
    hashed_password = generate_password_hash(password)  # 密码加密
    new_user = User(username=username, password=hashed_password, email=email)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': '用户注册成功'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):  # 验证密码
        return jsonify({'message': '登录成功'}), 200
    else:
        return jsonify({'message': '用户名或密码错误'}), 401