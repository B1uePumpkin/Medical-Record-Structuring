# -*- coding: utf-8 -*-

import openai
from dotenv import dotenv_values
from flask import Flask, render_template, request

openai.api_key = dotenv_values(".env")['API_KEY']
app = Flask(__name__, template_folder='frontend')
app.static_folder = 'frontend'

# 預先定義的固定prompt
fixed_prompt = """
首先完整查看使用者輸入的病例內容，再來根據這些信息產生一份完整的病例表格，格式內容請參考下面輸出範例，沒有或空白的資料請填入"N/A"，請確保欄位和資料內容須正確相符、完整且必須對齊，表格結構需要正確，最後檢查內容無誤再以原文或英文輸出
以下是輸出範例格式:
===

| 欄位 | 資料 |  

| 診斷資料號 | 資料號 |

| 病史 | CLINICAL HISTORY |

| 診斷 | DIAGNOSIS |

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

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 獲取表單中的用戶輸入prompt
        user_input = request.form["prompt"]
        # 將用戶輸入的prompt和預先定義的固定prompt結合
        combined_prompt = fixed_prompt + user_input
        # 生成結果
        res = openai.Completion.create(
            model="text-davinci-003",
            prompt=combined_prompt,
            max_tokens=1000
        )
        text = res["choices"][0]["text"]

        # 將 text 轉換為 HTML
        lines = text.split("\n")

        # 渲染模板並返回 HTML
        return render_template("index.html", lines=lines)

    # 顯示輸入表單
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
