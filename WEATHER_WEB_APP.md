# Flask + Vercel 날씨 검색 웹 페이지

이 프로젝트는 Flask로 만든 날씨 API와 정적 웹 페이지로 구성되어 있습니다.

- 로컬 Flask 앱: `app.py`
- Vercel Flask 서버리스 API: `api/weather.py`
- 화면: `public/index.html`
- 공통 날씨/그래프 로직: `weather_service.py`
- Open-Meteo 호출 코드: `weather_hourly.py`
- Vercel 설정: `vercel.json`
- Python 의존성: `requirements.txt`

## 동작 방식

1. 사용자가 웹 페이지에서 위치를 입력합니다.
2. 브라우저가 `/api/weather?location=...`를 호출합니다.
3. Flask API가 Open-Meteo Geocoding API로 위치 좌표를 찾습니다.
4. Flask API가 `weather_hourly.py`의 `fetch_today_hourly_weather()`로 오늘 시간별 날씨를 불러옵니다.
5. Flask API가 Matplotlib으로 기온 그래프를 PNG 이미지로 만들고 base64 데이터 URL로 응답합니다.
6. 웹 페이지가 요약 정보, 그래프, 시간별 날씨 표를 표시합니다.

## 로컬에서 Flask로 실행

Python 패키지를 설치합니다.

```powershell
python -m pip install -r requirements.txt
```

Flask 앱을 실행합니다.

```powershell
python app.py
```

브라우저에서 아래 주소를 엽니다.

```text
http://127.0.0.1:5000
```

## Vercel 방식으로 로컬 테스트

Vercel CLI가 없다면 먼저 설치합니다.

```powershell
npm install -g vercel
```

Vercel 개발 서버를 실행합니다.

```powershell
vercel dev
```

보통 아래 주소에서 확인할 수 있습니다.

```text
http://localhost:3000
```

## Vercel에 배포

Vercel CLI로 로그인합니다.

```powershell
vercel login
```

프로젝트 폴더에서 운영 배포를 실행합니다.

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

Open-Meteo API를 호출하므로 로컬 실행과 배포 환경 모두 인터넷 연결이 필요합니다. Vercel 서버리스 환경에서는 Matplotlib 캐시 위치를 `/tmp/matplotlib`로 설정합니다.
