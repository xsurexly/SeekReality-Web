#此处用于单条新闻的llm对话，即无上下文记忆功能
"""
使用promt，规定了输出格式为
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
[简要总结分析结论])
"""
#若要修改，请注意修改css样式和js中的输出格式

#待完善有日志记录，链接数据库等内容
#模型待微调
#似乎使用的是fetch方法，感觉可以修改
import logging
from flask import Blueprint, request, jsonify
from openai import OpenAI
import docx
from PyPDF2 import PdfReader
import io
#sk-9f8d92679a634dbc849338c0b36842b1
# 创建蓝图
aihelper_bp = Blueprint('aihelper', __name__)

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key="sk-9f8d92679a634dbc849338c0b36842b1",
    base_url="https://api.deepseek.com/v1",
)

# 系统提示词
system_prompt = """你是一位专业的虚假新闻检测专家，拥有丰富的新闻事实核查经验。在分析新闻时，你会从以下几个方面进行深入分析：

1. 信息来源可靠性：
   - 评估新闻来源的可信度
   - 检查作者身份和专业背景
   - 验证引用的数据和专家观点

2. 内容真实性：
   - 核实关键事实和数据
   - 检查时间线的合理性
   - 对比其他可靠媒体的报道

3. 情感倾向：
   - 分析语言是否客观中立
   - 检测煽动性或误导性表达
   - 评估标题与内容的一致性

4. 上下文完整性：
   - 考虑新闻的完整背景
   - 检查是否有重要信息被省略
   - 评估叙述的平衡性"""

# 分析格式提示词
analysis_format = """请按照以下格式提供分析：

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

messages = [{"role": "system", "content": system_prompt}]


def get_response(client, messages, stream=False):
    """获取助手回复"""
    print(messages)
    try:
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=messages,
            stream=stream,
        )
        print(response)
        return response
    except Exception as e:
        print(f"API 请求失败: {str(e)}")
        return None


@aihelper_bp.route('/talk', methods=['POST'])
def analyze_single():
    """单条新闻分析接口"""
    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({"error": "未提供新闻内容"}), 400

        # 构建完整的提示词
        prompt = f"""请分析以下新闻内容的真实性：

{user_message}

{analysis_format}"""

        # 构建消息
        current_messages = messages.copy()
        current_messages.append({"role": "user", "content": prompt})
        # 获取分析结果
        response = get_response(client, current_messages)

        if response:
            assistant_message = response.choices[0].message.content
            return jsonify({"response": assistant_message}), 200
        else:
            return jsonify({"error": "分析失败，请稍后重试"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_text_from_docx(file_stream):
    """从 Word 文档提取文本"""
    try:
        doc = docx.Document(file_stream)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        logging.error(f"Word文档处理错误: {str(e)}")
        raise Exception("无法读取Word文档，请确保文件格式正确")

def extract_text_from_pdf(file_stream):
    """从 PDF 文档提取文本"""
    try:
        reader = PdfReader(file_stream)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
        return text
    except Exception as e:
        logging.error(f"PDF处理错误: {str(e)}")
        raise Exception("无法读取PDF文档，请确保文件格式正确")


@aihelper_bp.route('/upload', methods=['POST'])
def analyze_file():
    """处理文件上传和分析"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "没有上传文件"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "未选择文件"}), 400

        # 读取文件内容
        file_content = file.read()
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

        # 直接使用现有的分析逻辑
        prompt = f"""请分析以下新闻内容的真实性：

{text}

{analysis_format}"""

        # 构建消息
        current_messages = messages.copy()
        current_messages.append({"role": "user", "content": prompt})

        # 获取分析结果
        response = get_response(client, current_messages)

        if response:
            assistant_message = response.choices[0].message.content
            return jsonify({"response": assistant_message}), 200
        else:
            return jsonify({"error": "分析失败，请稍后重试"}), 500

    except Exception as e:
        logging.error(f"文件处理错误: {str(e)}")
        return jsonify({"error": str(e)}), 500




# 可以添加更多与单条新闻分析相关的路由
@aihelper_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """提交分析反馈"""
    pass


@aihelper_bp.route('/save', methods=['POST'])
def save_analysis():
    """保存分析结果"""
    pass