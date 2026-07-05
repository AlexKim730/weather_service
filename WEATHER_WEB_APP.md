# Flask 날씨 검색 웹 페이지 실행 및 배포

이 프로젝트는 Flask API와 정적 웹 페이지로 구성된 날씨 검색 서비스입니다.

- 로컬 Flask 앱: `app.py`
- 화면: `public/index.html`
- 공통 날씨/그래프 로직: `weather_service.py`
- Open-Meteo 호출 코드: `weather_hourly.py`
- Python 의존성: `requirements.txt`

## Render에서 입력할 값

Render의 `Name`은 서비스 이름이며 기본 주소에도 사용됩니다. 기본 주소는 보통 아래와 같은 형태가 됩니다.

```text
https://서비스이름.onrender.com
```

도메인에는 언더바 `_`를 쓰지 않는 편이 좋습니다. 아래처럼 하이픈 `-`을 사용하세요.

```text
weather-service
```

이미 사용 중인 이름이면 아래처럼 조금 더 구체적으로 바꾸면 됩니다.

```text
weather-service-alex
```

Render Web Service 설정 권장값은 다음과 같습니다.

```text
Name: weather-service
Language: Python 3
Branch: main
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

환경 변수는 따로 필요하지 않습니다.

## 로컬에서 실행

Python 패키지를 설치합니다.

```powershell
python -m pip install -r requirements.txt
```

Flask 개발 서버로 실행합니다.

```powershell
python app.py
```

브라우저에서 아래 주소를 엽니다.

```text
http://127.0.0.1:5000
```

Render와 비슷하게 Gunicorn으로 실행하려면 아래 명령을 사용합니다.

```powershell
gunicorn app:app
```

## 동작 방식

1. 사용자가 위치를 입력합니다.
2. 브라우저가 `/api/weather?location=...`를 호출합니다.
3. Flask API가 Open-Meteo Geocoding API로 위치 좌표를 찾습니다.
4. Flask API가 오늘 시간별 날씨를 가져옵니다.
5. Flask API가 Matplotlib으로 기온 그래프를 만들고 base64 이미지로 응답합니다.
6. 웹 페이지가 요약 정보, 그래프, 시간별 날씨 표를 표시합니다.

## 참고

Open-Meteo API를 호출하므로 로컬 실행과 Render 배포 환경 모두 인터넷 연결이 필요합니다.
