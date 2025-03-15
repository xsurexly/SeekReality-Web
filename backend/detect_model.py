from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# 加载模型和分词器
model_path = r"D:\12006software\Defeat-All-Fake-main\Defeat-All-Fake-main\backend\model\FakeNewsModel"
tokenizer_path=r"D:\12006software\Defeat-All-Fake-main\Defeat-All-Fake-main\backend\model\FakeNewsTokenizer"
model = AutoModelForSequenceClassification.from_pretrained(model_path)
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

# 将模型移动到 GPU（如果可用）
device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
model.to(device)


def predict(text):
    """使用模型进行预测"""
    # 使用分词器处理文本
    inputs = tokenizer(
        text,
        return_tensors="pt",  # 返回 PyTorch 张量
        truncation=True,  # 截断超过最大长度的文本
        padding=True,  # 填充到最大长度
        max_length=512  # 最大长度
    )

    # 将输入数据移动到 GPU（如果可用）
    inputs = {key: val.to(device) for key, val in inputs.items()}

    # 使用模型进行预测
    with torch.no_grad():
        outputs = model(**inputs)

    # 获取 logits 并计算概率
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=-1)  # 将 logits 转换为概率
    predicted_class = torch.argmax(probabilities, dim=-1).item()  # 获取预测类别

    # 返回预测类别和概率
    return predicted_class, probabilities.tolist()[0]

# if __name__ == "__main__":
#     # 测试文本
#     text = "这是一条测试新闻，用于检测模型是否正常工作。"
#
#     # 进行预测
#     predicted_class, probabilities = predict(text)
#
#     # 输出结果
#     print(f"预测类别: {predicted_class}")
#     print(f"类别概率: {probabilities}")