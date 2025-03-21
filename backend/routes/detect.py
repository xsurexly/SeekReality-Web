from flask import Blueprint, request, jsonify,json
import os
from werkzeug.utils import secure_filename
import time
from datetime import datetime
import sys
from docx import Document
import pdfplumber
import json
import logging



# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# 将上级目录添加到系统路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from detect_model import predict  # 导入模型预测函数
from models import db, DetectionHistory, Record, Conversation

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
    is_fake = 0 if fraud_probability >= 60 else 1
    return {
    'fraudProbability': fraud_probability,
    'isFake': is_fake,
    'keyPoints': [
    "内容真实性存疑" if is_fake else "新闻内容真实性较高，置信度超过60%，鉴定为真实可信新闻",
    "检测模型：Model 1"
    ]
    }


def save_detection_history(userid, detection_type, content, file_path, detection_result, detection_tool):
    """保存检测历史记录到 DetectionHistory 表"""
    try:
        # 解析检测结果
        is_fake = detection_result.get('isFake', False)
        fraud_probability = detection_result.get('fraudProbability', 0.0)
        fraud_probability =fraud_probability
        # 将 isFake 转换为 0（true）或 1（false）
        # result_value = 1 if is_fake else 0
        result_value =1 if fraud_probability>=60 else 0
        # 创建检测历史记录
        history = DetectionHistory(
            userid=userid,  # 用户 ID
            detection_type=detection_type,  # 检测类型（"text" 或 "file"）
            content=content,  # 检测内容（文本内容）
            file_path=file_path,  # 文件路径（如果是文件检测）
            result=result_value,  # 检测结果（0 表示 true，1 表示 false）
            detection_tool=detection_tool,  # 检测工具（"ai" 或 "模型"）
            score=fraud_probability,  # 置信度
            created_at=datetime.utcnow()  # 检测时间
        )

        # 保存记录到数据库
        db.session.add(history)
        db.session.commit()
        logger.info(f'成功保存检测历史记录: {history.id}')
        return history

    except Exception as e:
        logger.error(f'保存检测历史记录时发生错误: {str(e)}')
        db.session.rollback()
        return None

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

    #保存历史记录
    save_detection_history(
        userid=data.get('user_id'),  # 用户 ID
        detection_type="text",  # 检测类型为文本
        content=detection_content,  # 检测内容
        file_path=None,  # 文件路径（文本检测时为 None）
        detection_result=detection_result,  # 检测结果
        detection_tool="模型"  # 检测工具（假设使用 model1）
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
    save_detection_history(
        userid=user_id,  # 用户 ID
        detection_type="file",  # 检测类型为文件
        content=content,  # 检测内容
        file_path=save_path,  # 文件路径
        detection_result=detection_result,  # 检测结果
        detection_tool="model1"  # 检测工具（假设使用 model1）
    )

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