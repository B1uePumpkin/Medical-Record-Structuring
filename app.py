# -*- coding: utf-8 -*-

import openai
from dotenv import dotenv_values
from flask import Flask
openai.api_key = dotenv_values(".env")['API_KEY']
app = Flask(__name__)
prompt = """
我希望將以下資料抽取部分欄位轉換成有主次關係的表格呈現結構化資料,除了專有名詞外請都用繁體中文顯示,內容必須完整的顯示
===
SNOMED:59000-A-81403. 

CLINICAL HISTORY AND DIAGNOSIS:

Bloody stool

DIAGNOSIS:   

Intestine, large, labeled as "Ascending colon", endoscopic biopsy

                                                      --- Adenocarcinoma

GROSS DESCRIPTION:  

The specimen submitted consists of 5 tissue fragments measuring up

to 0.5 x 0.2 x 0.2 cm in size, fixed in formalin. They are gray

white and elastic.

All for section is taken.   

MICROSCOPIC DESCRIPTION:

Section shows fragments of necrotic debris and colon mucosa with

proliferation and infiltration of irregular hyperchromatic neoplas-

tic glands arranged mainly in complicated tubulo-papillary fashion,  

a moderately differentiated adenocarcinoma. Remnants suggestive of a

pre-existing adenoma are not seen.

REFERENCE:   

S04-05069

Gall bladder, cholecystectomy

                                --- Acute gangrenous cholecystitis  

S01-01737   

Skin, nasal bridge, excisional biopsy --- Basal cell carcinoma

                                   PAGE 1/1

                            --- END OF REPORT ---


住院醫師:                   病理醫師: Shu-Han Huang, M.D./SWH

                                               病解專醫字第000477號  
===

輸出範例:  

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
"""

@app.route("/")
def index():
    # 生成結果
    res = openai.Completion.create(model="text-davinci-003", prompt=prompt, max_tokens=1000)
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



if __name__ == "__main__":
    app.run()