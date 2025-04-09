from flask import Flask, jsonify, request, Blueprint
from flask_cors import CORS
from models import db, Newslist

android_bp = Blueprint('android', __name__)
@android_bp.route('/news_table', methods=['GET'])
def get_news():
    news_list = Newslist.query.all()
    return jsonify([news.to_dict() for news in news_list])