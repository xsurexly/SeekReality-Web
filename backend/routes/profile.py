from flask import Blueprint, request, jsonify
from models import db, User
import os
from werkzeug.utils import secure_filename

profile_bp = Blueprint('profile', __name__)

# 更新用户资料
@profile_bp.route('/update-profile', methods=['POST'])
def update_profile():
    data = request.get_json()
    user_id = data.get('id')
    username = data.get('username')
    email = data.get('email')
    
    user = User.query.filter_by(id=user_id).first()
    if user:
        user.username = username
        user.email = email
        db.session.commit()
        return jsonify({
            'message': '用户资料更新成功',
            'user': {
                'username': user.username,
                'email': user.email,
            }
        }), 200
    else:
        return jsonify({'message': '用户未找到'}), 404

# 上传头像
@profile_bp.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    if 'file' not in request.files:
        return jsonify({'message': '没有文件上传'}), 400
        
    file = request.files['file']
    user_id = request.form.get('id')
    
    if file and user_id:
        # 确保上传目录存在
        upload_folder = os.path.join(os.getcwd(), 'uploads', 'avatars')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        # 生成安全的文件名
        filename = secure_filename(f"avatar_{user_id}_{file.filename}")
        file_path = os.path.join(upload_folder, filename)
        
        # 保存文件
        file.save(file_path)
        
        # 更新数据库
        user = User.query.filter_by(id=user_id).first()
        if user:
            # 删除旧头像
            if user.avatar and os.path.exists(user.avatar):
                os.remove(user.avatar)
                
            user.avatar = file_path
            db.session.commit()
            
            return jsonify({
                'message': '头像上传成功',
                'avatar': f"/uploads/avatars/{filename}"
            }), 200
        else:
            return jsonify({'message': '用户未找到'}), 404
            
    return jsonify({'message': '上传失败'}), 400
