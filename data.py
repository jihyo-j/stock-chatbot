import pandas as pd
import json
import urllib.request

code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', encoding='euc-kr')[0]

code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)

code_df = code_df[['회사명', '종목코드']]

stock_list = code_df.values.tolist()

for stock_set in stock_list:
    item_name = stock_set[0]
    item_code = stock_set[1]

    url = f"https://api.finance.naver.com/service/itemSummary.nhn?itemcode={item_code}"
    
    try:
        with urllib.request.urlopen(url) as response:

            if response.status == 200:
                raw_data = response.read().decode('utf-8')
                
                if raw_data.strip():  
                    try:
                        json_data = json.loads(raw_data)
                        print(f"{item_name}종목의 JSON 정보:\n{json_data}")
                    except json.JSONDecodeError:
                        print(f"Failed to decode JSON for {item_name} ({item_code})")
                else:
                    print(f"No data received for {item_name} ({item_code})")
            else:
                print(f"HTTP error {response.status} for {item_name} ({item_code})")
    
    except urllib.error.URLError as e:
        print(f"Failed to fetch data for {item_name} ({item_code}): {e.reason}")

print(stock_list)
