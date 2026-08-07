# Melon Chart API

`melon_top100.csv`를 JSON으로 제공하고, OpenAI API로 오늘 차트를 요약해 별도의 차트 홈페이지에 표시하는 FastAPI 프로젝트입니다.

## 실행 방법

```bash
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="내_API_키"
uvicorn main:app --reload
```

브라우저에서 아래 주소를 확인합니다.

- 홈페이지: http://127.0.0.1:8000
- API 문서: http://127.0.0.1:8000/docs
- 차트 JSON: http://127.0.0.1:8000/api/chart
- AI 요약: http://127.0.0.1:8000/api/summary

`OPENAI_API_KEY`가 없으면 `/api/summary`는 수업 시연이 중단되지 않도록 데이터 기반 기본 요약을 반환합니다. API 키는 절대 GitHub에 올리지 마세요.
