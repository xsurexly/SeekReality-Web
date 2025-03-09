from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from flask_mail import Message, Mail
import random
import string

auth_bp = Blueprint('auth', __name__)

mail = Mail()

def send_verification_email(email, verification_code):
    msg = Message('星眸查询密码找回验证码', recipients=[email])
    msg.body = f'您的验证码是：{verification_code}'
    mail.send(msg)

def generate_unique_userid():
    """生成8位不重复的随机userid"""
    while True:
        # 生成8位数字和字母的组合
        userid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        # 检查是否已存在
        existing_user = User.query.filter_by(userid=userid).first()
        if not existing_user:
            return userid

# 注册功能
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    # 检查是否已有用户名
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': '用户名已存在'}), 400
    
    # 生成唯一的userid
    userid = generate_unique_userid()

    hashed_password = generate_password_hash(password)  # 密码加密
    new_user = User(
        username=username, 
        password=hashed_password, 
        email=email,
        userid=userid,
        gender='男'  # 设置默认性别
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': '用户注册成功'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return jsonify({
            'success': True,
            'message': '登录成功',
            'user': {
                'username': user.username,
                'email': user.email,
                'password': user.password,
                'userid': user.userid,
                'gender': user.gender
            }
        }), 200
    else:
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    
# 请求验证码（找回密码时）
@auth_bp.route('/request-verification-code', methods=['POST'])
def request_verification_code():
    data = request.get_json()
    email = data.get('email')

    # 查找用户
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({'success': False, 'message': '邮箱错误'}), 400

    # 生成随机验证码
    verification_code = ''.join(random.choices(string.digits, k=6))
    user.verification_code = verification_code
    db.session.commit()
    print(f'verification_code: {verification_code}')

    # 发送验证码到用户邮箱
    send_verification_email(email, verification_code)

    return jsonify({'success': True, 'message': '验证码已发送'}), 200

# 修改密码
@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')
    verification_code = data.get('verificationCode')

    # 查找用户
    user = User.query.filter_by(email=email, username=username).first()
    
    if not user:
        print(f"User not found with email: {email} and username: {username}")
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 400

    # 验证当前密码
    if not check_password_hash(user.password, current_password):
        print(f"Current password is incorrect for user: {username}")
        return jsonify({
            'success': False,
            'message': '当前密码错误'
        }), 400

    # 验证验证码
    if verification_code != user.verification_code:
        print(f"Verification code mismatch. Expected: {user.verification_code}, Received: {verification_code}")
        return jsonify({
            'success': False,
            'message': '验证码错误'
        }), 400

    try:
        # 更新密码
        hashed_password = generate_password_hash(new_password)
        user.password = hashed_password
        # 清除验证码
        user.verification_code = None
        db.session.commit()

        print(f"Password changed successfully for user: {username}")

        return jsonify({
            'success': True,
            'message': '密码修改成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '修改失败，请稍后重试'
        }), 500
    

# 修改密码
@auth_bp.route('/find-password', methods=['POST'])
def find_password():
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('newPassword')
    verification_code = data.get('verificationCode')

    # 查找用户
    user = User.query.filter_by(email=email).first()
    
    if not user:
        print(f"User not found with email: {email}")
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 400

    # 验证验证码
    if verification_code != user.verification_code:
        print(f"Verification code mismatch. Expected: {user.verification_code}, Received: {verification_code}")
        return jsonify({
            'success': False,
            'message': '验证码错误'
        }), 400

    try:
        # 更新密码
        hashed_password = generate_password_hash(new_password)
        user.password = hashed_password
        # 清除验证码
        user.verification_code = None
        db.session.commit()

        print(f"Password changed successfully for user: {user.username}")

        return jsonify({
            'success': True,
            'message': '密码修改成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '修改失败，请稍后重试'
        }), 500