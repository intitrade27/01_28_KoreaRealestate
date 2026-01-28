# 🏠 대한민국 부동산 레이더

국토교통부 실거래가 데이터를 활용한 인터랙티브 부동산 시장 분석 대시보드

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 🌟 주요 기능

### 📍 실거래 가격 지도
- **인터랙티브 지도**: Folium 기반의 직관적인 지도 인터페이스
- **가격대별 색상 구분**: 거래가 분위수에 따른 4단계 색상 표시
  - 🟢 하위 25% (저가)
  - 🔵 25~50% (중저가)
  - 🟠 50~75% (중고가)
  - 🔴 상위 25% (고가)
- **상세 정보 팝업**: 아파트명, 거래가, 면적, 층, 거래일, 건축년도

### 📊 시세 통계 분석
- **핵심 지표**: 총 거래건수, 평균가, 중간가, 평균면적
- **평수별 가격 분포**: 산점도로 시각화
- **동별 평균 거래가**: 상위 10개 동 막대그래프
- **월별 시세 추이**: 최근 6개월 트렌드 분석
- **평수대별 분석**: 20평 이하 ~ 50평 이상 구간별 통계

### 📝 거래 목록
- **다중 필터링**: 아파트명, 동, 가격대별 필터
- **정렬 기능**: 거래일, 거래가, 평수 기준 정렬
- **CSV 다운로드**: 필터링된 데이터 엑셀 저장

## 🚀 빠른 시작

### 1. 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/realestate-radar.git
cd realestate-radar

# 가상환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 API 키를 입력하세요:

```env
JHRERSTAPI=your_kakao_rest_api_key
V_World_API=your_vworld_api_key
DATAPORTAL=your_data_portal_api_key
```

**API 키 발급 방법**은 [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)를 참고하세요.

### 3. 법정동 코드 데이터 생성

```bash
python bjdong_code_generator.py
```

### 4. 실행

```bash
streamlit run enhanced_realestate_dashboard.py
```

브라우저가 자동으로 열리며 `http://localhost:8501`에서 앱을 확인할 수 있습니다.

## 📁 프로젝트 구조

```
realestate-radar/
├── enhanced_realestate_dashboard.py  # 메인 대시보드 앱
├── bjdong_code_generator.py          # 법정동 코드 생성 도구
├── naver_kakao_integration_guide.md  # 추가 데이터 소스 가이드
├── requirements.txt                  # Python 의존성 패키지
├── INSTALLATION_GUIDE.md             # 상세 설치 가이드
├── README.md                         # 프로젝트 소개 (이 파일)
├── .env                              # 환경 변수 (Git 제외)
├── .gitignore                        # Git 제외 파일 목록
└── bjdong_codes.csv                  # 전국 법정동 코드 데이터
```

## 🛠️ 기술 스택

### Backend
- **Python 3.9+**: 주 프로그래밍 언어
- **Streamlit**: 웹 대시보드 프레임워크
- **Pandas**: 데이터 처리 및 분석
- **Requests**: HTTP API 호출

### Visualization
- **Folium**: 인터랙티브 지도 라이브러리
- **Plotly**: 고급 차트 및 그래프
- **Streamlit-Folium**: Streamlit과 Folium 통합

### Data Sources
- **국토교통부 실거래가 API**: 공식 아파트 거래 데이터
- **VWorld API**: 주소 → 좌표 변환
- **Kakao Local API**: 좌표 변환 (대안)

## 📊 데이터 출처

### 주요 데이터
- **국토교통부**: 아파트 실거래가 신고 데이터
- **공공데이터포털**: Open API 제공
- 데이터는 신고 기준으로 1-2개월 지연 발생 가능

### 법정동 코드
- **행정안전부**: 전국 법정동 코드
- 250개 시군구 완전 지원

## 🔍 주요 해결 과제

### ✅ 문제 1: 하위 구가 있는 도시 데이터 누락
**문제**: 성남시(41130)처럼 상위 코드로는 데이터 조회 불가

**해결**: 
- 수정구(41131), 중원구(41133), 분당구(41135) 등 하위 구별 코드 사용
- 전국 250개 시군구를 구 단위까지 세분화하여 `bjdong_codes.csv` 생성
- 사용자가 선택한 지역의 정확한 법정동 코드로 API 호출

### ✅ 문제 2: 법정동 코드 자동화
**문제**: 수동으로 코드를 입력하는 비효율성

**해결**:
- `bjdong_code_generator.py` 스크립트로 전국 데이터 자동 생성
- CSV 파일 캐싱으로 빠른 로드
- 시도 선택 시 자동으로 하위 시군구 필터링

### ⚠️ 문제 3: 네이버/카카오 부동산 데이터 연동
**현황**: 공식 API 없음

**해결 방안** (상세 내용은 [naver_kakao_integration_guide.md](naver_kakao_integration_guide.md) 참고):

1. **웹 스크래핑** (Selenium/Playwright)
   - 브라우저 자동화로 데이터 수집
   - 안정적이지만 느림
   
2. **비공식 모바일 API** (역분석)
   - 모바일 앱의 JSON API 활용
   - 빠르지만 구조 변경 위험
   
3. **대안 플랫폼** (권장)
   - 직방, 다방 등 오픈 API 제공 플랫폼
   - 법적 리스크 최소화

## 💡 사용 예시

### 시나리오 1: 강남구 아파트 시세 조회

1. 좌측 사이드바에서 "서울특별시" → "강남구" 선택
2. 조회 기간 "최근 6개월" 선택
3. "가격 지도" 탭에서 지역별 시세 확인
4. "시세 통계" 탭에서 평수별/동별 분석
5. "거래 목록" 탭에서 특정 아파트 필터링 및 CSV 다운로드

### 시나리오 2: 분당 vs 판교 비교

1. 분당구 데이터 조회 후 CSV 다운로드
2. 판교(분당구 내)의 특정 동 필터링
3. 평균 거래가 및 평수별 분포 비교
4. 시계열 추이로 트렌드 파악

## 🎨 UI/UX 특징

### 카카오맵 스타일 디자인
- 둥근 모서리의 가격 오버레이
- 흰색 테두리 및 그림자 효과
- 가격대별 색상 차별화

### 반응형 레이아웃
- 2열 차트 배치 (통계 탭)
- 모바일 친화적 디자인
- 다크모드 지원 (Streamlit 설정)

## 🔧 고급 기능

### 캐싱 최적화
```python
@st.cache_data(ttl=3600)  # 1시간 캐시
def get_coords_vworld(address: str):
    # 좌표 변환 결과 캐싱
    pass
```

### 다중 월 데이터 로딩
```python
# 최근 6개월 데이터를 병렬로 수집
df = fetch_multi_month_data(lawd_cd, months=6)
```

### 에러 핸들링
- API 호출 실패 시 대안 API 자동 시도
- 사용자 친화적 오류 메시지
- 빈 데이터 시 가이드 제공

## 📈 성능 지표

- **평균 로딩 시간**: 2-5초 (1개월 데이터)
- **최대 마커 수**: 100개 (지도 성능 최적화)
- **캐시 적중률**: ~80% (재방문 시)
- **API 호출 횟수**: 1-6회 (조회 기간에 따라)

## 🛡️ 보안 및 법적 고려사항

### 개인정보 보호
- API 키는 `.env` 파일로 관리
- Git에 민감 정보 커밋 방지
- 데이터는 캐시 외 저장 안 함

### 저작권 준수
- 공공데이터는 출처 명시
- 크롤링 시 robots.txt 준수
- 상업적 이용 전 라이선스 확인

## 🔮 향후 계획

- [ ] **추가 거래 유형**: 오피스텔, 빌라, 단독주택
- [ ] **전월세 시세**: 전세/월세 데이터 통합
- [ ] **실시간 알림**: 관심 지역 신규 거래 알림
- [ ] **AI 예측**: 머신러닝 기반 시세 예측
- [ ] **커뮤니티 리뷰**: 사용자 평가 및 댓글
- [ ] **모바일 앱**: React Native 기반 네이티브 앱
- [ ] **데이터베이스 연동**: PostgreSQL 기반 데이터 저장

## 🤝 기여하기

기여는 언제나 환영합니다! 다음 방법으로 참여할 수 있습니다:

1. **버그 리포트**: Issue 탭에서 버그 제보
2. **기능 제안**: Issue에서 새로운 아이디어 제안
3. **코드 기여**: Fork → 수정 → Pull Request
4. **문서 개선**: README, 가이드 문서 보완

### 기여 가이드라인
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

## 📞 문의 및 지원

- **이슈 등록**: [GitHub Issues](https://github.com/yourusername/realestate-radar/issues)
- **이메일**: your.email@example.com
- **블로그**: https://your-blog.com

## 🙏 감사의 말

이 프로젝트는 다음 오픈소스 프로젝트와 공공 데이터의 도움을 받았습니다:

- [Streamlit](https://streamlit.io/) - 웹 대시보드 프레임워크
- [Folium](https://python-visualization.github.io/folium/) - 인터랙티브 지도
- [Plotly](https://plotly.com/) - 데이터 시각화
- [국토교통부](http://www.molit.go.kr/) - 실거래가 데이터
- [공공데이터포털](https://www.data.go.kr/) - Open API 제공

## 📸 스크린샷

### 가격 지도
(지도에 가격 마커가 표시된 스크린샷)

### 시세 통계
(차트와 그래프가 있는 통계 탭 스크린샷)

### 거래 목록
(필터링된 거래 데이터 테이블 스크린샷)

---

**Made with ❤️ in Korea**

⭐ 이 프로젝트가 도움이 되었다면 Star를 눌러주세요!
