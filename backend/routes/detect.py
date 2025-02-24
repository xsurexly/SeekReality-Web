from flask import Blueprint, request, jsonify
import os
from werkzeug.utils import secure_filename
import time
from datetime import datetime
from routes.history import save_detection_history
import json  # 导入JSON模块，用于将复杂数据转换为字符串
from PyPDF2 import PdfReader
from docx import Document

detect_bp = Blueprint('detect', __name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def mock_detection(text):
    """模拟检测逻辑"""
    word_count = len(text)
    return {
        'fraudProbability': min(100, int(word_count * 0.2)),
        'isFake': word_count > 50,
        'keyPoints': [
            f"字数分析：{word_count} 字",
            "示例疑点：时间表述模糊" if word_count % 2 == 0 else "逻辑连贯性正常",
            "检测模型：v2.3.1（模拟）"
        ]
    }

@detect_bp.route('/text-detect', methods=['POST'])
def text_detect():
    # 参数验证
    if not request.is_json:
        return jsonify({'success': False, 'message': '请使用JSON格式请求'}), 400
    
    data = request.get_json()
    if not data or 'text' not in data or 'user_id' not in data:
        return jsonify({'success': False, 'message': '缺少必要参数'}), 400
    
    # 模拟处理延迟
    time.sleep(0.8)
    
    # 执行模拟检测
    detection_result = mock_detection(data['text'])
    detection_content = str(data.get('text', ''))  # 确保是字符串类型
    
    # 保存历史记录（需要根据实际数据库结构调整）
    save_detection_history(
        user_id=data['user_id'],
        detection_type='text',
        detection_content=detection_content,
        result=detection_result,
        detect_time=datetime.now().isoformat()
    )
    
    return jsonify({
        'success': True,
        'detectionResult': detection_result,
        'isFake': detection_result['isFake'],
        'keyPoints': detection_result['keyPoints']
    })

@detect_bp.route('/file-detect', methods=['POST'])
def file_detect():
    # 文件验证
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '未上传文件'}), 400
    
    file = request.files['file']
    user_id = request.form.get('user_id')
    
    if not user_id or file.filename == '':
        return jsonify({'success': False, 'message': '无效参数'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': '仅支持txt/pdf/docx格式'}), 400
    
    # 保存文件
    filename = f"{int(time.time())}_{secure_filename(file.filename)}"
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)
    
    # 读取文件内容（处理不同类型的文件）
    try:
        content = ""
        if file.filename.endswith('.txt'):
            with open(save_path, 'r', encoding='utf-8') as f:
                content = f.read(2048)  # 最多读取2048字符
        elif file.filename.endswith('.pdf'):
            with open(save_path, 'rb') as f:
                reader = PdfReader(f)
                content = ''
                for page in reader.pages:
                    content += page.extract_text()  # 提取PDF中的文本
        elif file.filename.endswith('.docx'):
            doc = Document(save_path)
            content = ''
            for para in doc.paragraphs:
                content += para.text  # 提取Word文档中的文本
    except Exception as e:
        content = "无法读取文件内容"
    
    # 执行模拟检测
    detection_result = mock_detection(content)
    
    # 保存历史记录
    save_detection_history(
        user_id=user_id,
        detection_type='file',
        detection_content=filename,  # 存储文件名而不是内容
        result=detection_result['fraudProbability'],
        detect_time=datetime.now().isoformat()
    )
    
    return jsonify({
        'success': True,
        'fraudProbability': detection_result['fraudProbability'],
        'isFake': detection_result['isFake'],
        'keyPoints': detection_result['keyPoints'],
        'savedPath': save_path
    })

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
