# -*- coding: utf-8 -*-

import openai
from dotenv import dotenv_values
from flask import Flask, request

openai.api_key = dotenv_values(".env")['API_KEY']
app = Flask(__name__)

# 預先定義的固定prompt
fixed_prompt = """
請先完整查看輸入內容
根據以下結構產生完整表格，此表格只是架構範例，內容請看輸入病例:
輸出範例(請根據使用者輸入內容做判斷，勿直接填入範例內容):
===

| 欄位 | 資料 |  

| --- | --- |

| 診斷資料號 | 59000-A-81403 |

| 診斷結果 | Bloody stool   |

| 組織片數 | 5片 |

| 組織尺寸 | 0.1*0.1*0.1 cm |  

| 組織外觀 | 灰 |

...以此類推
===
除了專有名詞，其餘請以繁體中文顯示，內容須正確完整並對齊
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
    return "<html><body><form method='post'><label for='prompt'>請輸入病例：</label><input type='text' name='prompt' size='100'><input type='submit' value='提交'></form></body></html>"

if __name__ == "__main__":
    app.run()
