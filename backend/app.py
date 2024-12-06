from flask import Flask
from flask_cors import CORS
import mysql.connector
from flask import request, jsonify
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})
# 配置数据库连接
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'fake_news_db'

# 创建数据库连接对象
mysql_connection = mysql.connector.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    password=app.config['MYSQL_PASSWORD'],
    database=app.config['MYSQL_DB']
)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    cursor = mysql_connection.cursor()
    try:
        # 先查询用户名是否已存在
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({'success': False, 'message': '用户名已存在，请更换用户名再注册！'})

        # 插入新用户数据到数据库
        insert_query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (username, password, email))
        mysql_connection.commit()
        return jsonify({'success': True, 'message': '注册成功！'})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': '注册过程出现问题，请稍后再试！'})
    finally:
        cursor.close()


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    cursor = mysql_connection.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        if user:
            return jsonify({'success': True, 'user': {'id': user[0], 'username': user[1]}})
        return jsonify({'success': False, 'message': '用户名或密码错误，请重新输入！'})
    except Exception as e:
        print(e)
        return jsonify({'success': False, 'message': '登录过程出现问题，请稍后再试！'})
    finally:
        cursor.close()

if __name__ == '__main__':
    app.run()