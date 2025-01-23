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
        return jsonify({'message': '用户资料更新成功'}), 200
    else:
        return jsonify({'message': '用户未找到'}), 404

# 上传头像
@profile_bp.route('/upload-avatar', methods=['POST'])
def upload_avatar():
    user_id = request.form.get('id')
    avatar = request.files.get('avatar')
    
    if avatar:
        filename = secure_filename(avatar.filename)
        avatar_path = os.path.join('uploads', filename)
        avatar.save(avatar_path)
        
        user = User.query.filter_by(id=user_id).first()
        if user:
            user.avatar = avatar_path
            db.session.commit()
            return jsonify({'message': '头像上传成功', 'avatar': avatar_path}), 200
        else:
            return jsonify({'message': '用户未找到'}), 404
    return jsonify({'message': '没有选择头像文件'}), 400
