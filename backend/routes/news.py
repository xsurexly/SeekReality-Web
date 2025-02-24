from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# 模拟的新闻数据
news_data = [
    {
        'id': 1,
        'title': '从“中国游”到“世界游”：往来便利让中外游客“双向奔赴”',
        'summary': '2024年，外国游客将通过“China Travel”和中国旅游热度的“World Travel”再度热情涌入中国。',
        'content': '2024年，外国游客将通过“China Travel”和中国旅游热度的“World Travel”再度热情涌入中国。...',
        'fraudProbability': 25,
        'isFake': False,
        'isFavorite': False
    },
    {
        'id': 2,
        'title': '流浪过夜后美国华裔餐馆迎新年 各地消费经济再次上升',
        'summary': '美国华裔餐馆在迎接2025年的同时，迎来消费热潮。',
        'content': '美国华裔餐馆在迎接2025年的同时，迎来消费热潮，提供了更多的餐饮和文化体验...',
        'fraudProbability': 10,
        'isFake': False,
        'isFavorite': False
    }
]

# 获取新闻列表
@app.route('/api/news', methods=['GET'])
def get_news():
    return jsonify({'news': news_data})

# 获取新闻详细信息
@app.route('/api/news/<int:news_id>', methods=['GET'])
def get_news_detail(news_id):
    for news in news_data:
        if news['id'] == news_id:
            return jsonify(news)
    return jsonify({'success': False, 'message': 'News not found'}), 404

# 切换收藏状态
@app.route('/api/news/<int:news_id>/favorite', methods=['POST'])
def toggle_favorite(news_id):
    for news in news_data:
        if news['id'] == news_id:
            news['isFavorite'] = not news['isFavorite']
            return jsonify({'success': True, 'isFavorite': news['isFavorite']})
    return jsonify({'success': False, 'message': 'News not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
