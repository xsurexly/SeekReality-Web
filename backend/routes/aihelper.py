# 此处新闻的llm对话，支持普通对话和新闻分析（文件上传或对话）
# 对话内容将会存储到conversations表，若是新闻分析还会存储到records表里
# 模型待微调
# 似乎使用的是fetch方法，感觉可以修改
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from openai import OpenAI
import docx
from PyPDF2 import PdfReader
import io
from models import db, Conversation, Record
import os
import json
import re
from .history import save_detection_record  # 添加这行导入

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aihelper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建蓝图
aihelper_bp = Blueprint('aihelper', __name__)

# 初始化 OpenAI 客户端
# 确保API密钥和基础URL正确
api_key = os.getenv('OPENAI_API_KEY', 'sk-9f8d92679a634dbc849338c0b36842b1')
base_url = os.getenv('OPENAI_BASE_URL', "https://api.deepseek.com/v1")

# 配置代理设置
proxy = os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY')
if proxy:
    logger.info(f"使用代理: {proxy}")
    os.environ['HTTPS_PROXY'] = proxy
    os.environ['HTTP_PROXY'] = proxy

if not api_key:
    logger.error("未设置OPENAI_API_KEY环境变量")
    api_available = False
else:
    logger.info(f"初始化OpenAI客户端，使用API密钥: {api_key[:5]}...{api_key[-5:]}，基础URL: {base_url}")
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=30.0,  # 设置30秒超时
            max_retries=3  # 添加重试次数
        )
        # 测试连接
        test_response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[{"role": "user", "content": "Test connection"}],
            max_tokens=5,
        )
        logger.info("OpenAI客户端初始化成功")
        api_available = True
    except Exception as e:
        logger.error(f"OpenAI客户端初始化失败: {str(e)}")
        api_available = False

# 系统提示词
SYSTEM_PROMPTS = {
    'chat': """你是一位友好的AI助手，能够进行日常对话和回答问题。请用简洁、准确、友好的方式回应用户。""",

    'analysis': """你是一位专业的虚假新闻检测专家，拥有丰富的新闻事实核查经验。在分析新闻时，你会从以下几个方面进行深入分析：
1. 信息来源可靠性：评估新闻来源的可信度，检查作者身份和专业背景，验证引用的数据和专家观点
2. 内容真实性：核实关键事实和数据，检查时间线的合理性，对比其他可靠媒体的报道
3. 情感倾向：分析语言是否客观中立，检测煽动性或误导性表达，评估标题与内容的一致性
4. 上下文完整性：考虑新闻的完整背景，检查是否有重要信息被省略，评估叙述的平衡性"""
}

# 分析格式提示词
ANALYSIS_FORMAT = """请按照以下格式提供分析：
真实性评分：[0-100分]
详细分析：
1. 信息来源可靠性：[评估新闻来源的可信度、作者身份等]
2. 内容真实性：[核实关键事实和数据的准确性]
3. 情感倾向：[分析语言是否客观中立，是否存在煽动性表达]
4. 上下文完整性：[评估新闻背景信息的完整性]
相关事实依据：
- [第一条事实依据及来源]
- [第二条事实依据及来源]
- [第三条事实依据及来源]
总结：
[简要总结分析结论]"""


def get_response(messages, stream=False):
    """获取AI助手回复"""
    if not api_available:
        logger.error("API不可用，无法获取回复")
        raise Exception("AI服务暂时不可用，请稍后重试")

    try:
        # 设置超时时间为30秒
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages,
            stream=stream,
            temperature=0.7,
            max_tokens=6000,
            timeout=180,
        )

        if not response or not response.choices:
            logger.error("AI服务返回空响应")
            raise Exception("AI服务返回空响应")

        return response
    except Exception as e:
        logger.error(f"API 请求失败: {str(e)}")
        # 返回更友好的错误信息
        if "timeout" in str(e).lower():
            raise Exception("AI服务响应超时，请稍后重试")
        elif "connection" in str(e).lower() or "proxy" in str(e).lower():
            raise Exception("无法连接到AI服务，请检查网络连接或代理设置")
        elif "ssl" in str(e).lower():
            raise Exception("SSL连接错误，请检查网络设置")
        else:
            raise Exception(f"AI服务请求失败: {str(e)}")


def save_conversation(user_message, assistant_message, mode='chat', username=None):
    """保存对话记录"""
    try:
        # 使用传入的 username 参数，如果没有则默认为'未登录用户'
        if username is None:
            username = '未登录用户'

        conversation = Conversation(
            user_message=user_message,
            assistant_message=assistant_message,
            mode=mode,
            timestamp=datetime.utcnow(),
            username=username
        )
        db.session.add(conversation)
        db.session.commit()
        logger.info(f"对话记录已保存: {conversation.id}, 用户: {username}")
    except Exception as e:
        logger.error(f"保存对话记录失败: {str(e)}")
        db.session.rollback()


def extract_text_from_docx(file_stream):
    """从 Word 文档提取文本"""
    try:
        doc = docx.Document(file_stream)
        text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        logger.info("成功从Word文档提取文本")
        return text
    except Exception as e:
        logger.error(f"Word文档处理错误: {str(e)}")
        raise Exception("无法读取Word文档，请确保文件格式正确")


def extract_text_from_pdf(file_stream):
    """从 PDF 文档提取文本"""
    try:
        reader = PdfReader(file_stream)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
        logger.info("成功从PDF文档提取文本")
        return text
    except Exception as e:
        logger.error(f"PDF处理错误: {str(e)}")
        raise Exception("无法读取PDF文档，请确保文件格式正确")


@aihelper_bp.route('/talk', methods=['POST'])
def analyze_message():
    """处理用户消息"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        conversation_mode = data.get('conversation_mode', 'chat')
        needs_analysis = data.get('needs_analysis', False)
        username = data.get('username', '未登录用户')

        if not user_message:
            return jsonify({"error": "消息不能为空"}), 400

        # 构建消息
        messages = [{"role": "system", "content": SYSTEM_PROMPTS[conversation_mode]}]

        if conversation_mode == 'analysis' and needs_analysis:
            prompt = f"""请分析以下新闻内容的真实性：
{user_message}
{ANALYSIS_FORMAT}"""
            messages.append({"role": "user", "content": prompt})
        else:
            messages.append({"role": "user", "content": user_message})

        # 获取回复
        response = get_response(messages)
        if not response:
            return jsonify({"error": "AI服务暂时不可用，请稍后重试"}), 503

        assistant_message = response.choices[0].message.content

        # 开始数据库事务
        try:
            # 创建新的对话记录
            conversation = Conversation(
                user_message=user_message,
                assistant_message=assistant_message,
                mode=conversation_mode,
                timestamp=datetime.utcnow(),
                username=username
            )

            # 添加到会话并获取ID
            db.session.add(conversation)
            db.session.flush()  # 刷新会话以获取ID，但还不提交

            conversation_id = conversation.id
            logger.info(f"准备保存对话记录: {conversation_id}, 用户: {username}")

            # 如果是分析模式，创建检测记录
            if conversation_mode == 'analysis' and needs_analysis:
                record = save_detection_record(
                    conversation_id,
                    username,
                    user_message,
                    'analysis',
                    assistant_message
                )
                if not record:
                    logger.error('保存检测记录失败')
                    db.session.rollback()
                    return jsonify({"error": "保存检测记录失败", "response": assistant_message}), 200

            # 提交事务
            db.session.commit()
            logger.info(f"成功保存对话记录和检测记录: {conversation_id}")

            return jsonify({"response": assistant_message}), 200

        except Exception as e:
            logger.error(f"数据库操作失败: {str(e)}")
            db.session.rollback()
            return jsonify({"error": "保存记录失败", "response": assistant_message}), 200

    except Exception as e:
        logger.error(f"处理消息错误: {str(e)}")
        return jsonify({"error": "服务器内部错误，请稍后重试"}), 500


@aihelper_bp.route('/upload', methods=['POST'])
def analyze_file():
    """处理文件上传和分析"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "没有上传文件"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "未选择文件"}), 400

        # 获取用户名，从表单数据中获取
        username = request.form.get('username', '未登录用户')

        # 检查文件大小
        file_content = file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB限制
            return jsonify({"error": "文件大小超过限制（最大10MB）"}), 400

        file_stream = io.BytesIO(file_content)

        # 根据文件类型提取文本
        if file.filename.endswith('.docx'):
            text = extract_text_from_docx(file_stream)
        elif file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_stream)
        else:
            return jsonify({"error": "仅支持.docx和.pdf文件"}), 400

        if not text.strip():
            return jsonify({"error": "文件内容为空"}), 400

        # 构建分析提示
        prompt = f"""请分析以下新闻内容的真实性：
{text}
{ANALYSIS_FORMAT}"""

        messages = [
            {"role": "system", "content": SYSTEM_PROMPTS['analysis']},
            {"role": "user", "content": prompt}
        ]

        # 获取分析结果
        response = get_response(messages)
        if not response:
            return jsonify({"error": "AI服务暂时不可用，请稍后重试"}), 503

        assistant_message = response.choices[0].message.content

        try:
            # 创建新的对话记录
            conversation = Conversation(
                user_message=f"[文件分析] {file.filename}",
                assistant_message=assistant_message,
                mode='analysis',
                timestamp=datetime.utcnow(),
                username=username
            )

            # 添加到会话并获取ID
            db.session.add(conversation)
            db.session.flush()  # 刷新会话以获取ID，但还不提交

            # 保存检测记录
            record = save_detection_record(
                conversation.id,
                username,
                text,  # 使用提取的文本内容
                'analysis',
                assistant_message
            )

            if not record:
                logger.error('保存检测记录失败')
                db.session.rollback()
                return jsonify({"error": "保存检测记录失败", "response": assistant_message}), 200

            # 提交事务
            db.session.commit()
            logger.info(f'成功保存文件分析记录，会话ID: {conversation.id}, 记录ID: {record.id}')

            return jsonify({
                "success": True,
                "response": assistant_message,
                "record": record.to_dict()
            }), 200

        except Exception as e:
            logger.error(f"保存记录失败: {str(e)}")
            db.session.rollback()
            return jsonify({"error": "保存记录失败", "response": assistant_message}), 200

    except Exception as e:
        logger.error(f"文件处理错误: {str(e)}")
        return jsonify({"error": str(e)}), 500


@aihelper_bp.route('/record/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """删除指定的检测记录"""
    try:
        # 查找记录
        record = Record.query.get(record_id)
        if not record:
            return jsonify({'error': '记录不存在'}), 404

        # 删除关联的对话记录（如果存在）
        if record.conversation_id:
            conversation = Conversation.query.get(record.conversation_id)
            if conversation:
                db.session.delete(conversation)

        # 删除记录
        db.session.delete(record)
        db.session.commit()

        logger.info(f'成功删除记录 ID: {record_id}')
        return jsonify({'message': '记录已成功删除'}), 200

    except Exception as e:
        logger.error(f'删除记录时发生错误: {str(e)}')
        db.session.rollback()
        return jsonify({'error': '删除记录失败，请稍后重试'}), 500


@aihelper_bp.route('/getreport', methods=['POST'])
def generate_report():
    """生成AI检测报告"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        username = data.get('username', '未登录用户')

        if not user_message:
            return jsonify({"error": "消息不能为空"}), 400

        # 构建系统提示词，包含更详细的分析指导
        system_prompt = """你是一位专业的虚假新闻检测专家，需要基于检测结果生成详细的分析报告。
                        在分析时，请特别注意：
                        1. 内容可信度：基于检测模型的判定和置信度，分析内容的整体可信程度
                        2. 关键特征：分析检测出的关键特征点，解释它们对真实性判断的影响
                        3. 语言特征：评估内容的表达方式、语气和逻辑性
                        4. 信息完整性：考察内容的完整性、连贯性和上下文合理性

                        请确保分析客观、专业，并提供具体的事实依据支持你的判断。"""

        # 构建用户提示词
        user_prompt = f"""请基于以下检测结果生成详细的分析报告：{user_message}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        # 获取AI回复
        try:
            response = get_response(messages)
            if not response or not response.choices:
                logger.error("AI服务返回空响应")
                return jsonify({"error": "AI服务返回空响应", "response": "无法生成分析报告，请稍后重试"}), 200

            assistant_message = response.choices[0].message.content
        except Exception as e:
            logger.error(f"获取AI回复失败: {str(e)}")
            return jsonify({"error": str(e), "response": "AI服务暂时不可用，请稍后重试"}), 200

        # 开始数据库事务
        try:
            # 创建新的对话记录
            conversation = Conversation(
                user_message=user_message,
                assistant_message=assistant_message,
                mode='analysis',
                timestamp=datetime.utcnow(),
                username=username
            )
            # 添加到会话并获取ID
            db.session.add(conversation)
            db.session.flush()

            # 提交事务
            db.session.commit()
            logger.info(f"成功保存AI分析报告: {conversation.id}")
            return jsonify({"response": assistant_message}), 200

        except Exception as e:
            logger.error(f"数据库操作失败: {str(e)}")
            db.session.rollback()
            # 即使数据库操作失败，也返回AI生成的报告
            return jsonify({"error": "保存记录失败", "response": assistant_message}), 200

    except Exception as e:
        logger.error(f"生成报告错误: {str(e)}")
        return jsonify({"error": str(e), "response": "服务器内部错误，请稍后重试"}), 500