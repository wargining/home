import csv
import os
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "melon_top100.csv"

app = FastAPI(
    title="의진의 Melon Chart API",
    description="CSV 차트 데이터와 AI 한 줄 평을 제공하는 실습용 API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def read_chart() -> list[dict]:
    if not CSV_PATH.exists():
        raise FileNotFoundError("melon_top100.csv 파일을 찾을 수 없습니다.")

    with CSV_PATH.open(encoding="utf-8-sig", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file))

    return [
        {
            "rank": int(row["순위"]),
            "title": row["곡명"].strip(),
            "artist": row["가수"].strip(),
        }
        for row in rows
    ]


@app.get("/api/chart", tags=["chart"])
def get_chart():
    """melon_top100.csv 전체를 JSON으로 반환합니다."""
    try:
        songs = read_chart()
    except (FileNotFoundError, KeyError, ValueError) as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    return {"count": len(songs), "songs": songs}


def fallback_summary(songs: list[dict]) -> str:
    top = songs[:3]
    names = ", ".join(f"{song['rank']}위 {song['title']}" for song in top)
    return f"오늘 차트 정상에는 {names}이(가) 올라 있으며, 다양한 아티스트의 곡이 고르게 사랑받고 있어요."


@app.get("/api/summary", tags=["ai"])
def get_ai_summary():
    """오늘 차트의 특징을 AI가 한 문단으로 요약합니다."""
    songs = read_chart()
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return {
            "summary": fallback_summary(songs),
            "generated_by": "fallback",
            "message": "OPENAI_API_KEY가 없어 데이터 기반 기본 요약을 표시했습니다.",
        }

    chart_text = "\n".join(
        f"{song['rank']}위: {song['title']} - {song['artist']}" for song in songs[:20]
    )

    try:
        response = OpenAI(api_key=api_key).responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
            instructions=(
                "당신은 음악 차트 에디터입니다. 제공된 순위만 근거로 오늘 차트의 특징을 "
                "친근한 한국어 한 문단, 두 문장 이내로 요약하세요. 과장하거나 정보를 지어내지 마세요."
            ),
            input=chart_text,
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"AI 요약 생성에 실패했습니다: {error}",
        ) from error

    return {"summary": response.output_text.strip(), "generated_by": "openai"}


@app.get("/", include_in_schema=False)
def homepage():
    return FileResponse(BASE_DIR / "index.html")


app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")
