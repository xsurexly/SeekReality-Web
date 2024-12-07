import mysql.connector
from flask import jsonify

# 数据库连接配置
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = '123456'
MYSQL_DB = 'fake_news_db'


# 创建数据库连接对象
def get_db_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )


# 注册功能
def register_user(username, password, email):
    mysql_connection = get_db_connection()
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
        mysql_connection.close()


# 登录功能
def login_user(username, password):
    mysql_connection = get_db_connection()
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
        mysql_connection.close()
