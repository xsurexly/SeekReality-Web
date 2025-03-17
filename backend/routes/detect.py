
from flask import Blueprint, request, jsonify,json
import os
from werkzeug.utils import secure_filename
import time
from datetime import datetime
import sys
from docx import Document
import pdfplumber
# 将上级目录添加到系统路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from routes.history import save_detection_history
from detect_model import predict  # 导入模型预测函数

detect_bp = Blueprint('detect', __name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def text_detection(text):
    """使用训练好的模型进行检测"""
    predicted_class, probabilities = predict(text)

    # 模型输出为二分类（0: 真实, 1: 伪造）
    is_fake = predicted_class == 1
    fraud_probability = float(probabilities[1] * 100)

    return {
        'fraudProbability': fraud_probability,
        'isFake': is_fake,
        'keyPoints': [
            f"模型预测概率：{fraud_probability}%",
            "示例疑点：内容真实性存疑" if is_fake else "内容真实性较高",
            "检测模型：Model 1"
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

    # 执行检测
    detection_result = text_detection(data.get('text'))
    detection_content = str(data.get('text', ''))  # 确保是字符串类型

    # 保存历史记录
    # save_detection_history(
    #     user_id=data['user_id'],
    #     detection_type='text',
    #     detection_content=detection_content,
    #     result=detection_result,
    #     detect_time=datetime.now().isoformat()
    # )
    # 保存历史记录
    # save_detection_history(
    #     user_id=  data['user_id'],
    #     detection_type='text',
    #     detection_content=detection_content,
    #     result=json.dumps(detection_result),  # 将字典转换为 JSON 字符串
    #     detect_time=datetime.now().isoformat()
    # )

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

    # 读取文件内容
    try:
        content = ""
        if file.filename.endswith('.txt'):
            with open(save_path, 'r', encoding='utf-8') as f:
                content = f.read(2048)  # 最多读取2048字符
        elif file.filename.endswith('.pdf'):
            with pdfplumber.open(save_path) as pdf:
                # 遍历每一页
                for page in pdf.pages:
                    # 提取当前页的文字内容
                    text = page.extract_text()
                    if text:  # 如果提取到文字
                        content += text + '\n'
        elif file.filename.endswith('.docx'):
            doc = Document(save_path)
            content = ''
            for para in doc.paragraphs:
                content += para.text  # 提取Word文档中的文本
    except Exception as e:
        content = "无法读取文件内容"

    # 执行检测
    detection_result = text_detection(content)

    # 保存历史记录
    # save_detection_history(
    #     user_id=user_id,
    #     detection_type='file',
    #     detection_content=filename,  # 存储文件名而不是内容
    #     result=detection_result['fraudProbability'],
    #     detect_time=datetime.now().isoformat()
    # )

    return jsonify({
        'content': content,
        'success': True,
        'fraudProbability': detection_result['fraudProbability'],
        'isFake': detection_result['isFake'],
        'keyPoints': detection_result['keyPoints'],
        'savedPath': save_path
    })


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS