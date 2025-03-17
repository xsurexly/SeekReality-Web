from flask import Blueprint, request, jsonify
from models import db, User
import os
from werkzeug.utils import secure_filename

profile_bp = Blueprint('profile', __name__)

# 更新用户资料
@profile_bp.route('/update-profile', methods=['POST'])
def update_profile():
    data = request.get_json()
    userid = data.get('userid')
    username = data.get('username')
    gender = data.get('gender')
    
    # 使用userid查找用户
    user = User.query.filter_by(userid=userid).first()
    if not user:
        return jsonify({
            'success': False,
            'message': '用户未找到'
        }), 404

    # 检查用户名是否已被其他用户使用
    if username != user.username:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': '用户名已被使用'
            }), 400
    try:
        user.username = username
        user.gender = gender
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '用户资料更新成功',
            'user': {
                'username': user.username,
                'gender': user.gender,
                'userid': user.userid
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': '更新失败，请稍后重试'
        }), 500

@profile_bp.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    if 'file' not in request.files:
        return jsonify({'message': '没有文件上传'}), 400
        
    file = request.files['file']
    userid = request.form.get('userid')  # 改用userid
    
    if not file or not userid:
        return jsonify({'message': '上传失败：缺少必要参数'}), 400
        
    if file.filename == '':
        return jsonify({'message': '没有选择文件'}), 400

    try:
        # 确保上传目录存在
        upload_folder = os.path.join(os.getcwd(), 'static', 'uploads', 'avatars')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        # 生成安全的文件名
        filename = secure_filename(f"avatar_{userid}_{file.filename}")
        file_path = os.path.join(upload_folder, filename)
        print(file_path)
        
        # 保存文件
        file.save(file_path)
        
        # 更新数据库
        user = User.query.filter_by(userid=userid).first()  # 使用userid查询
        if user:
            # 删除旧头像
            if user.avatar and os.path.exists(os.path.join(os.getcwd(), user.avatar.lstrip('/'))):
                try:
                    os.remove(os.path.join(os.getcwd(), user.avatar.lstrip('/')))
                except:
                    pass
                
            # 更新数据库中的头像路径
            user.avatar = f"/static/uploads/avatars/{filename}"
            db.session.commit()
            
            return jsonify({
                'message': '头像上传成功',
                'avatar': f"/static/uploads/avatars/{filename}"
            }), 200
        else:
            return jsonify({'message': '用户未找到'}), 404
            
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return jsonify({'message': f'上传失败：{str(e)}'}), 500