# Vercel 배포용 날씨 검색 웹 페이지

이 프로젝트는 Vercel 배포에 맞춰 정적 프론트엔드와 Python 서버리스 API로 구성되어 있습니다.

- 화면: `public/index.html`
- API: `api/weather.py`
- 배포 설정: `vercel.json`
- Python 의존성: `requirements.txt`
- 날씨 조회 공통 코드: `weather_hourly.py`

## 동작 방식

1. 사용자가 웹 페이지에서 위치를 입력합니다.
2. 브라우저가 `/api/weather?location=...` API를 호출합니다.
3. API가 Open-Meteo Geocoding API로 위치 좌표를 찾습니다.
4. API가 기존 `weather_hourly.py`의 `fetch_today_hourly_weather()`로 오늘 시간별 날씨를 불러옵니다.
5. API가 Matplotlib으로 기온 그래프를 PNG 이미지로 만들고 base64 데이터 URL로 응답합니다.
6. 웹 페이지가 요약 정보, 그래프, 시간별 날씨 표를 화면에 표시합니다.

## 로컬에서 Vercel 방식으로 실행

Vercel CLI가 없다면 먼저 설치합니다.

```powershell
npm install -g vercel
```

Python 패키지를 설치합니다.

```powershell
python -m pip install -r requirements.txt
```

로컬 개발 서버를 실행합니다.

```powershell
vercel dev
```

터미널에 표시되는 로컬 주소를 브라우저에서 엽니다. 보통 아래 주소입니다.

```text
http://localhost:3000
```

## Vercel에 배포

Vercel CLI로 로그인합니다.

```powershell
vercel login
```

프로젝트 폴더에서 배포합니다.

```powershell
vercel
```

운영 배포가 필요하면 아래 명령을 사용합니다.

```powershell
vercel --prod
```

## Vercel 대시보드로 배포

1. 이 프로젝트를 GitHub 저장소에 올립니다.
2. Vercel에서 `Add New Project`를 선택합니다.
3. 해당 저장소를 import 합니다.
4. Framework Preset은 `Other`로 둡니다.
5. 별도 Build Command는 비워둡니다.
6. Deploy를 누릅니다.

## 참고

Open-Meteo API를 호출하므로 배포된 서비스와 로컬 개발 환경 모두 인터넷 연결이 필요합니다. Matplotlib은 서버리스 함수 안에서 그래프를 생성하며, Vercel 환경에서 쓸 수 있도록 캐시 위치를 `/tmp/matplotlib`로 설정했습니다.
