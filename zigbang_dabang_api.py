"""
직방/다방 부동산 플랫폼 API 활용 예시

주의: 이 코드들은 비공식 API를 사용하며, 플랫폼의 정책 변경으로
      작동하지 않을 수 있습니다. 교육 목적으로만 사용하세요.
"""

import requests
import pandas as pd
from typing import List, Dict, Tuple
import time


# ==================== 직방 API ====================

class ZigbangAPI:
    """직방 부동산 플랫폼 API 래퍼"""
    
    BASE_URL = "https://apis.zigbang.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_geohash(self, lat: float, lon: float, level: int = 1) -> List[Dict]:
        """
        위경도 기반 geohash 조회
        
        Args:
            lat: 위도
            lon: 경도
            level: 확대 레벨 (1-6, 클수록 넓은 범위)
        """
        url = f"{self.BASE_URL}/v2/items/geohash"
        params = {
            'lat': lat,
            'lng': lon,
            'level': level
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Geohash 조회 실패: {e}")
            return []
    
    def get_items_by_geohash(self, geohash: str) -> List[Dict]:
        """
        Geohash로 매물 조회
        
        Args:
            geohash: 지역 geohash 코드
        """
        url = f"{self.BASE_URL}/v2/items"
        params = {'geohash': geohash}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"매물 조회 실패: {e}")
            return []
    
    def get_item_detail(self, item_id: str) -> Dict:
        """
        매물 상세 정보 조회
        
        Args:
            item_id: 매물 ID
        """
        url = f"{self.BASE_URL}/v3/items/{item_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"상세 정보 조회 실패: {e}")
            return {}
    
    def search_by_location(self, lat: float, lon: float) -> pd.DataFrame:
        """
        위치 기반 매물 검색 (통합)
        
        Args:
            lat: 위도
            lon: 경도
            
        Returns:
            pd.DataFrame: 매물 정보
        """
        # 1. Geohash 조회
        geohashes = self.get_geohash(lat, lon)
        
        if not geohashes:
            return pd.DataFrame()
        
        # 2. 각 geohash별 매물 조회
        all_items = []
        for gh in geohashes:
            items = self.get_items_by_geohash(gh['geohash'])
            all_items.extend(items)
            time.sleep(0.1)  # Rate limiting
        
        # 3. DataFrame 변환
        if not all_items:
            return pd.DataFrame()
        
        df = pd.DataFrame(all_items)
        
        # 필요한 컬럼만 선택 (존재하는 경우)
        columns = ['item_id', 'sales_type', 'deposit', 'rent', 
                  'size_m2', 'floor', 'building_floor', 'title']
        
        df = df[[col for col in columns if col in df.columns]]
        
        return df


# ==================== 다방 API ====================

class DabangAPI:
    """다방 부동산 플랫폼 API 래퍼"""
    
    BASE_URL = "https://www.dabangapp.com/api"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
            'Accept': 'application/json'
        })
    
    def search_by_bbox(self, bbox: Tuple[float, float, float, float]) -> List[Dict]:
        """
        경계 상자 내 원룸 매물 검색
        
        Args:
            bbox: (남서 위도, 남서 경도, 북동 위도, 북동 경도)
        """
        url = f"{self.BASE_URL}/2/room/list/bbox-point"
        
        params = {
            'api_version': '2.0.1',
            'call_type': 'web',
            'bbox': f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('rooms', [])
        except Exception as e:
            print(f"매물 검색 실패: {e}")
            return []
    
    def get_room_detail(self, room_id: str) -> Dict:
        """
        매물 상세 정보 조회
        
        Args:
            room_id: 매물 ID
        """
        url = f"{self.BASE_URL}/2/room/detail"
        params = {'room_id': room_id}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"상세 정보 조회 실패: {e}")
            return {}
    
    def search_by_location(self, lat: float, lon: float, 
                          radius_km: float = 0.5) -> pd.DataFrame:
        """
        위치 기반 매물 검색
        
        Args:
            lat: 중심 위도
            lon: 중심 경도
            radius_km: 검색 반경 (km)
        """
        # 대략적인 경계 상자 계산 (1도 ≈ 111km)
        lat_offset = radius_km / 111.0
        lon_offset = radius_km / (111.0 * abs(lat / 90.0))
        
        bbox = (
            lat - lat_offset,  # 남서 위도
            lon - lon_offset,  # 남서 경도
            lat + lat_offset,  # 북동 위도
            lon + lon_offset   # 북동 경도
        )
        
        rooms = self.search_by_bbox(bbox)
        
        if not rooms:
            return pd.DataFrame()
        
        df = pd.DataFrame(rooms)
        
        # 필요한 컬럼만 선택
        columns = ['id', 'price_title', 'room_type', 'size_m2', 
                  'floor', 'address']
        
        df = df[[col for col in columns if col in df.columns]]
        
        return df


# ==================== 통합 API ====================

class RealEstateAggregator:
    """여러 부동산 플랫폼 데이터 통합"""
    
    def __init__(self):
        self.zigbang = ZigbangAPI()
        self.dabang = DabangAPI()
    
    def search_all_platforms(self, lat: float, lon: float) -> pd.DataFrame:
        """
        모든 플랫폼에서 매물 검색
        
        Args:
            lat: 위도
            lon: 경도
        """
        results = []
        
        # 직방 데이터
        print("📥 직방 데이터 수집 중...")
        try:
            zigbang_df = self.zigbang.search_by_location(lat, lon)
            if not zigbang_df.empty:
                zigbang_df['source'] = 'zigbang'
                results.append(zigbang_df)
                print(f"   ✓ 직방: {len(zigbang_df)}건")
        except Exception as e:
            print(f"   ✗ 직방 실패: {e}")
        
        # 다방 데이터
        print("📥 다방 데이터 수집 중...")
        try:
            dabang_df = self.dabang.search_by_location(lat, lon)
            if not dabang_df.empty:
                dabang_df['source'] = 'dabang'
                results.append(dabang_df)
                print(f"   ✓ 다방: {len(dabang_df)}건")
        except Exception as e:
            print(f"   ✗ 다방 실패: {e}")
        
        if results:
            return pd.concat(results, ignore_index=True)
        
        return pd.DataFrame()
    
    def get_statistics(self, df: pd.DataFrame) -> Dict:
        """플랫폼별 통계"""
        if df.empty:
            return {}
        
        stats = {
            'total_count': len(df),
            'by_source': df['source'].value_counts().to_dict() if 'source' in df else {}
        }
        
        return stats


# ==================== 사용 예시 ====================

def example_usage():
    """API 사용 예시"""
    
    # 강남역 좌표
    gangnam_lat = 37.4979
    gangnam_lon = 127.0276
    
    print("=" * 60)
    print("부동산 플랫폼 API 테스트")
    print("=" * 60)
    
    # 1. 직방 API 테스트
    print("\n1️⃣ 직방 API 테스트")
    print("-" * 60)
    
    zigbang = ZigbangAPI()
    zigbang_df = zigbang.search_by_location(gangnam_lat, gangnam_lon)
    
    if not zigbang_df.empty:
        print(f"총 {len(zigbang_df)}건의 매물을 찾았습니다.")
        print("\n처음 5개 매물:")
        print(zigbang_df.head())
    else:
        print("매물을 찾을 수 없습니다.")
    
    # 2. 다방 API 테스트
    print("\n2️⃣ 다방 API 테스트")
    print("-" * 60)
    
    dabang = DabangAPI()
    dabang_df = dabang.search_by_location(gangnam_lat, gangnam_lon)
    
    if not dabang_df.empty:
        print(f"총 {len(dabang_df)}건의 매물을 찾았습니다.")
        print("\n처음 5개 매물:")
        print(dabang_df.head())
    else:
        print("매물을 찾을 수 없습니다.")
    
    # 3. 통합 검색
    print("\n3️⃣ 통합 검색")
    print("-" * 60)
    
    aggregator = RealEstateAggregator()
    all_df = aggregator.search_all_platforms(gangnam_lat, gangnam_lon)
    
    if not all_df.empty:
        stats = aggregator.get_statistics(all_df)
        print(f"\n📊 통계:")
        print(f"   전체 매물: {stats['total_count']}건")
        print(f"   플랫폼별:")
        for source, count in stats['by_source'].items():
            print(f"      - {source}: {count}건")
        
        # CSV 저장
        output_file = "realestate_listings.csv"
        all_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 데이터를 {output_file}에 저장했습니다.")
    else:
        print("매물을 찾을 수 없습니다.")


# ==================== Streamlit 통합 ====================

def integrate_with_streamlit():
    """
    Streamlit 대시보드에 통합하는 방법
    
    enhanced_realestate_dashboard.py에 다음과 같이 추가:
    """
    
    example_code = '''
import streamlit as st
from zigbang_dabang_api import RealEstateAggregator

# 사이드바에 플랫폼 선택 추가
use_zigbang = st.sidebar.checkbox("직방 매물 포함", value=False)
use_dabang = st.sidebar.checkbox("다방 매물 포함", value=False)

if use_zigbang or use_dabang:
    # 좌표 가져오기 (예: 현재 선택된 지역의 중심)
    center_lat, center_lon = get_center_coords(sido, sigungu)
    
    # 매물 검색
    aggregator = RealEstateAggregator()
    
    if use_zigbang:
        zigbang_df = aggregator.zigbang.search_by_location(center_lat, center_lon)
        st.write(f"직방 매물: {len(zigbang_df)}건")
    
    if use_dabang:
        dabang_df = aggregator.dabang.search_by_location(center_lat, center_lon)
        st.write(f"다방 매물: {len(dabang_df)}건")
'''
    
    print("=" * 60)
    print("Streamlit 통합 코드")
    print("=" * 60)
    print(example_code)


if __name__ == "__main__":
    # 사용 예시 실행
    example_usage()
    
    # Streamlit 통합 가이드 출력
    print("\n" * 2)
    integrate_with_streamlit()
    
    print("\n" * 2)
    print("=" * 60)
    print("⚠️  주의사항")
    print("=" * 60)
    print("""
1. 이 코드는 비공식 API를 사용하므로 언제든 작동하지 않을 수 있습니다.
2. API 호출 시 적절한 딜레이를 두어 서버에 부담을 주지 마세요.
3. robots.txt를 확인하고 플랫폼의 이용약관을 준수하세요.
4. 상업적 용도로 사용하기 전에 법적 자문을 받으세요.
5. 개인정보가 포함된 데이터는 수집하지 마세요.

더 안전한 방법:
- 공공데이터포털의 공식 API 사용
- 플랫폼과 직접 파트너십 체결
- 공개 데이터셋 활용
    """)
