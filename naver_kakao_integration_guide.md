# 네이버/카카오 부동산 데이터 연동 기술 가이드

## 📋 목차
1. [개요](#개요)
2. [네이버 부동산 데이터 수집](#네이버-부동산-데이터-수집)
3. [카카오 부동산 데이터 수집](#카카오-부동산-데이터-수집)
4. [대안 솔루션](#대안-솔루션)
5. [법적 고려사항](#법적-고려사항)

---

## 개요

네이버와 카카오는 **공식 부동산 매물 API를 제공하지 않습니다**. 따라서 데이터를 수집하기 위해서는 다음과 같은 방법을 사용해야 합니다:

### 가능한 접근 방법
1. **웹 스크래핑** (Selenium/Playwright)
2. **모바일 API 역분석** (비공식)
3. **공식 대안 플랫폼** (직방, 다방 등)

---

## 네이버 부동산 데이터 수집

### 1. Selenium을 활용한 웹 스크래핑 (권장)

#### 설치
```bash
pip install selenium webdriver-manager
```

#### 구현 예시
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

def fetch_naver_land_listings(region_code: str, trade_type: str = "A1") -> pd.DataFrame:
    """
    네이버 부동산 매물 크롤링
    
    Args:
        region_code: 지역 코드 (예: "1168000000" - 강남구)
        trade_type: 거래 유형 (A1: 매매, B1: 전세, B2: 월세)
    
    Returns:
        pd.DataFrame: 매물 정보
    """
    
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 백그라운드 실행
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    # 드라이버 초기화
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        # 네이버 부동산 URL
        url = f"https://new.land.naver.com/complexes?ms={region_code}&a={trade_type}&e=RETAIL"
        driver.get(url)
        time.sleep(3)  # 페이지 로딩 대기
        
        # 스크롤하여 더 많은 데이터 로드
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # 매물 리스트 추출
        listings = []
        
        # 아파트 단지 요소 찾기
        complex_items = driver.find_elements(By.CSS_SELECTOR, ".item_complex")
        
        for item in complex_items:
            try:
                # 단지명
                name = item.find_element(By.CSS_SELECTOR, ".text").text
                
                # 가격 정보
                price_elem = item.find_element(By.CSS_SELECTOR, ".price")
                price = price_elem.text
                
                # 면적 정보
                area_elem = item.find_element(By.CSS_SELECTOR, ".spec")
                area = area_elem.text
                
                listings.append({
                    'name': name,
                    'price': price,
                    'area': area,
                    'source': 'naver'
                })
                
            except Exception as e:
                continue
        
        return pd.DataFrame(listings)
    
    finally:
        driver.quit()

# 사용 예시
df = fetch_naver_land_listings("1168000000")  # 강남구
print(df.head())
```

### 2. Playwright를 활용한 고급 스크래핑

```bash
pip install playwright
playwright install chromium
```

```python
from playwright.sync_api import sync_playwright
import pandas as pd

def fetch_with_playwright(region: str) -> pd.DataFrame:
    """Playwright를 사용한 네이버 부동산 크롤링"""
    
    with sync_playwright() as p:
        # 브라우저 실행
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        # 네이버 부동산 접속
        page.goto(f'https://new.land.naver.com/complexes?ms={region}')
        page.wait_for_load_state('networkidle')
        
        # 데이터 추출
        listings = page.query_selector_all('.item_complex')
        
        data = []
        for listing in listings:
            name = listing.query_selector('.text').inner_text()
            price = listing.query_selector('.price').inner_text()
            
            data.append({
                'name': name,
                'price': price
            })
        
        browser.close()
        
        return pd.DataFrame(data)
```

### 3. 네이버 모바일 API 역분석 (고급)

네이버 부동산 모바일 앱은 JSON API를 사용합니다. 이를 활용할 수 있습니다:

```python
import requests
import json

def fetch_naver_api(lat: float, lon: float, zoom: int = 15) -> dict:
    """
    네이버 부동산 비공식 API 호출
    
    주의: 이 방법은 네이버의 서비스 약관을 위반할 수 있으며,
    API 구조가 변경되면 작동하지 않을 수 있습니다.
    """
    
    # 네이버 부동산 모바일 API 엔드포인트
    url = "https://m.land.naver.com/cluster/clusterList"
    
    # 요청 파라미터
    params = {
        'cortarNo': '1168000000',  # 지역 코드
        'view': 'atcl',
        'rletTpCd': 'APT',  # 아파트
        'tradTpCd': 'A1',   # 매매
        'z': zoom,
        'lat': lat,
        'lon': lon,
    }
    
    # 헤더 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
        'Referer': 'https://m.land.naver.com/',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        return response.json()
    except Exception as e:
        print(f"API 호출 실패: {e}")
        return {}

# 사용 예시
data = fetch_naver_api(37.5172, 127.0473)  # 강남역 좌표
print(json.dumps(data, indent=2, ensure_ascii=False))
```

---

## 카카오 부동산 데이터 수집

### 1. 카카오 지도 API 활용 (공식)

카카오는 직접적인 매물 정보를 제공하지 않지만, 주변 부동산 중개업소 정보를 가져올 수 있습니다:

```python
import requests
import os

KAKAO_REST_KEY = os.getenv("KAKAO_REST_KEY")

def search_real_estate_agencies(lat: float, lon: float, radius: int = 1000):
    """카카오 지도 API로 주변 부동산 중개업소 검색"""
    
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    
    headers = {
        "Authorization": f"KakaoAK {KAKAO_REST_KEY}"
    }
    
    params = {
        "query": "부동산",
        "x": lon,
        "y": lat,
        "radius": radius,
        "size": 15,
        "sort": "distance"
    }
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    agencies = []
    for doc in data.get('documents', []):
        agencies.append({
            'name': doc['place_name'],
            'address': doc['address_name'],
            'phone': doc.get('phone', ''),
            'distance': doc['distance']
        })
    
    return agencies

# 사용 예시
agencies = search_real_estate_agencies(37.5172, 127.0473)
for agency in agencies:
    print(f"{agency['name']} - {agency['phone']}")
```

### 2. 카카오맵 스크래핑

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def scrape_kakao_map(keyword: str, region: str):
    """카카오맵에서 부동산 정보 스크래핑"""
    
    driver = webdriver.Chrome()
    
    try:
        # 카카오맵 검색
        search_query = f"{region} {keyword}"
        url = f"https://map.kakao.com/?q={search_query}"
        driver.get(url)
        time.sleep(3)
        
        # 검색 결과 추출
        results = driver.find_elements(By.CSS_SELECTOR, ".placelist > .PlaceItem")
        
        places = []
        for result in results:
            name = result.find_element(By.CSS_SELECTOR, ".head_item .tit_name").text
            address = result.find_element(By.CSS_SELECTOR, ".info_item .addr").text
            
            places.append({
                'name': name,
                'address': address
            })
        
        return places
    
    finally:
        driver.quit()
```

---

## 대안 솔루션

### 1. 공공 API 활용 (추천)

네이버/카카오 대신 공공데이터를 활용하는 것이 가장 안전하고 합법적입니다:

```python
# 이미 구현된 국토부 API
def fetch_molit_data(lawd_cd: str, deal_ymd: str):
    """국토교통부 실거래가 API (공식)"""
    url = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"
    # ... (기존 코드)
```

### 2. 직방 API (비공식)

직방은 비공식적으로 API를 제공합니다:

```python
def fetch_zigbang_items(lat: float, lon: float):
    """직방 매물 검색 (비공식 API)"""
    
    # 1단계: 지역 ID 조회
    geohash_url = "https://apis.zigbang.com/v2/items/geohash"
    params = {
        'lat': lat,
        'lng': lon,
        'level': 1
    }
    
    response = requests.get(geohash_url, params=params)
    geohash_data = response.json()
    
    # 2단계: 매물 목록 조회
    items = []
    for gh in geohash_data:
        item_url = f"https://apis.zigbang.com/v2/items?geohash={gh['geohash']}"
        item_response = requests.get(item_url)
        items.extend(item_response.json())
    
    return items

# 사용 예시
items = fetch_zigbang_items(37.5172, 127.0473)
for item in items[:5]:
    print(f"{item.get('title')} - {item.get('sales_price')}만원")
```

### 3. 다방 API (비공식)

```python
def fetch_dabang_rooms(bbox: tuple):
    """
    다방 원룸 매물 검색
    
    Args:
        bbox: (남서쪽 위도, 남서쪽 경도, 북동쪽 위도, 북동쪽 경도)
    """
    
    url = "https://www.dabangapp.com/api/2/room/list/bbox-point"
    
    params = {
        'api_version': '2.0.1',
        'call_type': 'web',
        'bbox': f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
    }
    
    response = requests.get(url, params=params)
    return response.json()
```

---

## 법적 고려사항

### ⚠️ 주의사항

1. **robots.txt 준수**
   ```python
   # robots.txt 확인
   import urllib.robotparser
   
   rp = urllib.robotparser.RobotFileParser()
   rp.set_url("https://land.naver.com/robots.txt")
   rp.read()
   
   can_fetch = rp.can_fetch("*", "https://land.naver.com/complexes")
   print(f"크롤링 가능 여부: {can_fetch}")
   ```

2. **요청 제한**
   ```python
   import time
   from functools import wraps
   
   def rate_limit(min_interval: float = 1.0):
       """API 호출 간격 제한 데코레이터"""
       def decorator(func):
           last_called = [0.0]
           
           @wraps(func)
           def wrapper(*args, **kwargs):
               elapsed = time.time() - last_called[0]
               if elapsed < min_interval:
                   time.sleep(min_interval - elapsed)
               result = func(*args, **kwargs)
               last_called[0] = time.time()
               return result
           
           return wrapper
       return decorator
   
   @rate_limit(2.0)  # 2초마다 1회 호출
   def fetch_data():
       # ... API 호출
       pass
   ```

3. **User-Agent 설정**
   ```python
   headers = {
       'User-Agent': 'MyRealEstateApp/1.0 (contact@example.com)',
       'From': 'contact@example.com'
   }
   ```

### 권장 사항

1. **공식 API 우선 사용**
   - 국토교통부 실거래가 API
   - 한국부동산원 API
   - 지자체 공공데이터

2. **스크래핑 시 주의**
   - 과도한 요청 자제
   - 캐싱 활용
   - 에러 처리 철저히

3. **개인정보 보호**
   - 개인 연락처 수집 금지
   - 데이터 저장 시 암호화
   - GDPR/개인정보보호법 준수

---

## 실무 통합 예시

### 다중 소스 데이터 통합

```python
class RealEstateDataAggregator:
    """여러 소스에서 부동산 데이터를 수집하고 통합"""
    
    def __init__(self):
        self.sources = {
            'molit': self.fetch_molit,
            'zigbang': self.fetch_zigbang,
            'dabang': self.fetch_dabang
        }
    
    def fetch_all(self, region: str) -> pd.DataFrame:
        """모든 소스에서 데이터 수집"""
        all_data = []
        
        for source_name, fetch_func in self.sources.items():
            try:
                data = fetch_func(region)
                data['source'] = source_name
                all_data.append(data)
            except Exception as e:
                print(f"{source_name} 데이터 수집 실패: {e}")
        
        if all_data:
            return pd.concat(all_data, ignore_index=True)
        return pd.DataFrame()
    
    def fetch_molit(self, region: str) -> pd.DataFrame:
        # 국토부 API 호출
        pass
    
    def fetch_zigbang(self, region: str) -> pd.DataFrame:
        # 직방 API 호출
        pass
    
    def fetch_dabang(self, region: str) -> pd.DataFrame:
        # 다방 API 호출
        pass

# 사용
aggregator = RealEstateDataAggregator()
df = aggregator.fetch_all("강남구")
```

---

## 결론

네이버와 카카오의 부동산 데이터를 수집하는 것은 기술적으로 가능하지만, 다음 사항을 고려해야 합니다:

### ✅ 권장
- 국토교통부 등 공공 API 우선 활용
- 직방, 다방 등 비공식 API 활용
- 스크래핑 시 법적/윤리적 기준 준수

### ❌ 비권장
- 무분별한 대량 크롤링
- robots.txt 무시
- 개인정보 수집

**최선의 방법**: 현재 구현된 국토부 API를 기반으로 하고, 필요시 직방/다방 등의 보완적 데이터를 추가하는 것을 추천합니다.
