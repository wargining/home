# Melon Chart API

`melon_top100.csv`를 JSON으로 제공하고, Google Gemini API로 오늘 차트를 요약하는 FastAPI 프로젝트입니다.

## 실행 방법

```bash
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

브라우저에서 아래 주소를 확인합니다.

- 홈페이지: http://127.0.0.1:8000
- API 문서: http://127.0.0.1:8000/docs
- 전체 곡: http://127.0.0.1:8000/songs
- 상위 10곡: http://127.0.0.1:8000/songs/top10
- 가수별 곡 수: http://127.0.0.1:8000/artists
- Gemini 요약: http://127.0.0.1:8000/insight

실행 전에 `.env` 파일의 `GEMINI_API_KEY=` 뒤에 Google AI Studio에서 발급받은 키를 입력하세요. `.env`는 `.gitignore`에 포함되어 GitHub에 올라가지 않습니다.
