from flask import Blueprint, request, jsonify
from models import db, DetectionHistory

history_bp = Blueprint('history', __name__)

# 保存检测记录
def save_detection_history(user_id, detection_type, detection_content=None, file_path=None, result=""):
    history = DetectionHistory(
        user_id=user_id,
        detection_type=detection_type,
        detection_content=detection_content,
        file_path=file_path,
        result=result
    )
    db.session.add(history)
    db.session.commit()

# 查询检测历史
@history_bp.route('/history', methods=['GET'])
def get_detection_history():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '缺少 user_id'}), 400

    # 查询用户的历史记录
    histories = DetectionHistory.query.filter_by(user_id=user_id).order_by(DetectionHistory.detected_at.desc()).all()

    # 构造返回的 JSON 数据
    result = [
        {
            'id': h.id,
            'detection_type': h.detection_type,
            'detection_content': h.detection_content,
            'file_path': h.file_path,
            'result': h.result,
            'detected_at': h.detected_at.strftime('%Y-%m-%d %H:%M:%S')
        } for h in histories
    ]

    return jsonify({'success': True, 'history': result})
