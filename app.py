# -*- coding: utf-8 -*-

import openai
from dotenv import dotenv_values
from flask import Flask, request

openai.api_key = dotenv_values(".env")['API_KEY']
app = Flask(__name__)

# 預先定義的固定prompt
fixed_prompt = """
首先完整查看使用者輸入的病例內容，再來根據這些信息產生一份完整的病例表格，格式內容請參考下面輸出範例，請確保欄位籍資料內容須正確相符、完整並對齊，最後檢查內容無誤再以繁體中文輸出，專有名詞以及姓名除外。
以下是輸出範例格式:
===

| 欄位 | 資料 |  

| --- | --- |

| 診斷資料號 | 資料號 |

| 診斷結果 | 結果 |

| 組織片數 | 片數 |

| 組織尺寸 | 切片尺寸大小 |  

| 組織外觀 | 顏色，形狀 |

...以此類推
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

        # 轉換為HTML
        html = "<html><body><table>"
        lines = text.split("\n")
        for line in lines:
            if "|" in line:
                # 移除空格並分割成欄位
                columns = [col.strip() for col in line.split("|")]
                # 構建HTML表格行
                html += "<tr>"
                for col in columns:
                    html += f"<td>{col}</td>"
                html += "</tr>"
        html += "</table></body></html>"

        # 直接返回HTML內容
        return html

    # 顯示輸入表單
    return "<html><body><form method='post'><label for='prompt'>請輸入病例：</label><br/> <textarea name='prompt' rows='50' cols='100'></textarea><input type='submit' value='提交'></form></body></html>"

if __name__ == "__main__":
    app.run()
