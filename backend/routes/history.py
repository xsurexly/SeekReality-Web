from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from models import db, DetectionHistory, Record, Conversation

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

detection_history_bp = Blueprint('detection_history', __name__)

def save_detection_record(conversation_id, username, content, detection_mode, assistant_message):
    """保存检测记录"""
    try:
        # 从AI回复中提取结构化数据
        analysis_data = parse_ai_response(assistant_message)
        if not analysis_data:
            logger.error('无法从AI回复中提取结构化数据')
            return None

        # 创建检测记录
        record = Record(
            conversation_id=conversation_id,
            username=username,
            content=content,
            detection_mode=detection_mode,
            score=analysis_data.get('score', 0),
            result=analysis_data.get('result', False),
            confidence=analysis_data.get('confidence', 0.0),
            detailed_analysis=analysis_data.get('detailed_analysis', ''),
            evidence=analysis_data.get('evidence', ''),
            summary=analysis_data.get('summary', '')
        )
        
        db.session.add(record)
        db.session.commit()
        logger.info(f'成功保存检测记录: {record.id}')
        return record
        
    except Exception as e:
        logger.error(f'保存检测记录时发生错误: {str(e)}')
        db.session.rollback()
        return None

def parse_ai_response(response):
    """解析AI响应，提取结构化数据"""
    try:
        import re
        # 提取真实性评分
        score_match = re.search(r'真实性评分：(\d+)', response)
        score = int(score_match.group(1)) if score_match else 0
        
        # 提取详细分析
        analysis_match = re.search(r'详细分析：(.*?)(?=相关事实依据：)', response, re.DOTALL)
        detailed_analysis = analysis_match.group(1).strip() if analysis_match else ''
        
        # 提取相关事实依据
        evidence_match = re.search(r'相关事实依据：(.*?)(?=总结：)', response, re.DOTALL)
        evidence = evidence_match.group(1).strip() if evidence_match else ''
        
        # 提取总结
        summary_match = re.search(r'总结：(.*?)$', response, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else ''
        
        return {
            'score': score,
            'result': score >= 60,  # 大于等于60分判定为真实
            'confidence': score / 100.0,
            'detailed_analysis': detailed_analysis,
            'evidence': evidence,
            'summary': summary
        }
    except Exception as e:
        logger.error(f"解析AI响应失败: {str(e)}")
        return None

@detection_history_bp.route('/detection-records', methods=['GET'])
def get_detection_records():
    """获取用户的AI检测记录"""
    try:
        username = request.args.get('username')
        mode = request.args.get('mode', 'analysis')

        if not username:
            return jsonify({'error': '用户名不能为空'}), 400

        # 查询记录
        records = Record.query.filter_by(
            username=username,
            detection_mode=mode
        ).order_by(Record.created_at.desc()).all()

        # 格式化返回数据
        history = [record.to_dict() for record in records]
        return jsonify({'history': history})

    except Exception as e:
        logger.error(f'获取检测记录失败: {str(e)}')
        return jsonify({'error': '获取检测记录失败'}), 500


@detection_history_bp.route('/detection-records/<int:record_id>', methods=['DELETE'])
def delete_detection_record(record_id):
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
        logger.error(f'删除记录失败: {str(e)}')
        db.session.rollback()
        return jsonify({'error': '删除记录失败'}), 500

# 保存检测历史
def save_detection_history(user_id, detection_type, detection_content=None, file_path=None, result="", detect_time=None):
    history = DetectionHistory(
        user_id=user_id,
        detection_type=detection_type,
        detection_content=detection_content,
        file_path=file_path,
        result=result,
        detected_at=detect_time
    )
    db.session.add(history)
    db.session.commit()

# 查询检测历史
@detection_history_bp.route('/old-history', methods=['GET'])
def get_old_history():
    """获取旧版本的检测历史"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': '缺少 user_id'}), 400

    histories = DetectionHistory.query.filter_by(user_id=user_id).order_by(DetectionHistory.detected_at.desc()).all()

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
