# 부동산 레이더 설치 및 실행 가이드

## 📦 필수 패키지 설치

### requirements.txt 생성

```txt
streamlit>=1.32.0
python-dotenv>=1.0.0
requests>=2.31.0
folium>=0.15.0
streamlit-folium>=0.18.0
streamlit-geolocation>=0.1.0
pandas>=2.2.0
plotly>=5.18.0
beautifulsoup4>=4.12.0
lxml>=5.1.0
selenium>=4.16.0
webdriver-manager>=4.0.0
playwright>=1.40.0
```

### 설치 명령어

```bash
# 가상환경 생성 (선택사항이지만 권장)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# Playwright 브라우저 설치 (크롤링 사용 시)
playwright install chromium
```

## 🔑 환경 변수 설정

### .env 파일 생성

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
# 카카오 REST API 키
JHRERSTAPI=your_kakao_rest_api_key_here

# VWorld API 키
V_World_API=your_vworld_api_key_here

# 공공데이터포털 API 키
DATAPORTAL=your_data_portal_api_key_here
```

### API 키 발급 방법

#### 1. 카카오 REST API 키

1. [Kakao Developers](https://developers.kakao.com/) 접속
2. 로그인 후 "내 애플리케이션" 클릭
3. "애플리케이션 추가하기" 클릭
4. 앱 이름 입력 후 생성
5. "앱 키" 섹션에서 "REST API 키" 복사

#### 2. VWorld API 키

1. [VWorld 오픈API](https://www.vworld.kr/dev/v4dv_2ddataguide2_s001.do) 접속
2. 회원가입 및 로그인
3. "인증키 발급" 메뉴 클릭
4. API 신청서 작성 (무료)
5. 발급된 인증키 복사

#### 3. 공공데이터포털 API 키

1. [공공데이터포털](https://www.data.go.kr/) 접속
2. 회원가입 및 로그인
3. "아파트 실거래 상세 자료" 검색
4. "국토교통부_아파트 매매 신고 조회 서비스" 선택
5. "활용신청" 클릭
6. 승인 대기 (통상 1-2시간 소요)
7. "마이페이지 > 오픈API > 개발계정" 에서 인증키 확인

## 🚀 실행 방법

### 기본 실행

```bash
streamlit run enhanced_realestate_dashboard.py
```

### 포트 변경하여 실행

```bash
streamlit run enhanced_realestate_dashboard.py --server.port 8080
```

### 브라우저 자동 열림 비활성화

```bash
streamlit run enhanced_realestate_dashboard.py --server.headless true
```

## 📁 프로젝트 구조

```
realestate-radar/
├── enhanced_realestate_dashboard.py  # 메인 대시보드
├── bjdong_code_generator.py          # 법정동 코드 생성 스크립트
├── naver_kakao_integration_guide.md  # 네이버/카카오 연동 가이드
├── requirements.txt                  # 패키지 목록
├── .env                               # 환경 변수 (비공개)
├── .gitignore                        # Git 제외 파일
├── bjdong_codes.csv                  # 법정동 코드 데이터
└── README.md                         # 프로젝트 설명
```

## 🛠️ 법정동 코드 데이터 생성

```bash
# 법정동 코드 CSV 생성
python bjdong_code_generator.py
```

이 명령어를 실행하면 `bjdong_codes.csv` 파일이 생성됩니다.

## ⚙️ Streamlit 설정 (선택사항)

`.streamlit/config.toml` 파일을 생성하여 Streamlit 설정을 커스터마이즈할 수 있습니다:

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501

[browser]
gatherUsageStats = false
```

## 🐛 문제 해결

### 문제 1: API 키 인증 오류

**증상**: "Unauthorized" 또는 "Invalid API Key" 오류

**해결**:
1. `.env` 파일의 API 키가 올바른지 확인
2. 공공데이터포털 API는 승인 후 사용 가능 (1-2시간 소요)
3. API 키에 불필요한 공백이 없는지 확인

### 문제 2: 좌표 변환 실패

**증상**: 지도에 마커가 표시되지 않음

**해결**:
1. VWorld 또는 Kakao API 키 확인
2. 두 API 중 하나만 작동해도 됨
3. 네트워크 연결 확인

### 문제 3: 데이터가 조회되지 않음

**증상**: "데이터가 없습니다" 메시지

**해결**:
1. 해당 지역/기간에 실제 거래가 없을 수 있음
2. 법정동 코드가 올바른지 확인
3. 조회 기간을 늘려보기 (6개월로 변경)
4. 국토부 API 서비스 상태 확인

### 문제 4: Streamlit 실행 오류

**증상**: `ModuleNotFoundError` 또는 임포트 오류

**해결**:
```bash
# 패키지 재설치
pip install -r requirements.txt --force-reinstall

# 가상환경 재생성
deactivate
rm -rf venv
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## 📊 성능 최적화

### 1. 캐싱 활용

Streamlit의 `@st.cache_data` 데코레이터가 적용되어 있어 동일한 데이터는 재사용됩니다.

### 2. API 호출 제한

- VWorld/Kakao API: 좌표 변환 시 캐싱 (TTL: 1시간)
- 국토부 API: 데이터 조회 시 캐싱 (TTL: 10분)

### 3. 지도 마커 제한

성능을 위해 지도에는 최대 100개의 마커만 표시됩니다.

## 🔒 보안 주의사항

### .gitignore 설정

```gitignore
# 환경 변수
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Streamlit
.streamlit/secrets.toml

# 데이터 캐시
*.pkl
*.cache
```

### API 키 보호

- **절대** API 키를 코드에 직접 입력하지 마세요
- Git에 `.env` 파일을 커밋하지 마세요
- 공개 저장소에 업로드할 때는 `.env.example` 만 포함하세요

## 📱 배포 (Streamlit Cloud)

### 1. Streamlit Cloud에 배포

1. [Streamlit Cloud](https://streamlit.io/cloud) 가입
2. GitHub 저장소 연결
3. 앱 배포 설정
4. "Secrets" 섹션에서 환경 변수 입력:

```toml
JHRERSTAPI = "your_kakao_key"
V_World_API = "your_vworld_key"
DATAPORTAL = "your_dataportal_key"
```

### 2. 로컬 서버 배포

```bash
# 백그라운드 실행
nohup streamlit run enhanced_realestate_dashboard.py &

# 또는 tmux/screen 사용
tmux new -s realestate
streamlit run enhanced_realestate_dashboard.py
# Ctrl+B, D로 detach
```

## 📈 향후 개선 계획

- [ ] 오피스텔, 빌라 거래 데이터 추가
- [ ] 전월세 시세 정보 통합
- [ ] 실시간 시세 알림 기능
- [ ] 투자 수익률 계산기
- [ ] 관심 지역 즐겨찾기
- [ ] 데이터 내보내기 (Excel, PDF)
- [ ] 모바일 최적화

## 💡 사용 팁

1. **빠른 지역 변경**: 사이드바에서 시도/시군구를 선택하면 자동으로 데이터가 업데이트됩니다.

2. **필터 활용**: 거래 목록 탭에서 아파트명, 동, 가격대로 필터링할 수 있습니다.

3. **CSV 다운로드**: 거래 목록 탭 하단의 "CSV 다운로드" 버튼으로 데이터를 저장할 수 있습니다.

4. **지도 확대**: 지도에서 마커를 클릭하면 상세 정보를 볼 수 있습니다.

5. **기간 선택**: 최근 1개월 데이터는 빠르게 로드되고, 6개월 데이터는 더 많은 정보를 제공합니다.

## 🤝 기여하기

버그 리포트, 기능 제안, 코드 기여를 환영합니다!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

문제가 발생하거나 질문이 있으시면 이슈를 등록해 주세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
