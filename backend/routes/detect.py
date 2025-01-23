from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
from routes.history import save_detection_history

# 创建 Blueprint
detect_bp = Blueprint('detect', __name__)

# 支持的文件类型
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 确保上传文件夹存在
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 文本检测接口
@detect_bp.route('/text-detect', methods=['POST'])
def text_detect():
    data = request.json
    user_id = data.get('user_id')
    text = data.get('text', '')

    if not user_id or not text:
        return jsonify({'success': False, 'message': '缺少必要参数！'}), 400

    # 模拟检测逻辑
    result = '虚假' if len(text) % 2 == 0 else '真实'

    # 保存检测历史记录
    save_detection_history(user_id=user_id, detection_type='text', detection_content=text, result=result)

    return jsonify({'success': True, 'result': result})

@detect_bp.route('/file-detect', methods=['POST'])
def file_detect():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '未上传文件！'}), 400

    file = request.files['file']
    user_id = request.form.get('user_id')

    if not user_id or file.filename == '':
        return jsonify({'success': False, 'message': '缺少必要参数！'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': '文件类型不支持！'}), 400

    # 保存文件到服务器
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # 模拟检测逻辑
    result = '虚假' if len(filename) % 2 == 0 else '真实'

    # 保存检测历史记录
    save_detection_history(user_id=user_id, detection_type='file', file_path=file_path, result=result)

    return jsonify({'success': True, 'result': result, 'file_path': file_path})