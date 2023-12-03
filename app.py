# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from dotenv import dotenv_values
from flask import send_file
from docx import Document
import openai

app = Flask(__name__, template_folder='frontend')
app.static_folder = 'frontend'

# Load configuration from .env
dotenv_config = dotenv_values(".env")

# Set your OpenAI API key
api_key = dotenv_config.get('API_KEY')
openai.api_key = api_key

# MySQL configuration
app.config['MYSQL_HOST'] = dotenv_config['MYSQL_HOST']
app.config['MYSQL_USER'] = dotenv_config['MYSQL_USER']
app.config['MYSQL_PASSWORD'] = dotenv_config['MYSQL_PASSWORD']
app.config['MYSQL_DB'] = dotenv_config['MYSQL_DB']

# Initialize MySQL
mysql = MySQL(app)

# 預先定義的固定 prompt
fixed_prompt = """
首先完整查看使用者輸入的病例內容，再來根據這些信息產生一份完整的病例表格，格式內容請參考下面輸出範例，沒有或空白的資料請填入"N/A"，請確保欄位和資料內容須正確相符、完整且必須對齊，表格結構需要正確，最後檢查內容無誤再以病歷原文以及英文輸出
以下是輸出範例格式，注意不要跑版，並且要按照飯裡順序:  
|SNOMED:| SNOMED |
|病史:| CLINICAL HISTORY |
|診斷:| DIAGNOSIS |
|組織片數:| 片數 |
|組織尺寸:| 切片尺寸大小 | 
|組織部位:| 組織或切片部位 |
|切片方式:| 切片組織獲得方法 |  
|處理方式:| 組織處理方式 | 
|組織顏色:| 組織切片顏色 |
|組織形狀:| 組織切片形狀 |
|顯微鏡檢查:| 顯微鏡檢查結果 |
|參考資料:| 參考資料內容 |
|住院醫師:| 醫師姓名 |
|病理醫師:| 醫師姓名 |
|細胞醫檢師:| 細胞醫檢師姓名 |
|病理專醫字:| 病理專醫字 |
"""

# 登入路由
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if the user exists in the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()

        # If the user exists, set them as logged in
        if user:
            session['user'] = user
            return redirect(url_for('index'))

    return render_template("login.html")

# 登入路由
@app.route("/login", methods=["GET", "POST"])
def login_home():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if the user exists in the database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()

        # If the user exists, set them as logged in and redirect to index
        if user:
            session['user'] = user
            return redirect(url_for('index'))

        # If the user does not exist or the password is incorrect, show an error message
        error_message = "Invalid username or password. Please try again."
        return render_template("login.html", error_message=error_message)

    return render_template("login.html")

# Index route
@app.route("/index", methods=["GET", "POST"])
def index():
    if 'user' in session:
        user = session['user']

        if request.method == "POST":
            user_input = request.form["prompt"]
            combined_prompt = fixed_prompt + user_input

            # Generate result from OpenAI API
            res = openai.Completion.create(
                model="text-davinci-003",
                prompt=combined_prompt,
                max_tokens=1000
            )
            text = res["choices"][0]["text"]

            # Convert text to HTML
            lines = text.split("\n")
            lines = [line.strip() for line in lines]

            # Save text as a plain text file
            save_txt_path = "result.txt"
            with open(save_txt_path, "w", encoding="utf-8") as txt_file:
                for line in lines:
                    clean_line = line.replace("|", "")
                    if clean_line.strip():
                        txt_file.write(clean_line + "\n")

            return render_template("index.html", lines=lines)

        return render_template("index.html", user=user)

    else:
        return redirect(url_for('login'))


# Logout route
@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route("/download_txt", methods=["GET"])
def download_txt():
    # 檔案路徑
    file_path = "result.txt"
    
    # 回傳檔案至使用者
    return send_file(file_path, as_attachment=True, download_name="病例表格.txt")

# 新增路由用於處理下載 Word 文件請求
@app.route("/download_word", methods=["GET"])
def download_word():
    # 檔案路徑
    txt_file_path = "result.txt"
    word_file_path = "result.docx"

    # 讀取 txt 檔案內容
    with open(txt_file_path, "r", encoding="utf-8") as txt_file:
        txt_content = txt_file.read()

    # 創建 Word 文件
    doc = Document()
    doc.add_paragraph(txt_content)

    # 儲存 Word 文件
    doc.save(word_file_path)

    # 回傳 Word 檔案至使用者
    return send_file(word_file_path, as_attachment=True, download_name="病例表格.docx")

if __name__ == "__main__":
    app.secret_key = '000000'  # Set your secret key for session encryption
    app.run()