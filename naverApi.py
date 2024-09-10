import requests
import json
from urllib.parse import urlencode
from datetime import datetime
import os
from dotenv import load_dotenv

# .env 파일의 변수 로드
load_dotenv()

def search_naver(query=None, chunk=100, chunk_no=1, sort="date", 
                 do_done=False, max_record=1000, 
                 client_id=None, 
                 client_secret=None, 
                 verbose=True):

    # .env에서 CLIENT_ID와 CLIENT_SECRET 값을 가져옴
    client_id = client_id or os.getenv("CLIENT_ID")
    client_secret = client_secret or os.getenv("CLIENT_SECRET")
    
    if query is None:
        raise ValueError("검색 키워드인 query를 입력하지 않았습니다.")
    
    if chunk < 1 or chunk > 100:
        raise ValueError("chunk 요청 변수값이 허용 범위(1~100)인지 확인해 보세요.")
    
    if chunk_no < 1 or chunk_no > 1000:
        raise ValueError("chunk_no 요청 변수값이 허용 범위(1~1000)인지 확인해 보세요.")

    search_url = "https://openapi.naver.com/v1/search/news.json"
    query_encoded = urlencode({'query': query})

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

    url = f"{search_url}?{query_encoded}&display={chunk}&start={chunk_no}&sort={sort}"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"API 호출 실패: {response.status_code}")

    # JSON 응답을 파싱
    data = response.json()
    total_count = int(data['total'])

    if verbose:
        print(f"* 검색된 총 기사 건수는 {total_count}건입니다.")
        print(f"  - ({chunk}/{min(total_count, max_record)})건 호출을 진행합니다.\n")

    def parse_items(items):
        result = []
        for item in items:
            title = item.get("title", "").replace("&quot;", "").replace("<b>", "").replace("</b>", "")
            description = item.get("description", "").replace("&quot;", "").replace("<b>", "").replace("</b>", "")
            pub_date = datetime.strptime(item.get("pubDate", ""), "%a, %d %b %Y %H:%M:%S %z")
            result.append({
                "title": title,
                "description": description,
                "publish_date": pub_date
            })
        return result

    items = data['items']
    search_list = parse_items(items)
    
    if not do_done or len(search_list) >= total_count or len(search_list) >= max_record:
        return search_list
    else:
        total_count = min(total_count, max_record)
        results = search_list

        for i in range(2, (total_count // chunk) + 2):
            if verbose:
                print(f"  - ({chunk * i}/{total_count})건 호출을 진행합니다.\n")

            url = f"{search_url}?{query_encoded}&display={chunk}&start={i}&sort={sort}"
            response = requests.get(url, headers=headers)
            data = response.json()
            items = data['items']
            additional_list = parse_items(items)
            results.extend(additional_list)
            
            if len(results) >= max_record:
                break
        
        return results


# 네이버 뉴스 검색
search_list = search_naver(
    query="주식"
)

search_list_large = search_naver(
    query="주식", 
    do_done=True, 
    max_record=1000
)

# 결과 출력

if search_list_large:
    first_article = search_list_large[0]  # 첫 번째 기사
    print("첫 번째 기사 내용:")
    print(f"제목: {first_article['title']}")
    print(f"설명: {first_article['description']}")
    print(f"발행일: {first_article['publish_date']}")
else:
    print("검색 결과가 없습니다.")

# print(f"첫 번째 검색 결과: {len(search_list)}개")
# print(f"3000건 검색 결과: {len(search_list_large)}개")