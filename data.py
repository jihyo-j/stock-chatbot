import pandas as pd
import json
import urllib.request

#한국거래소 종목 코드 
code_df = pd.read_html('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13', encoding='euc-kr')[0]

# 종목코드가 6자리 설정
code_df.종목코드 = code_df.종목코드.map('{:06d}'.format)

print(code_df)