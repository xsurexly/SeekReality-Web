from datetime import datetime

from flask import Blueprint, request, jsonify
from models import db, ReadHistory,Newslist,Newsread
from sqlalchemy import func, and_

read_history_bp = Blueprint('read_history', __name__)

#记录阅读数据，但newsread中的阅读完成未更新
@read_history_bp.route('/read_history/<string:news_id>', methods=['POST'])
def add_read_history(news_id):
    data = request.get_json()
    read_time = data.get('read_time', 0)
    username = data.get('username')

    # 创建新的阅读历史记录
    new_read_history = ReadHistory(
        username=username,
        news_id=news_id,
        read_time=read_time,
    )
    db.session.add(new_read_history)

    # 检查是否已经存在于 Newsread 表中
    news_read_record = Newsread.query.filter_by(username=username, news_id=news_id).first()
    if not news_read_record:
        # 如果没有记录，则创建新的记录
        news_read_record = Newsread(username=username, news_id=news_id, is_favorite=False, is_finished=False)
        db.session.add(news_read_record)
    else:
        # 如果已经存在，更新阅读状态
        news_read_record.is_finished = True  # 假设用户完成了阅读
    db.session.commit()
    return jsonify({"msg": "新的阅读历史记录已创建"}), 201

# #获取阅读历史记录
# @read_history_bp.route('/user/<string:username>', methods=['GET'])
# def get_user_read_history(username):
#     records = (
#         db.session.query(ReadHistory, Newslist, Newsread)
#         .join(Newslist, ReadHistory.news_id == Newslist.id)  # 连接 Newslist 表
#         .join(Newsread, (ReadHistory.news_id == Newsread.news_id) & (Newsread.username == username))  # 连接 Newsread 表
#         .filter(ReadHistory.username == username)
#         .filter(ReadHistory.read_time >0)
#         .all()
#     )
#
#     # 将结果转换为字典格式
#     result = []
#     for read_history, news, news_read in records:
#         result.append({
#             "id": read_history.id,
#             "date": read_history.created_at,
#             "news_id": news.id,
#             "title": news.title,
#             "content": news.content,
#             "category": news.category,
#             "source": news.source,
#             "readtime": read_history.read_time,
#             "is_finished": news_read.is_finished,  # 从 Newsread 表获取是否读完
#             "is_favorite": news_read.is_favorite,  # 从 Newsread 表获取收藏状态
#         })
#
#     return jsonify(result), 200
#获取阅读历史记录，只会返回每一天的最后的阅读记录
@read_history_bp.route('/user/<string:username>', methods=['GET'])
def get_user_read_history(username):
    # 获取每个新闻每天的最后阅读时间
    date_subquery = (
        db.session.query(
            ReadHistory.news_id,
            func.date(ReadHistory.created_at).label('read_date'),
            func.max(ReadHistory.created_at).label('last_read_time')
        )
        .filter(
            ReadHistory.username == username,
            ReadHistory.read_time > 0
        )
        .group_by(
            ReadHistory.news_id,
            func.date(ReadHistory.created_at)
        )
        .subquery()
    )

    # 获取最终需要的历史记录
    records = (
        db.session.query(ReadHistory, Newslist, Newsread)
        .join(
            date_subquery,
            and_(
                ReadHistory.news_id == date_subquery.c.news_id,
                ReadHistory.created_at == date_subquery.c.last_read_time
            )
        )
        .join(Newslist, ReadHistory.news_id == Newslist.id)
        .join(
            Newsread,
            and_(
                ReadHistory.news_id == Newsread.news_id,
                Newsread.username == username
            )
        )
        .order_by(ReadHistory.created_at.desc())
        .all()
    )

    # 构建返回结果
    result = []
    for read_history, news, news_read in records:
        result.append({
            "id": read_history.id,
            "date": read_history.created_at.isoformat(),
            "news_id": news.id,
            "title": news.title,
            "content": news.content,
            "category": news.category,
            "source": news.source,
            "readtime": read_history.read_time,
            "is_finished": news_read.is_finished,
            "is_favorite": news_read.is_favorite,
        })

    return jsonify(result), 200
# 删除阅读记录(会全部删除)，并取消newsread表的收藏和已阅读
@read_history_bp.route('/deleterecord/<int:id>', methods=['DELETE'])
def delete_read_history(id):
    # 假设用户ID为2，实际应从请求中获取
    data=request.get_json()
    username = data.get('username')
    # 查找要删除的 ReadHistory 记录
    record = ReadHistory.query.get(id)  # 根据 ID 查找记录

    if record:
        # 获取对应的新闻记录
        news_id = record.news_id  # 获取要删除的记录的 news_id
        print(f"Deleting records for news_id: {news_id}")

        # 删除 ReadHistory 表中与该 news_id 相关的所有记录
        ReadHistory.query.filter_by(news_id=news_id, username=username).delete()

        # 查找 Newsread 表中的记录
        Newsread.query.filter_by(news_id=news_id, username=username).delete()

        # 提交更改
        db.session.commit()  # 提交对新闻记录的更改

        return jsonify({'message': '所有相关记录已删除'}), 200

    print("Record not found.")
    return jsonify({'message': '记录未找到'}), 404

#更新收藏
@read_history_bp.route('/favorite/<string:news_id>', methods=['PUT'])
def update_toggle_history(news_id):
    data = request.get_json()
    username=data.get('username')
    print(f"Updating favorite for username: {username}, news_id: {news_id}, is_favorite: {data.get('is_favorite')}")
    record = Newsread.query.filter_by(news_id=news_id, username=username).first()  # 确保根据用户ID查找记录

    if record:
        # 更新新闻记录的收藏状态
        record.is_favorite = data.get('is_favorite', record.is_favorite)
        db.session.commit()
        return jsonify({"msg": "记录已更新"}), 200

    return jsonify({"msg": "记录未找到"}), 404

@read_history_bp.route('/reading_stats/<string:username>', methods=['GET'])
def get_reading_stats(username):
    print('total_reads')
    # Count total unique reads based on news_id
    total_reads = db.session.query(func.count(func.distinct(ReadHistory.news_id))).filter_by(username=username).scalar()
    print(total_reads)
    today = datetime.utcnow().date()
    # Count unique reads for today
    today_reads = db.session.query(func.count(func.distinct(ReadHistory.news_id))).filter(
        ReadHistory.username == username,
        func.date(ReadHistory.created_at) == today
    ).scalar()

    # Count unique reads grouped by date
    daily_reads = db.session.query(
        func.date(ReadHistory.created_at).label('date'),
        func.count(func.distinct(ReadHistory.news_id)).label('count')
    ).filter(ReadHistory.username == username).group_by(func.date(ReadHistory.created_at)).all()

    # Convert daily reads to a dictionary
    daily_reads_dict = {str(date): count for date, count in daily_reads}

    return jsonify({
        'total_reads': total_reads,
        'today_reads': today_reads,
        'daily_reads': daily_reads_dict  # 返回每日阅读数量
    }), 200