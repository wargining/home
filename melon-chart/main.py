import csv
import os
from collections import Counter
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from google import genai


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "melon_top100.csv"
load_dotenv(BASE_DIR / ".env")

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


@app.get("/songs", tags=["1단계 · CSV API"])
def get_songs():
    """melon_top100.csv의 모든 곡을 JSON 리스트로 반환합니다."""
    try:
        return read_chart()
    except (FileNotFoundError, KeyError, ValueError) as error:
        raise HTTPException(status_code=500, detail=str(error)) from error


@app.get("/songs/top10", tags=["1단계 · CSV API"])
def get_top10():
    """순위 상위 10곡만 반환합니다."""
    return read_chart()[:10]


@app.get("/artists", tags=["1단계 · CSV API"])
def get_artists():
    """가수별 차트 진입 곡 수를 많은 순서대로 반환합니다."""
    counts = Counter(song["artist"] for song in read_chart())
    return [
        {"artist": artist, "song_count": count}
        for artist, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


@app.get("/insight", tags=["2단계 · Gemini AI"])
def get_insight():
    """Gemini가 오늘 멜론 Top 100의 특징을 한 문단으로 요약합니다."""
    songs = read_chart()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY가 없습니다. melon-chart/.env 파일에 키를 설정해 주세요.",
        )

    chart_text = "\n".join(f"{song['rank']}위: {song['title']} - {song['artist']}" for song in songs)
    prompt = f"""
다음은 오늘의 멜론 Top 100 전체 데이터입니다.

{chart_text}

이 데이터에서 실제로 확인할 수 있는 상위권 곡과 여러 곡을 올린 가수 등의 특징을
친근한 한국어 한 문단(2~3문장)으로 요약하세요.
장르 컬럼은 없으므로 곡명이나 가수만 보고 장르를 추측하지 말고, 데이터에 없는 사실은 만들지 마세요.
제목이나 목록 없이 요약 문단만 답하세요.
""".strip()

    try:
        response = genai.Client(api_key=api_key).models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
            contents=prompt,
        )
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=f"Gemini 요약 생성에 실패했습니다: {error}",
        ) from error

    if not response.text:
        raise HTTPException(status_code=502, detail="Gemini가 빈 응답을 반환했습니다.")

    return {"insight": response.text.strip(), "model": os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")}


@app.get("/", include_in_schema=False)
def homepage():
    return FileResponse(BASE_DIR / "index.html")


app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")
