# -*- coding: utf-8 -*-
from flask import *
from dotenv import dotenv_values
from docx import Document
import openai
import pymongo

app = Flask(
    __name__,
    static_folder = 'static',
    template_folder = 'templates',
    static_url_path='/static'
    )


# 從 .env 載入配置
dotenv_config = dotenv_values(".env")

# 設定 OpenAI API 金鑰
openai.api_key = dotenv_config.get('API_KEY')

# 設定 MongoDB 連接
mongo_client = pymongo.MongoClient(dotenv_config.get('MONGODB_URI'))
db = mongo_client["medical_web"]
print("成功連接至 MongoDB")

############################################################################################################

# 預先定義的固定 prompt
fixed_prompt = """
首先完整查看使用者輸入的病例內容，再來根據這些信息產生一份完整的病例表格，格式內容請參考下面輸出範例，沒有或空白的資料請填入"N/A"，請確保欄位和資料內容須正確相符、完整且必須對齊，表格結構需要正確，最後檢查內容無誤再以原文或英文輸出
以下是輸出範例格式:
===

| 欄位 | 資料 |  

| 診斷資料號 | 資料號 |

| 病史 | 病人病史 |

| 診斷結果 | 診斷結果 |

| 組織片數 | 片數 |

| 組織尺寸 | 切片尺寸大小 | 

| 組織部位 | 組織部位或切片部位 |

| 切片方式 | 組織獲得方法 |  

| 處理方式 | 組織處理方式 | 

| 組織顏色 | 顏色 |

| 組織形狀 | 形狀 |

| 顯微鏡檢查 | 顯微鏡檢查結果 |

| 參考資料 | 參考資料內容 |

| 住院醫師 | 醫師姓名 |

| 病理醫師 | 醫師姓名 |

| 病理專醫字 | 醫師姓名 |
===
"""

############################################################################################################

# 登入首頁路由
@app.route("/")
def index():
    return render_template("index.html")

# 錯誤頁面路由
@app.route("/error")
def error():
    msg = request.args.get('msg')
    return render_template("error.html", error_msg=msg)

# 註冊頁面路由
@app.route("/signup")
def signup():
    return render_template("signup.html")

# 主頁面路由
@app.route("/home")
def home():
    # 檢查 session 中是否有會員資訊，防止未登入的用戶進入會員頁面
    if 'username' in session:
        return render_template("home.html", username=session['username'])
    else:
        return redirect('/')

############################################################################################################

# 處理註冊表單請求
@app.route('/register', methods=['POST'])
def register():
    # 從前端接受資料
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    # 檢查 user 是否已經被註冊
    collection = db.user
    is_exist = collection.find_one({'username': username})
    # 如果已經被註冊，導向錯誤頁面
    # 如果沒有被註冊，將資料寫入資料庫，再導向登入頁面
    if is_exist != None:
        msg="此 Email 已經註冊過"
        return render_template("error.html", error_msg=msg)
    else:
        collection.insert_one({
            'username': username,
            'email': email,
            'password': password
        })
        return redirect('/')

# 處理登入表單請求
@app.route('/login', methods=['POST'])
def login():
    # 從前端接受資料
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    # 檢查 email 和 password 是否正確
    collection = db.user
    is_correct = collection.find_one({
        "$and": [
            {'email': email},
            {'password': password}
        ]
    })
    # 如果不正確，導向錯誤頁面
    # 如果正確，在session中記錄會員資訊，再導向會員頁面
    if is_correct == None:
        return redirect('/error?msg=帳號或密碼輸入錯誤')
    else:
        session['username'] = is_correct['username']
        return redirect('/home')
    
# 處理登出請求
@app.route('/logout')
def logout():
    # 清除 session 中的會員資訊
    session.pop('username', None)
    return redirect('/')

# @app.route('/instructions')
# def show_instructions():
#     # 在這裡可以加入返回使用說明的邏輯
#     return render_template('instructions.html')

# # Index 路由
# @app.route("/index", methods=["GET", "POST"])
# def index():
#     if 'user' in session:  #判斷是否有使用者已經登入
#         user = session['user']
#             #處理 POST 請求。當接收到 POST 請求時，從表單中取得使用者輸入的文字
#         if request.method == "POST":  
#             user_input = request.form["prompt"]
#             combined_prompt = fixed_prompt + user_input

#             # 使用 OpenAI API 生成結果
#             res = openai.Completion.create(
#                 model="text-davinci-003",
#                 prompt=combined_prompt,
#                 max_tokens=1000,
#                 temperature=0
#             )
#             text = res["choices"][0]["text"]

#             # 將文字轉換為 HTML
#             lines = text.split("\n")
#             lines = [line.strip() for line in lines]

#              #將結果轉換為 HTML 格式，同時保存為純文字檔案
#             save_txt_path = "result.txt" 
#             with open(save_txt_path, "w", encoding="utf-8") as txt_file:
#                 for line in lines:
#                     clean_line = line.replace("|", "")
#                     if clean_line.strip():
#                         txt_file.write(clean_line + "\n")

#             return render_template("index.html", lines=lines)  #將結果傳遞給模板並返回

#         return render_template("index.html", user=user)

#     else:
#         return redirect(url_for('login'))


# @app.route("/download_txt", methods=["GET"])
# def download_txt():
#     # 檔案路徑
#     file_path = "result.txt"

#     # 回傳檔案至使用者
#     return send_file(file_path, as_attachment=True, download_name="病例表格.txt")

# # 新增路由用於處理下載 Word 文件請求
# @app.route("/download_word", methods=["GET"])
# def download_word():
#     # 檔案路徑
#     txt_file_path = "result.txt"
#     word_file_path = "result.docx"

#     # 讀取 txt 檔案內容
#     with open(txt_file_path, "r", encoding="utf-8") as txt_file:
#         txt_content = txt_file.read()

#     # 創建 Word 文件
#     doc = Document()
#     doc.add_paragraph(txt_content)

#     # 儲存 Word 文件
#     doc.save(word_file_path)

#     # 回傳 Word 檔案至使用者
#     return send_file(word_file_path, as_attachment=True, download_name="病例表格.docx")


if __name__ == "__main__":
    app.secret_key = '000000'  # 設置用於會話加密的秘密金鑰
    app.run()
