import openai
from dotenv import dotenv_values
openai.api_key = dotenv_values('.env')["API_KEY"]

from types import resolve_bases

prompt = """
我希望將以下資料抽取部分欄位轉換成以表格呈現的結構化資料
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

 住院醫師:                  病理醫師: Shu-Han Huang, M.D./SWH

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
res = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens = 1000
    )

print (res["choices"][0]["text"])