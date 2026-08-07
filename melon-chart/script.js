const chartList = document.querySelector("#chart-list");
const apiStatus = document.querySelector("#api-status");
const summaryElement = document.querySelector("#ai-summary");

function renderSongs(songs) {
  chartList.innerHTML = songs.slice(0, 10).map((song) => `
    <article class="chart-row">
      <strong class="rank">${song.rank}</strong>
      <div class="song-info">
        <span class="song-title">${song.title}</span>
        <span class="artist">${song.artist}</span>
      </div>
    </article>
  `).join("");
}

async function loadChart() {
  try {
    const chartResponse = await fetch("/songs");
    if (!chartResponse.ok) throw new Error("차트 API 응답 오류");
    const songs = await chartResponse.json();
    renderSongs(songs);
    apiStatus.textContent = `${songs.length}곡 연결 완료`;
    apiStatus.classList.add("connected");
  } catch (error) {
    chartList.innerHTML = `<p class="error-message">데이터를 불러오지 못했습니다. FastAPI 서버를 확인해 주세요.</p>`;
    apiStatus.textContent = "연결 실패";
    apiStatus.classList.add("failed");
    return;
  }

  try {
    const insightResponse = await fetch("/insight");
    const insight = await insightResponse.json();
    if (!insightResponse.ok) throw new Error(insight.detail || "AI 요약 API 응답 오류");
    summaryElement.textContent = insight.insight;
  } catch (error) {
    summaryElement.textContent = error.message;
  }
}

loadChart();
