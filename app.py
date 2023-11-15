# -*- coding: utf-8 -*-

import openai
from dotenv import dotenv_values
from flask import Flask, request

openai.api_key = dotenv_values(".env")['API_KEY']
app = Flask(__name__)

# 預先定義的固定prompt
fixed_prompt = """
首先完整查看使用者輸入的病例內容，再來根據這些信息產生一份完整的病例表格，格式內容請參考下面輸出範例，請確保欄位籍資料內容須正確相符、完整且對齊，表格結構需要正確，最後檢查內容無誤再以繁體中文輸出，專有名詞以及姓名除外。
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
        html = """
        <html>
            <head>
                <style>
                    body {
                        font-family: 'Arial', sans-serif;
                        margin: 50px;
                        background-color: #f8f9fa; /* 背景顏色 */
                    }

                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 20px;
                        background-color: #ffffff; /* 表格背景顏色 */
                    }

                    th, td {
                        border: 1px solid #dddddd;
                        text-align: left;
                        padding: 8px;
                    }

                    th {
                        background-color: #f2f2f2;
                    }

                    #back-btn {
                        padding: 15px 20px;
                        background-color: #007bff;
                        color: #ffffff;
                        border: none;
                        cursor: pointer;
                    }
                </style>
            </head>
            <body>
                <table>
        """

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

        html += """
                </table>
                <button id='back-btn' onclick='goBack()'>返回</button>
                <script>
                    function goBack() {
                        window.history.back();
                    }
                </script>
            </body>
        </html>
        """

        # 直接返回HTML內容
        return html

    # 顯示輸入表單
    return """
    <html>
        <body>
            <form method='post'>
                <label for='prompt'>請輸入病例：</label><br/>
                <textarea name='prompt' rows='10' style='width: 100%; height: 300px; font-size: 16px;'></textarea>
                <br/>
                <input type='submit' value='提交' style='background-color: #007bff; color: #ffffff; padding: 15px 20px;'>
            </form>
        </body>
    </html>
    """


if __name__ == "__main__":
    app.run()
