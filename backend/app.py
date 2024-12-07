from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from auth import register_user, login_user  # 引入auth.py中的函数

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    # 调用auth.py中的register_user函数
    return register_user(username, password, email)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 调用auth.py中的login_user函数
    return login_user(username, password)

if __name__ == '__main__':
    app.run()
