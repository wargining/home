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
    const [chartResponse, summaryResponse] = await Promise.all([
      fetch("/api/chart"),
      fetch("/api/summary"),
    ]);
    if (!chartResponse.ok) throw new Error("차트 API 응답 오류");
    const chart = await chartResponse.json();
    renderSongs(chart.songs);
    apiStatus.textContent = `${chart.count}곡 연결 완료`;
    apiStatus.classList.add("connected");

    if (!summaryResponse.ok) throw new Error("AI 요약 API 응답 오류");
    const summary = await summaryResponse.json();
    summaryElement.textContent = summary.summary;
    if (summary.generated_by === "fallback") summaryElement.title = summary.message;
  } catch (error) {
    chartList.innerHTML = `<p class="error-message">데이터를 불러오지 못했습니다. FastAPI 서버를 확인해 주세요.</p>`;
    apiStatus.textContent = "연결 실패";
    apiStatus.classList.add("failed");
    summaryElement.textContent = error.message;
  }
}

loadChart();
