# -*- coding: utf-8 -*-
from flask import *
from dotenv import dotenv_values
from docx import Document
import openai
import pymongo
from bson.objectid import ObjectId


app = Flask(
    __name__,
    static_folder = 'static',
    template_folder = 'templates',
    static_url_path='/static'
    )


# 從 .env 載入配置
dotenv_config = dotenv_values(".env")

# 設定 OpenAI API 金鑰
openai.api_key = dotenv_config.get('OPENAI_API_KEY')

# 設定 MongoDB 連接
mongo_client = pymongo.MongoClient(dotenv_config.get('MONGODB_URI'))
db = mongo_client["medical_web"]
print("成功連接至 MongoDB")

################################################## Prompt設置 ##########################################################
# query_fields
query_fields = [
    {'id': 'query_diagnosis_id', 'label': '診斷資料號', 'db_key': '診斷資料號'},
    {'id': 'query_medical_history', 'label': '病史', 'db_key': '病史'},
    {'id': 'query_diagnosis_result', 'label': '診斷結果', 'db_key': '診斷結果'},
    {'id': 'query_tissue_count', 'label': '組織片數', 'db_key': '組織片數'},
    {'id': 'query_tissue_size', 'label': '組織尺寸', 'db_key': '組織尺寸'},
    {'id': 'query_tissue_location', 'label': '組織部位', 'db_key': '組織部位'},
    {'id': 'query_biopsy_type', 'label': '切片方式', 'db_key': '切片方式'},
    {'id': 'query_treatment_method', 'label': '處理方式', 'db_key': '處理方式'},
    {'id': 'query_tissue_color', 'label': '組織顏色', 'db_key': '組織顏色'},
    {'id': 'query_tissue_consistency', 'label': '組織形狀', 'db_key': '組織形狀'},
    {'id': 'query_microscopic_examination', 'label': '顯微鏡檢查', 'db_key': '顯微鏡檢查'},
    {'id': 'query_reference_data', 'label': '參考資料', 'db_key': '參考資料'},
    {'id': 'query_attending_physician', 'label': '住院醫師', 'db_key': '住院醫師'},
    {'id': 'query_pathologist', 'label': '病理醫師', 'db_key': '病理醫師'},
    {'id': 'query_pathologist_license', 'label': '病理專醫字', 'db_key': '病理專醫字'}
]
# 預先定義的固定 prompt
fixed_prompt = """
首先完整查看使用者輸入的病例內容，再來根據這些信息產生一份完整的病例表格，格式內容請參考下面輸出範例，沒有或空白的資料請填入"N/A"，請確保欄位和資料內容須正確相符、完整且必須對齊，表格結構需要正確，最後檢查內容無誤再以原文或英文輸出
以下是輸出範例格式:
===

{
  "診斷資料號": "資料號",
  "病史": "病人病史",
  "診斷結果": "診斷結果",
  "組織片數": "片數",
  "組織尺寸": "切片尺寸大小",
  "組織部位": "組織部位或切片部位",
  "切片方式": "組織獲得方法",
  "處理方式": "組織處理方式",
  "組織顏色": "顏色",
  "組織形狀": "形狀",
  "顯微鏡檢查": "顯微鏡檢查結果",
  "參考資料": "參考資料內容",
  "住院醫師": "醫師姓名",
  "病理醫師": "醫師姓名",
  "病理專醫字": "醫師姓名"
}

===
"""

################################################## 頁面路由設定 ##########################################################

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
    
# 關於頁面路由
@app.route('/instructions')
def show_instructions():
    return render_template('instructions.html')

# 控制面板路由
@app.route('/control_panel')
def show_control_panel():
    # 使用全局的query_fields
    return render_template('control_panel.html', query_fields=query_fields, msg='')

####################################################### 登入登出 #####################################################

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

################################################ 生成及處理資料 ############################################################
# 處理API溝通 POST 請求
@app.route("/generate", methods=["POST"])
def generate():

    # 結合固定 prompt 和使用者輸入的文字
    user_input = request.form["prompt"]
    combined_prompt = fixed_prompt + user_input

    # 使用 OpenAI API 生成結果
    res = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "現在你是一位可以精準地將重點提煉出並整理成表格的助手"},
            {"role": "user", "content": combined_prompt}
        ],
        max_tokens=1000,
        temperature=0,
        
    )


    # 提取助手的回應文本
    print("Response from OpenAI API:", res)  # 打印 res 的內容
    response_content = res["choices"][0]["message"]["content"]  # 修改這行以提取助手的回應文本

    # 返回結果
    return render_template("confirm.html", data =response_content, username=session['username'])

########################################## 處理檔案下載功能 ##################################################################

@app.route("/download_txt", methods=["GET"])
def download_txt():
    # 檔案路徑
    file_path = "result.txt"

    # 回傳檔案至使用者
    return send_file(file_path, as_attachment=True, attachment_filename="病例表格.txt")

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
    return send_file(word_file_path, as_attachment=True, attachment_filename="病例表格.docx")

######################################### 資料庫操作 ###################################################################
# 將OpenAI的回應儲存到MongoDB
@app.route("/save_to_mongoDB", methods=["POST"])
def save_to_mongoDB():
    # 從表單數據中獲取數據
    data = request.form.get('data')
    print("接收到的數據:", data)

    # 將接收到的字符串數據轉換成字典
    import json
    data_dict = json.loads(data)

    # 存儲到MongoDB
    collection = db.responses
    result = collection.insert_one(data_dict)
    if result.acknowledged:
        print("資料存儲成功" + str(result.inserted_id))
        return redirect(url_for('home', alert="資料存儲成功"))
    else:
        return redirect(url_for('home', alert="資料存儲失敗"))

# 從MongoDB中獲取OpenAI的回應
from flask import request, render_template, redirect, url_for

@app.route("/search", methods=["POST"])
def search():
    query_conditions = {}
    # 使用全域的query_fields
    for field in query_fields:
        checkbox_field_id = 'use_' + field['id']
        input_field_id = field['db_key']
        if request.form.get(checkbox_field_id) == 'on' and request.form.get(input_field_id):
            query_conditions[field['db_key']] = request.form[input_field_id]

    if not query_conditions:
        msg = "請至少選擇一個查詢條件"
        return render_template("control_panel.html", query_fields=query_fields, msg=msg)
    
    # 查詢MongoDB
    collection = db.responses
    results = collection.find(query_conditions)
    result_list = list(results) if results else []
    print("查詢條件:", query_conditions)
    print("查詢结果:", result_list)


    # 返回結果
    if result_list:
        return render_template("control_panel.html", query_fields=query_fields, data=result_list)
    else:
        msg = "沒有符合條件的資料"
        return render_template("control_panel.html", query_fields=query_fields, msg=msg)

# 刪除MongoDB中的OpenAI回應
@app.route("/delete", methods=["POST"])
def delete():
    # 從表單數據中獲取數據
    data_id = request.form.get('data_id')
    print(f"刪除的資料ID:{data_id}")

    # 刪除MongoDB中的數據
    collection = db.responses
    result = collection.delete_one({'_id': ObjectId(data_id)})
    if result.deleted_count > 0:
        msg="資料刪除成功"
        print(msg)
        return redirect(url_for('home', alert=msg))
    else:
        msg="資料刪除失敗"
        print(msg)
        redirect(url_for('home', alert=msg))

# 更新MongoDB中的OpenAI回應
@app.route("/update_or_delete", methods=["POST"])
def update_or_delete():
    data_id = request.form.get('data_id')
    action = request.form.get('action')
    
    if action == 'update':
        病史 = request.form.get('病史')
        診斷資料號 = request.form.get('診斷資料號')
        print(f"更新資料的ID: {data_id}")
        print(f"更新的病史: {病史}")
        print(f"更新的診斷資料號: {診斷資料號}")
        
        # 將接收到的字串轉換成字典
        data_dict = {
            "病史": 病史,
            "診斷資料號": 診斷資料號
        }

        # 更新MongoDB中的數據
        collection = db.responses
        result = collection.update_one({'_id': ObjectId(data_id)}, {'$set': data_dict})
        if result.modified_count > 0:
            msg = "資料更新成功"
            print(msg)
            return redirect(url_for('home', alert=msg))
        else:
            msg = "資料更新失敗"
            print(msg)
            return redirect(url_for('home', alert=msg))
    elif action == 'delete':
        print(f"刪除資料的ID: {data_id}")
        
        # 刪除MongoDB中的數據
        collection = db.responses
        result = collection.delete_one({'_id': ObjectId(data_id)})
        if result.deleted_count > 0:
            msg = "資料刪除成功"
            print(msg)
            return redirect(url_for('home', alert=msg))
        else:
            msg = "資料刪除失敗"
            print(msg)
            return redirect(url_for('home', alert=msg))
    else:
        msg = "無效的操作"
        print(msg)
        return redirect(url_for('home', alert=msg))


################################### 結束 ######################################################################
if __name__ == "__main__":
    app.secret_key = '000000'  # 設置用於會話加密的秘密金鑰
    app.run(debug=True)
