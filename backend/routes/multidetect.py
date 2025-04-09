import os
import torch
import base64
import numpy as np
import io
import tempfile
from io import BytesIO
from PIL import Image
from flask import Blueprint, request, jsonify, render_template, current_app
from transformers import logging
from backend.model.multinodel.myweibo_dataset import token, feature_extractor, processor, blipmodel
from backend.model.multinodel.MMFN import MultiModal
from datetime import datetime
import logging

# 文件处理相关库
import pytesseract
import pdf2image
import docx2txt
from pdf2image import convert_from_bytes
import fitz

import subprocess
# 导入数据库模型
from models import db, DetectionHistory, ModelDetectionReport
# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Blueprint
multidetect_bp = Blueprint('multidetect', __name__)

# 检测设备
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"使用设备: {device}")

# 获取当前文件所在目录的绝对路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(os.path.dirname(CURRENT_DIR), "model", "multinodel", "best_model.pth")

# 使用延迟加载模式
model = None

def get_model():
    global model
    if model is None:
        print(f"加载模型...")
        model = MultiModal()
        model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
        model.to(device)
        model.eval()
        print(f"模型成功加载：{MODEL_PATH}")
    return model

def to_var(x):
    """将张量移动到可用设备上"""
    if device == 'cuda' and torch.cuda.is_available():
        x = x.cuda()
    return x

def get_tesseract_path():
    """获取 Tesseract 可执行文件的路径"""
    try:
        # 在 Windows 上使用 where 命令查找 tesseract
        result = subprocess.run(['where', 'tesseract'],
                              capture_output=True,
                              text=True,
                              check=True)
        path = result.stdout.strip().split('\n')[0]
        print(f"找到 Tesseract 路径: {path}")
        return path
    except subprocess.CalledProcessError:
        print("无法通过 where 命令找到 tesseract")
        # 返回默认路径
        return r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    except Exception as e:
        print(f"查找 Tesseract 路径时出错: {e}")
        return r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image):
    """从图片中提取文本"""
    try:
        # 获取并设置 Tesseract 路径
        tesseract_path = get_tesseract_path()
        print(f"使用 Tesseract 路径: {tesseract_path}")
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

        # 验证 Tesseract 是否可用
        try:
            version = pytesseract.get_tesseract_version()
            print(f"Tesseract 版本: {version}")
        except Exception as e:
            print(f"验证 Tesseract 版本时出错: {e}")
            return "无法从图片提取文本，但会继续进行图像分析。"

        # 检查语言包
        try:
            # 使用 subprocess 直接调用 tesseract 检查可用语言
            result = subprocess.run([tesseract_path, '--list-langs'],
                                    capture_output=True,
                                    text=True)
            print(f"可用语言包: {result.stdout}")
            if 'chi_sim' not in result.stdout:
                print("警告: 未找到中文语言包")
        except Exception as e:
            print(f"检查语言包时出错: {e}")

        # 确保图片是RGB模式
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        elif image.mode not in ['RGB', 'L']:
            image = image.convert('RGB')

        # 尝试提取文本
        try:
            # 首先尝试中文+英文
            text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            if not text.strip():
                # 如果失败，仅尝试英文
                print("中文识别失败，尝试仅使用英文")
                text = pytesseract.image_to_string(image, lang='eng')

            if not text.strip():
                print("文本提取结果为空")
                return "无法从图片提取有效文本，但会继续进行图像分析。"

            print("成功提取文本")
            return text
        except Exception as e:
            print(f"文本提取过程出错: {e}")
            return "无法从图片提取文本，但会继续进行图像分析。"

    except Exception as e:
        print(f"OCR 处理过程出错: {e}")
        return "无法从图片提取文本，但会继续进行图像分析。"

def process_document(file_bytes, file_type):
    """处理文档，提取文本和图片"""
    extracted_text = ""
    main_image = None

    try:
        if file_type.startswith('image/'):
            # 处理图片文件
            img = Image.open(BytesIO(file_bytes))
            main_image = img.copy()
            # 尝试提取文本，如果失败则继续处理
            ocr_text = extract_text_from_image(img)
            extracted_text = ocr_text if ocr_text else "无法从图片提取文本，但会继续进行图像分析。"

        elif file_type == 'application/pdf':
            try:
                # 使用PyMuPDF处理PDF
                pdf_document = fitz.open(stream=file_bytes, filetype="pdf")

                # 获取第一页作为主图片
                if pdf_document.page_count > 0:
                    first_page = pdf_document[0]
                    # 获取页面的图像
                    pix = first_page.get_pixmap()
                    img_data = pix.tobytes("png")
                    main_image = Image.open(BytesIO(img_data))

                    # 从所有页面提取文本
                    for page_num in range(pdf_document.page_count):
                        page = pdf_document[page_num]
                        page_text = page.get_text()
                        if page_text.strip():
                            extracted_text += page_text + "\n\n"

                pdf_document.close()

                if not extracted_text.strip():
                    # 如果无法直接提取文本，尝试OCR
                    print("PDF没有可提取的文本，尝试OCR...")
                    if main_image:
                        ocr_text = extract_text_from_image(main_image)
                        extracted_text = ocr_text if ocr_text else "无法从PDF提取文本，但会继续进行图像分析。"

            except Exception as e:
                print(f"PDF处理失败: {e}")
                return "PDF文件处理失败，请确保文件未加密且格式正确。", None

        elif file_type in ['application/msword',
                           'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            # 处理Word文档
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp:
                temp.write(file_bytes)
                temp_path = temp.name

            try:
                # 提取文本
                extracted_text = docx2txt.process(temp_path)

                # 从Word文档中提取图片
                try:
                    extracted_images = docx2txt.process(temp_path, temp_path + "_images")
                    image_dir = temp_path + "_images"

                    if os.path.exists(image_dir) and os.path.isdir(image_dir):
                        image_files = [f for f in os.listdir(image_dir) if
                                       f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                        if image_files:
                            first_image_path = os.path.join(image_dir, image_files[0])
                            main_image = Image.open(first_image_path)
                except Exception as e:
                    print(f"提取Word文档图片失败: {e}")
            finally:
                # 清理临时文件
                if os.path.exists(temp_path):
                    try:
                        os.unlink(temp_path)
                    except Exception as e:
                        print(f"清理临时文件失败: {e}")
                if os.path.exists(image_dir) and os.path.isdir(image_dir):
                    try:
                        for file in os.listdir(image_dir):
                            os.unlink(os.path.join(image_dir, file))
                        os.rmdir(image_dir)
                    except Exception as e:
                        print(f"清理图片目录失败: {e}")

    except Exception as e:
        print(f"处理文档出错: {e}")
        return f"文档处理失败: {str(e)}", None

    if not extracted_text:
        return "无法从文档中提取文本。", main_image

    return extracted_text, main_image

def preprocess_text_image(text, image=None, image_base64=None):
    """预处理文本和图片"""
    try:
        # 获取当前设备
        device = current_app.config.get('DEVICE', 'cpu')

        # 处理图片 - 从路径或base64
        if image_base64:
            # 解码base64字符串为图片
            try:
                image_data = base64.b64decode(image_base64)
                img = Image.open(BytesIO(image_data)).convert('RGB')
                img = img.resize((224, 224))
            except Exception as e:
                print(f"解码base64图片出错：{e}")
                img = Image.new('RGB', (224, 224), (255, 255, 255)).convert('RGB')
        elif image:
            if isinstance(image, Image.Image):
                img = image.convert('RGB')
                img = img.resize((224, 224))
            elif os.path.exists(image):
                img = Image.open(image).convert('RGB')
                img = img.resize((224, 224))
            else:
                print(f"图片文件未找到：{image}")
                img = Image.new('RGB', (224, 224), (255, 255, 255)).convert('RGB')
        else:
            # 如果没有提供图片，创建空白图片
            img = Image.new('RGB', (224, 224), (255, 255, 255)).convert('RGB')

        # 为BLIP准备输入
        inputs = processor(img, text, return_tensors="pt")

        # 使用Swin transformer处理图像
        image_swin = feature_extractor(img, return_tensors="pt").pixel_values

        # 使用BERT tokenizer处理文本
        text_data = token.encode_plus(
            text,
            truncation=True,
            padding='max_length',
            max_length=300,
            return_tensors='pt',
            return_attention_mask=True,
            return_token_type_ids=True
        )

        input_ids = text_data['input_ids']
        attention_mask = text_data['attention_mask']
        token_type_ids = text_data['token_type_ids']

        # 使用BLIP模型提取特征
        with torch.no_grad():
            try:
                blipmodel.to(device)
                inputs_on_device = {k: v.to(device) for k, v in inputs.items()}

                outputs = blipmodel(**inputs_on_device)

                if hasattr(outputs, 'vision_model_output'):
                    image_features = outputs.vision_model_output.last_hidden_state.mean(dim=1)
                    text_features = outputs.text_model_output.last_hidden_state.mean(dim=1)
                else:
                    # 从question_embeds获取文本特征
                    text_features = outputs.question_embeds
                    if text_features.dim() > 2:
                        text_features = text_features.mean(dim=1)

                    # 从last_hidden_state获取图像特征
                    image_features = outputs.last_hidden_state
                    if image_features.dim() > 2:
                        image_features = image_features.mean(dim=1)

                # 将特征移动到CPU以避免内存问题
                text_features = text_features.detach().cpu()
                image_features = image_features.detach().cpu()

                # 清理
                del inputs_on_device, outputs

            except Exception as e:
                print(f"处理BLIP特征出错：{e}")
                # 备用特征
                text_features = torch.zeros(1, 768)
                image_features = torch.zeros(1, 768)

            finally:
                # 清理GPU内存
                blipmodel.cpu()
                torch.cuda.empty_cache()

        return input_ids, attention_mask, token_type_ids, image_swin, image_features, text_features

    except Exception as e:
        print(f"预处理过程出错：{e}")
        return None

def predict(model, input_ids, attention_mask, token_type_ids, image, text_features, image_features):
    """使用模型进行预测"""
    try:
        with torch.no_grad():
            # 将所有输入移动到适当的设备
            input_ids = to_var(input_ids)
            attention_mask = to_var(attention_mask)
            token_type_ids = to_var(token_type_ids)
            image = to_var(image)
            text_features = to_var(text_features)
            image_features = to_var(image_features)

            # 前向传播
            outputs = model(input_ids, attention_mask, token_type_ids, image, text_features, image_features)

            # 获取预测类别的概率分布
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            
            # 获取两个类别的概率值
            fake_prob = float(probabilities[0][0].item())  # 虚假新闻的概率
            real_prob = float(probabilities[0][1].item())  # 真实新闻的概率
            
            # 确定预测类别
            predicted_class = 1 if real_prob > fake_prob else 0
            
            # 使用真实概率作为真实度
            truth_level = "高" if real_prob > 0.8 else "中等" if real_prob > 0.6 else "低"
            
            # 生成分析说明
            analysis = {
                "真实概率": f"{real_prob:.2%}",
                "虚假概率": f"{fake_prob:.2%}",
                "真实度级别": truth_level,
                "分析说明": f"该新闻的真实度{truth_level}，模型判定其为{'真实' if predicted_class == 1 else '虚假'}新闻。"
            }
            
            if real_prob < 0.6:
                analysis["建议"] = "由于新闻真实度较低，建议进一步核实信息来源和内容真实性。"

            # 将预测结果转换为有意义的标签
            result = {
                "prediction": "真实新闻" if predicted_class == 1 else "虚假新闻",
                "class": predicted_class,
                "truth_probability": real_prob,  # 真实度（使用真实新闻的概率）
                "analysis": analysis,
                "isFake": predicted_class == 0,  # 添加isFake字段，与detect.py中的格式保持一致
                "fraudProbability": real_prob * 100  # 添加fraudProbability字段，与detect.py中的格式保持一致
            }

            return result

    except Exception as e:
        print(f"预测过程出错：{e}")
        return {"error": str(e)}

def save_detection_history(userid, detection_type, content, file_path, detection_result, detection_tool):
    """保存检测历史记录到 DetectionHistory 表"""
    try:
        # 解析检测结果
        is_fake = detection_result.get('isFake', False)
        fraud_probability = detection_result.get('fraudProbability', 0.0)
        
        # 将 isFake 转换为 0（true）或 1（false）
        result_value = 1 if fraud_probability >= 60 else 0
        
        # 创建检测历史记录
        history = DetectionHistory(
            userid=userid,  # 用户 ID
            detection_type=detection_type,  # 检测类型（"text" 或 "file"）
            content=content,  # 检测内容（文本内容）
            file_path=file_path,  # 文件路径（如果是文件检测）
            result=result_value,  # 检测结果（0 表示 true，1 表示 false）
            detection_tool=detection_tool,  # 使用的模型
            score=fraud_probability,  # 置信度
            created_at=datetime.utcnow()  # 检测时间
        )

        # 保存记录到数据库
        db.session.add(history)
        db.session.flush()  # 获取history.id

        return history

    except Exception as e:
        logger.error(f'保存检测历史记录时发生错误: {str(e)}')
        db.session.rollback()
        return None

# 合并后的统一检测API
@multidetect_bp.route("/detect", methods=["POST"])
def unified_detect_api():
    """统一的虚假新闻检测API端点 - 支持文本、图片和文件输入"""
    # 记录请求开始
    print(f"收到统一检测请求")
    
    # 检查请求中是否包含文件
    if 'file' in request.files:
        # 文件检测模式
        print(f"检测模式: 文件上传")
        uploaded_file = request.files['file']
        
        # 检查文件名是否为空
        if uploaded_file.filename == '':
            return jsonify({"status": "error", "message": "未选择文件"}), 400
        
        # 获取文件类型和内容
        file_content = uploaded_file.read()
        file_type = uploaded_file.content_type
        
        # 处理文档，提取文本和图片
        extracted_text, main_image = process_document(file_content, file_type)
        
        # 如果没有提取到文本或图片
        if not extracted_text:
            return jsonify({"status": "error", "message": "无法从文件中提取文本"}), 400
        
        # 预处理提取的内容
        processed_inputs = preprocess_text_image(extracted_text, main_image)
        if processed_inputs is None:
            return jsonify({"status": "error", "message": "预处理输入出错"}), 500
        
        input_ids, attention_mask, token_type_ids, image_swin, image_features, text_features = processed_inputs
        
        # 进行预测
        result = predict(get_model(), input_ids, attention_mask, token_type_ids, image_swin, image_features, text_features)
        
        # 如果预测过程有错误
        if "error" in result:
            return jsonify({"status": "error", "message": result["error"]}), 500
        
        # 创建响应数据
        response_data = {
            "status": "success",
            "result": result,
            "extracted_text": extracted_text
        }
        
        # 如果提取到了图片，将其转为base64以在前端显示
        if main_image:
            img_byte_arr = BytesIO()
            main_image.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            response_data["extracted_image"] = base64.b64encode(img_byte_arr).decode('utf-8')
        
        # 保存检测历史记录
        user_id = request.form.get('user_id')
        if user_id:
            save_detection_history(
                userid=user_id,
                detection_type="file",
                content=extracted_text,
                file_path=uploaded_file.filename,
                detection_result=result,
                detection_tool="MMFN"
            )
        
        # 记录预测结果
        print(f"文件预测结果: {result}")
        
        # 返回结果
        return jsonify(response_data), 200
    
    else:
        # 文本/图片检测模式
        print(f"检测模式: 文本/图片")
        
        # 检查请求内容类型
        print(f"请求Content-Type: {request.content_type}")
        
        # 获取请求数据
        try:
            request_data = request.get_json()
            print(f"请求数据: {request_data}")
        except Exception as e:
            print(f"解析JSON出错: {e}")
            return jsonify({"status": "error", "message": f"无效的JSON: {str(e)}"}), 400
        
        # 检查必填字段
        if not request_data:
            return jsonify({"status": "error", "message": "未提供数据"}), 400
        
        if "text" not in request_data:
            return jsonify({"status": "error", "message": "text字段为必填项"}), 400
        
        text = request_data.get("text", "")
        image_path = request_data.get("image_path", None)
        image_base64 = request_data.get("image_base64", None)
        user_id = request_data.get("user_id", None)
        
        # 预处理输入
        processed_inputs = preprocess_text_image(text, image_path, image_base64)
        if processed_inputs is None:
            return jsonify({"status": "error", "message": "预处理输入出错"}), 500
        
        input_ids, attention_mask, token_type_ids, image_swin, image_features, text_features = processed_inputs
        
        # 进行预测
        result = predict(get_model(), input_ids, attention_mask, token_type_ids, image_swin, image_features, text_features)
        
        # 如果预测过程有错误
        if "error" in result:
            return jsonify({"status": "error", "message": result["error"]}), 500
        
        # 保存检测历史记录
        if user_id:
            save_detection_history(
                userid=user_id,
                detection_type="text",
                content=text,
                file_path=None,
                detection_result=result,
                detection_tool="MMFN"
            )
        
        # 记录预测结果
        print(f"预测结果: {result}")
        
        # 返回结果
        return jsonify({
            "status": "success",
            "result": result
        }), 200

# 保留原有路由以保持向后兼容性
@multidetect_bp.route("/predict", methods=["POST"])
def predict_api():
    """虚假新闻检测的API端点 - 文本和图像输入（向后兼容）"""
    return unified_detect_api()

@multidetect_bp.route("/file_predict", methods=["POST"])
def file_predict_api():
    """虚假新闻检测的API端点 - 文件上传（向后兼容）"""
    return unified_detect_api()

