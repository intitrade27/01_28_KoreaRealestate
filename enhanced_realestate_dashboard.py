import streamlit as st
from dotenv import load_dotenv
import os
import requests
import folium
from streamlit_folium import st_folium
import xml.etree.ElementTree as ET
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from typing import Dict, List, Tuple, Optional
import json
from bs4 import BeautifulSoup
import re

# ==================== 설정 ====================
st.set_page_config(
    page_title="🏠 대한민국 부동산 레이더",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 환경 변수 로드
load_dotenv()
KAKAO_REST_KEY = os.getenv("JHRERSTAPI")
VWORLD_API_KEY = os.getenv("V_World_API")
MOLIT_API_KEY = os.getenv("DATAPORTAL")

# ==================== 법정동 코드 자동 로드 ====================

@st.cache_data
def load_bjdong_codes() -> pd.DataFrame:
    """
    법정동 코드 CSV 로드 (행정안전부 제공)
    CSV가 없으면 샘플 데이터 반환
    """
    # 실무에서는 행정안전부 법정동 코드 전체 CSV를 다운로드하여 사용
    # https://www.code.go.kr/stdcode/regCodeL.do
    
    sample_data = [
        # 서울
        ("서울특별시", "강남구", "11680"),
        ("서울특별시", "강동구", "11740"),
        ("서울특별시", "강북구", "11305"),
        ("서울특별시", "강서구", "11500"),
        ("서울특별시", "관악구", "11620"),
        ("서울특별시", "광진구", "11215"),
        ("서울특별시", "구로구", "11530"),
        ("서울특별시", "금천구", "11545"),
        ("서울특별시", "노원구", "11350"),
        ("서울특별시", "도봉구", "11320"),
        ("서울특별시", "동대문구", "11230"),
        ("서울특별시", "동작구", "11590"),
        ("서울특별시", "마포구", "11440"),
        ("서울특별시", "서대문구", "11410"),
        ("서울특별시", "서초구", "11650"),
        ("서울특별시", "성동구", "11200"),
        ("서울특별시", "성북구", "11290"),
        ("서울특별시", "송파구", "11710"),
        ("서울특별시", "양천구", "11470"),
        ("서울특별시", "영등포구", "11560"),
        ("서울특별시", "용산구", "11170"),
        ("서울특별시", "은평구", "11380"),
        ("서울특별시", "종로구", "11110"),
        ("서울특별시", "중구", "11140"),
        ("서울특별시", "중랑구", "11260"),
        
        # 경기도 (구가 있는 시는 구별로 분리)
        ("경기도", "수원시 장안구", "41111"),
        ("경기도", "수원시 권선구", "41113"),
        ("경기도", "수원시 팔달구", "41115"),
        ("경기도", "수원시 영통구", "41117"),
        ("경기도", "성남시 수정구", "41131"),
        ("경기도", "성남시 중원구", "41133"),
        ("경기도", "성남시 분당구", "41135"),
        ("경기도", "안양시 만안구", "41171"),
        ("경기도", "안양시 동안구", "41173"),
        ("경기도", "용인시 처인구", "41461"),
        ("경기도", "용인시 기흥구", "41463"),
        ("경기도", "용인시 수지구", "41465"),
        ("경기도", "고양시 덕양구", "41281"),
        ("경기도", "고양시 일산동구", "41285"),
        ("경기도", "고양시 일산서구", "41287"),
        ("경기도", "안산시 상록구", "41271"),
        ("경기도", "안산시 단원구", "41273"),
        ("경기도", "부천시", "41190"),
        ("경기도", "광명시", "41210"),
        ("경기도", "평택시", "41220"),
        ("경기도", "과천시", "41290"),
        ("경기도", "오산시", "41370"),
        ("경기도", "시흥시", "41390"),
        ("경기도", "군포시", "41410"),
        ("경기도", "의왕시", "41430"),
        ("경기도", "하남시", "41450"),
        ("경기도", "김포시", "41570"),
        ("경기도", "화성시", "41590"),
        ("경기도", "광주시", "41610"),
        ("경기도", "양주시", "41630"),
        ("경기도", "포천시", "41650"),
        ("경기도", "여주시", "41670"),
        ("경기도", "남양주시", "41360"),
        ("경기도", "의정부시", "41150"),
        ("경기도", "이천시", "41500"),
        ("경기도", "파주시", "41480"),
        
        # 인천
        ("인천광역시", "중구", "28110"),
        ("인천광역시", "동구", "28140"),
        ("인천광역시", "미추홀구", "28177"),
        ("인천광역시", "연수구", "28185"),
        ("인천광역시", "남동구", "28200"),
        ("인천광역시", "부평구", "28237"),
        ("인천광역시", "계양구", "28245"),
        ("인천광역시", "서구", "28260"),
        
        # 부산
        ("부산광역시", "중구", "26110"),
        ("부산광역시", "서구", "26140"),
        ("부산광역시", "동구", "26170"),
        ("부산광역시", "영도구", "26200"),
        ("부산광역시", "부산진구", "26230"),
        ("부산광역시", "동래구", "26260"),
        ("부산광역시", "남구", "26290"),
        ("부산광역시", "북구", "26320"),
        ("부산광역시", "해운대구", "26350"),
        ("부산광역시", "사하구", "26380"),
        ("부산광역시", "금정구", "26410"),
        ("부산광역시", "강서구", "26440"),
        ("부산광역시", "연제구", "26470"),
        ("부산광역시", "수영구", "26500"),
        ("부산광역시", "사상구", "26530"),
        
        # 대구
        ("대구광역시", "중구", "27110"),
        ("대구광역시", "동구", "27140"),
        ("대구광역시", "서구", "27170"),
        ("대구광역시", "남구", "27200"),
        ("대구광역시", "북구", "27230"),
        ("대구광역시", "수성구", "27260"),
        ("대구광역시", "달서구", "27290"),
        ("대구광역시", "달성군", "27710"),
        
        # 대전
        ("대전광역시", "동구", "30110"),
        ("대전광역시", "중구", "30140"),
        ("대전광역시", "서구", "30170"),
        ("대전광역시", "유성구", "30200"),
        ("대전광역시", "대덕구", "30230"),
        
        # 광주
        ("광주광역시", "동구", "29110"),
        ("광주광역시", "서구", "29140"),
        ("광주광역시", "남구", "29155"),
        ("광주광역시", "북구", "29170"),
        ("광주광역시", "광산구", "29200"),
        
        # 울산
        ("울산광역시", "중구", "31110"),
        ("울산광역시", "남구", "31140"),
        ("울산광역시", "동구", "31170"),
        ("울산광역시", "북구", "31200"),
        ("울산광역시", "울주군", "31710"),
        
        # 세종
        ("세종특별자치시", "세종시", "36110"),
    ]
    
    df = pd.DataFrame(sample_data, columns=['시도', '시군구', '법정동코드'])
    return df

# ==================== 좌표 변환 ====================

@st.cache_data(ttl=3600)
def get_coords_vworld(address: str) -> Tuple[Optional[float], Optional[float]]:
    """VWorld API를 사용한 주소 -> 좌표 변환"""
    if not VWORLD_API_KEY:
        return None, None
    
    url = 'https://api.vworld.kr/req/address'
    params = {
        'service': 'address',
        'request': 'getCoord',
        'key': VWORLD_API_KEY,
        'type': 'PARCEL',
        'address': address
    }
    
    try:
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
        if data['response']['status'] == 'OK':
            point = data['response']['result']['point']
            return float(point['y']), float(point['x'])
    except Exception as e:
        st.warning(f"좌표 변환 실패: {address} - {str(e)}")
    
    return None, None

@st.cache_data(ttl=3600)
def get_coords_kakao(address: str) -> Tuple[Optional[float], Optional[float]]:
    """Kakao API를 사용한 주소 -> 좌표 변환 (대안)"""
    if not KAKAO_REST_KEY:
        return None, None
    
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_KEY}"}
    params = {"query": address}
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        data = res.json()
        if data['documents']:
            return float(data['documents'][0]['y']), float(data['documents'][0]['x'])
    except Exception as e:
        st.warning(f"카카오 좌표 변환 실패: {address}")
    
    return None, None

# ==================== 국토부 실거래 데이터 ====================

@st.cache_data(ttl=600)
def fetch_apt_trade_data(lawd_cd: str, deal_ymd: str) -> pd.DataFrame:
    """국토부 아파트 실거래가 조회"""
    url = "https://apis.data.go.kr/1613000/RTMSDataSvcAptTrade/getRTMSDataSvcAptTrade"
    params = {
        'serviceKey': MOLIT_API_KEY,
        'LAWD_CD': lawd_cd,
        'DEAL_YMD': deal_ymd,
        'numOfRows': '1000'
    }
    
    try:
        res = requests.get(url, params=params, timeout=10)
        root = ET.fromstring(res.content)
        
        items = []
        for item in root.findall('.//item'):
            try:
                items.append({
                    'apt': item.findtext('aptNm', '').strip(),
                    'price': int(item.findtext('dealAmount', '0').replace(',', '')),
                    'dong': item.findtext('umdNm', '').strip(),
                    'jibun': item.findtext('jibun', '').strip(),
                    'area': float(item.findtext('excluUseAr', '0')),
                    'floor': item.findtext('floor', ''),
                    'year': item.findtext('dealYear', ''),
                    'month': item.findtext('dealMonth', ''),
                    'day': item.findtext('dealDay', ''),
                    'build_year': item.findtext('buildYear', ''),
                })
            except Exception as e:
                continue
        
        if items:
            df = pd.DataFrame(items)
            df['date'] = pd.to_datetime(df['year'] + '-' + df['month'] + '-' + df['day'])
            return df
        
    except Exception as e:
        st.error(f"데이터 조회 실패: {str(e)}")
    
    return pd.DataFrame()

@st.cache_data(ttl=600)
def fetch_multi_month_data(lawd_cd: str, months: int = 6) -> pd.DataFrame:
    """최근 N개월 데이터 조회"""
    all_data = []
    current_date = datetime.now()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(months):
        target_date = current_date - timedelta(days=30 * i)
        deal_ymd = target_date.strftime("%Y%m")
        
        status_text.text(f"📥 {deal_ymd} 데이터 로딩 중...")
        df = fetch_apt_trade_data(lawd_cd, deal_ymd)
        
        if not df.empty:
            all_data.append(df)
        
        progress_bar.progress((i + 1) / months)
        time.sleep(0.3)  # API 호출 제한 고려
    
    progress_bar.empty()
    status_text.empty()
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    return pd.DataFrame()

# ==================== 네이버/카카오 부동산 데이터 수집 ====================

def fetch_naver_listings(region: str) -> pd.DataFrame:
    """
    네이버 부동산 매물 정보 수집
    
    주의: 네이버 부동산은 공식 API를 제공하지 않습니다.
    아래는 개념적 예시이며, 실제 사용 시 다음 방법을 고려하세요:
    
    1. Selenium/Playwright를 사용한 브라우저 자동화
    2. 네이버 부동산 모바일 API 역분석 (비공식)
    3. RSS 피드 활용 (제한적)
    
    법적 이슈 주의:
    - robots.txt 준수
    - 과도한 요청 자제
    - 개인정보 보호
    """
    
    st.warning("""
    ⚠️ 네이버 부동산 데이터 수집 안내
    
    네이버는 공식 API를 제공하지 않습니다. 데이터 수집을 위해서는:
    
    1. **Selenium/Playwright 방식** (권장)
       - 실제 브라우저처럼 동작
       - 안정적이지만 느림
       
    2. **API 역분석 방식** (고급)
       - 네이버 모바일 앱의 API 엔드포인트 활용
       - 빠르지만 구조 변경 시 수정 필요
       
    3. **공식 데이터 사용** (최선)
       - 국토부 공공데이터 활용 (현재 사용 중)
       - 직방/다방 등 오픈 API 제공 플랫폼 활용
    """)
    
    # 샘플 반환 (실제 구현 필요)
    return pd.DataFrame()

def fetch_kakao_property_info(lat: float, lon: float, radius: int = 500) -> Dict:
    """
    카카오 지도 API로 주변 부동산 정보 조회
    
    카카오는 장소 검색 API를 제공하지만, 매물 정보는 제공하지 않습니다.
    대신 주변 부동산 중개업소 정보를 가져올 수 있습니다.
    """
    if not KAKAO_REST_KEY:
        return {}
    
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_KEY}"}
    params = {
        "query": "부동산",
        "x": lon,
        "y": lat,
        "radius": radius,
        "size": 15
    }
    
    try:
        res = requests.get(url, headers=headers, params=params, timeout=5)
        return res.json()
    except:
        return {}

# ==================== 데이터 가공 ====================

def calc_pyeong(m2: float) -> float:
    """제곱미터를 평수로 변환"""
    try:
        return round(float(m2) / 3.3058, 1)
    except:
        return 0

def format_price_to_uk(price: int) -> str:
    """만원 단위를 억/천 단위로 변환"""
    try:
        uk = price // 10000
        man = price % 10000
        
        if uk > 0:
            if man > 0:
                return f"{uk}.{man//100:02d}억"
            return f"{uk}억"
        return f"{price}만"
    except:
        return str(price)

def get_price_color(price: int, df: pd.DataFrame) -> str:
    """가격대별 색상 반환 (카카오 스타일)"""
    if df.empty:
        return "#258fff"
    
    q1 = df['price'].quantile(0.25)
    q2 = df['price'].quantile(0.50)
    q3 = df['price'].quantile(0.75)
    
    if price <= q1:
        return "#4CAF50"  # 저가 - 녹색
    elif price <= q2:
        return "#2196F3"  # 중저가 - 파란색
    elif price <= q3:
        return "#FF9800"  # 중고가 - 주황색
    else:
        return "#F44336"  # 고가 - 빨간색

# ==================== UI 구성 ====================

def render_sidebar() -> Tuple[str, str]:
    """사이드바 렌더링"""
    st.sidebar.title("🌍 지역 선택")
    
    # 법정동 코드 로드
    bjdong_df = load_bjdong_codes()
    
    # 시도 선택
    sido_list = bjdong_df['시도'].unique().tolist()
    selected_sido = st.sidebar.selectbox("시·도", sido_list, index=0)
    
    # 시군구 선택
    sigungu_list = bjdong_df[bjdong_df['시도'] == selected_sido]['시군구'].tolist()
    selected_sigungu = st.sidebar.selectbox("시·군·구", sigungu_list, index=0)
    
    # 법정동 코드 추출
    lawd_cd = bjdong_df[
        (bjdong_df['시도'] == selected_sido) & 
        (bjdong_df['시군구'] == selected_sigungu)
    ]['법정동코드'].iloc[0]
    
    st.sidebar.divider()
    
    # 조회 옵션
    st.sidebar.title("📊 조회 옵션")
    
    data_range = st.sidebar.radio(
        "데이터 범위",
        ["최근 1개월", "최근 3개월", "최근 6개월"],
        index=0
    )
    
    month_map = {"최근 1개월": 1, "최근 3개월": 3, "최근 6개월": 6}
    months = month_map[data_range]
    
    # 필터 옵션
    st.sidebar.title("🔍 필터")
    
    return selected_sido, selected_sigungu, lawd_cd, months

def render_map_tab(df: pd.DataFrame, sido: str, sigungu: str):
    """지도 탭 렌더링"""
    st.subheader("📍 실거래 가격 지도")
    
    if df.empty:
        st.warning("표시할 데이터가 없습니다.")
        return
    
    # 중심 좌표 계산
    sample_addr = f"{sido} {sigungu} {df.iloc[0]['dong']} {df.iloc[0]['jibun']}"
    center_lat, center_lon = get_coords_vworld(sample_addr)
    
    if not center_lat:
        center_lat, center_lon = get_coords_kakao(sample_addr)
    
    if not center_lat:
        st.error("지도 중심 좌표를 찾을 수 없습니다.")
        return
    
    # Folium 지도 생성
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=14,
        tiles="cartodbpositron"
    )
    
    # 마커 추가 (최대 100개)
    for idx, row in df.head(100).iterrows():
        addr = f"{sido} {sigungu} {row['dong']} {row['jibun']}"
        lat, lon = get_coords_vworld(addr)
        
        if not lat:
            lat, lon = get_coords_kakao(addr)
        
        if lat:
            price_display = format_price_to_uk(row['price'])
            color = get_price_color(row['price'], df)
            
            # 카카오 스타일 마커
            icon_html = f'''
            <div style="
                background: {color};
                color: white;
                padding: 5px 10px;
                border-radius: 15px;
                font-size: 12px;
                font-weight: bold;
                border: 2px solid white;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                white-space: nowrap;
            ">
                {price_display}
            </div>
            '''
            
            popup_html = f"""
            <div style="font-family: sans-serif; min-width: 200px;">
                <h4 style="margin: 0 0 10px 0; color: #333;">{row['apt']}</h4>
                <table style="width: 100%; font-size: 13px;">
                    <tr><td><b>거래가</b></td><td>{price_display}</td></tr>
                    <tr><td><b>면적</b></td><td>{row['py']}평 ({row['area']}㎡)</td></tr>
                    <tr><td><b>층</b></td><td>{row['floor']}층</td></tr>
                    <tr><td><b>거래일</b></td><td>{row['date'].strftime('%Y-%m-%d')}</td></tr>
                    <tr><td><b>건축년도</b></td><td>{row['build_year']}년</td></tr>
                </table>
            </div>
            """
            
            folium.Marker(
                [lat, lon],
                icon=folium.DivIcon(html=icon_html),
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(m)
    
    # 범례 추가
    legend_html = f'''
    <div style="
        position: fixed;
        bottom: 50px;
        left: 50px;
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        z-index: 1000;
        font-size: 13px;
    ">
        <h4 style="margin: 0 0 10px 0;">가격대별 색상</h4>
        <div><span style="color: #4CAF50;">●</span> 하위 25%</div>
        <div><span style="color: #2196F3;">●</span> 25~50%</div>
        <div><span style="color: #FF9800;">●</span> 50~75%</div>
        <div><span style="color: #F44336;">●</span> 상위 25%</div>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    st_folium(m, width="100%", height=600)

def render_statistics_tab(df: pd.DataFrame):
    """통계 탭 렌더링"""
    st.subheader("📊 거래 통계 및 시세 분석")
    
    if df.empty:
        st.warning("표시할 데이터가 없습니다.")
        return
    
    # 주요 지표
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 거래 건수", f"{len(df):,}건")
    
    with col2:
        avg_price = df['price'].mean()
        st.metric("평균 거래가", format_price_to_uk(int(avg_price)))
    
    with col3:
        median_price = df['price'].median()
        st.metric("중간 거래가", format_price_to_uk(int(median_price)))
    
    with col4:
        avg_py = df['py'].mean()
        st.metric("평균 면적", f"{avg_py:.1f}평")
    
    st.divider()
    
    # 차트 섹션
    col1, col2 = st.columns(2)
    
    with col1:
        # 평수별 가격 분포
        fig1 = px.scatter(
            df,
            x="py",
            y="price",
            size="price",
            color="price",
            hover_data=["apt", "dong", "floor"],
            title="평수별 거래가 분포",
            labels={"py": "면적 (평)", "price": "거래가 (만원)"},
            color_continuous_scale="Viridis"
        )
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # 동별 평균 가격
        dong_avg = df.groupby('dong')['price'].agg(['mean', 'count']).reset_index()
        dong_avg = dong_avg.sort_values('mean', ascending=False).head(10)
        
        fig2 = px.bar(
            dong_avg,
            x="dong",
            y="mean",
            title="동별 평균 거래가 (상위 10개)",
            labels={"dong": "동", "mean": "평균 거래가 (만원)"},
            color="mean",
            color_continuous_scale="Blues",
            hover_data={"count": True}
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # 시계열 분석
    if len(df['date'].unique()) > 1:
        st.subheader("📈 시세 추이")
        
        # 월별 평균 가격
        df['year_month'] = df['date'].dt.to_period('M').astype(str)
        monthly_avg = df.groupby('year_month')['price'].mean().reset_index()
        
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=monthly_avg['year_month'],
            y=monthly_avg['price'],
            mode='lines+markers',
            name='평균 거래가',
            line=dict(color='#2196F3', width=3),
            marker=dict(size=8)
        ))
        
        fig3.update_layout(
            title="월별 평균 거래가 추이",
            xaxis_title="거래 월",
            yaxis_title="평균 거래가 (만원)",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    # 평수대별 분석
    st.subheader("📐 평수대별 분석")
    
    df['py_range'] = pd.cut(
        df['py'],
        bins=[0, 20, 30, 40, 50, 100],
        labels=['20평 이하', '20-30평', '30-40평', '40-50평', '50평 이상']
    )
    
    py_stats = df.groupby('py_range')['price'].agg(['mean', 'median', 'count']).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig4 = px.bar(
            py_stats,
            x='py_range',
            y='mean',
            title="평수대별 평균 거래가",
            labels={'py_range': '평수대', 'mean': '평균 거래가 (만원)'},
            color='mean',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    with col2:
        fig5 = px.pie(
            py_stats,
            names='py_range',
            values='count',
            title="평수대별 거래 비중"
        )
        st.plotly_chart(fig5, use_container_width=True)

def render_list_tab(df: pd.DataFrame):
    """거래 목록 탭 렌더링"""
    st.subheader("📝 실거래 내역")
    
    if df.empty:
        st.warning("표시할 데이터가 없습니다.")
        return
    
    # 필터링 옵션
    col1, col2, col3 = st.columns(3)
    
    with col1:
        apt_list = ['전체'] + sorted(df['apt'].unique().tolist())
        selected_apt = st.selectbox("아파트", apt_list)
    
    with col2:
        dong_list = ['전체'] + sorted(df['dong'].unique().tolist())
        selected_dong = st.selectbox("동", dong_list)
    
    with col3:
        min_price, max_price = int(df['price'].min()), int(df['price'].max())
        price_range = st.slider(
            "가격대 (만원)",
            min_price,
            max_price,
            (min_price, max_price)
        )
    
    # 필터 적용
    filtered_df = df.copy()
    
    if selected_apt != '전체':
        filtered_df = filtered_df[filtered_df['apt'] == selected_apt]
    
    if selected_dong != '전체':
        filtered_df = filtered_df[filtered_df['dong'] == selected_dong]
    
    filtered_df = filtered_df[
        (filtered_df['price'] >= price_range[0]) &
        (filtered_df['price'] <= price_range[1])
    ]
    
    # 표시할 데이터 준비
    display_df = filtered_df[[
        'date', 'dong', 'apt', 'py', 'price', 'floor', 'build_year'
    ]].copy()
    
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    display_df['price_display'] = display_df['price'].apply(format_price_to_uk)
    display_df = display_df.rename(columns={
        'date': '거래일',
        'dong': '동',
        'apt': '아파트',
        'py': '평수',
        'price_display': '거래가',
        'floor': '층',
        'build_year': '건축년도'
    })
    
    display_df = display_df[[
        '거래일', '동', '아파트', '평수', '거래가', '층', '건축년도'
    ]]
    
    # 정렬 옵션
    sort_by = st.selectbox(
        "정렬 기준",
        ['거래일 (최신순)', '거래일 (오래된순)', '거래가 (높은순)', '거래가 (낮은순)', '평수 (큰순)', '평수 (작은순)']
    )
    
    if sort_by == '거래일 (최신순)':
        display_df = display_df.sort_values('거래일', ascending=False)
    elif sort_by == '거래일 (오래된순)':
        display_df = display_df.sort_values('거래일', ascending=True)
    elif sort_by == '거래가 (높은순)':
        display_df = display_df.sort_values('평수', ascending=False)
    elif sort_by == '거래가 (낮은순)':
        display_df = display_df.sort_values('평수', ascending=True)
    elif sort_by == '평수 (큰순)':
        display_df = display_df.sort_values('평수', ascending=False)
    elif sort_by == '평수 (작은순)':
        display_df = display_df.sort_values('평수', ascending=True)
    
    st.info(f"총 {len(display_df):,}건의 거래가 검색되었습니다.")
    
    # 데이터 표시
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=500
    )
    
    # CSV 다운로드
    csv = display_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 CSV 다운로드",
        data=csv,
        file_name=f"real_estate_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# ==================== 메인 앱 ====================

def main():
    # 타이틀
    st.title("🏠 대한민국 부동산 레이더")
    st.caption("국토교통부 실거래가 데이터 기반 부동산 시장 분석 대시보드")
    
    # 사이드바
    sido, sigungu, lawd_cd, months = render_sidebar()
    
    # 데이터 로드
    with st.spinner("📥 데이터를 불러오는 중..."):
        if months == 1:
            current_month = datetime.now().strftime("%Y%m")
            df = fetch_apt_trade_data(lawd_cd, current_month)
        else:
            df = fetch_multi_month_data(lawd_cd, months)
    
    if not df.empty:
        # 데이터 가공
        df['py'] = df['area'].apply(calc_pyeong)
        
        # 탭 구성
        tab1, tab2, tab3 = st.tabs(["📍 가격 지도", "📊 시세 통계", "📝 거래 목록"])
        
        with tab1:
            render_map_tab(df, sido, sigungu)
        
        with tab2:
            render_statistics_tab(df)
        
        with tab3:
            render_list_tab(df)
    
    else:
        st.warning(f"""
        ⚠️ {sido} {sigungu}의 최근 {months}개월 거래 데이터가 없습니다.
        
        다음을 확인해 주세요:
        - 법정동 코드가 올바른지 확인
        - 조회 기간을 변경해 보세요
        - 해당 지역의 거래가 실제로 없을 수 있습니다
        """)
    
    # 추가 정보 섹션
    with st.expander("ℹ️ 사용 안내 및 데이터 출처"):
        st.markdown("""
        ### 📌 사용 방법
        1. 좌측 사이드바에서 원하는 지역을 선택하세요
        2. 조회 기간을 설정하세요 (1개월 / 3개월 / 6개월)
        3. 각 탭에서 다양한 분석 결과를 확인하세요
        
        ### 📊 데이터 출처
        - **국토교통부** 실거래가 공개시스템
        - **공공데이터포털** API 활용
        - **VWorld / Kakao** 지도 API
        
        ### ⚠️ 주의사항
        - 실거래가는 신고 기준으로 1-2개월 지연될 수 있습니다
        - 일부 지역은 거래가 없어 데이터가 표시되지 않을 수 있습니다
        - 좌표 변환 실패 시 일부 마커가 표시되지 않을 수 있습니다
        
        ### 🔧 기술 스택
        - **Framework**: Streamlit
        - **Map**: Folium
        - **Charts**: Plotly
        - **Data**: Pandas
        """)

if __name__ == "__main__":
    main()
