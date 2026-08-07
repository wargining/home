const toggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('.nav');

if (toggle && nav) {
  toggle.addEventListener('click', () => {
    nav.classList.toggle('open');
  });
}

const API_BASE_URL = 'http://localhost:8000';
const chartRanking = document.querySelector('#chart-ranking');
const chartInsight = document.querySelector('#chart-insight');
const chartStatus = document.querySelector('#chart-status');

function createSongRow(song) {
  const item = document.createElement('li');
  item.className = 'chart-item';

  const rank = document.createElement('strong');
  rank.className = 'chart-rank';
  rank.textContent = song.rank;

  const info = document.createElement('div');
  info.className = 'chart-song-info';

  const title = document.createElement('span');
  title.className = 'chart-song-title';
  title.textContent = song.title;

  const artist = document.createElement('span');
  artist.className = 'chart-artist';
  artist.textContent = song.artist;

  info.append(title, artist);
  item.append(rank, info);
  return item;
}

async function loadTop10() {
  try {
    const response = await fetch(`${API_BASE_URL}/songs/top10`);
    if (!response.ok) throw new Error('차트 API 응답 오류');

    const songs = await response.json();
    chartRanking.replaceChildren(...songs.map(createSongRow));
    chartStatus.textContent = '연결 완료';
    chartStatus.classList.add('connected');
  } catch (error) {
    chartRanking.innerHTML = '<li class="chart-message error">차트를 불러오지 못했습니다. FastAPI 서버를 확인해 주세요.</li>';
    chartStatus.textContent = '연결 실패';
    chartStatus.classList.add('failed');
  }
}

async function loadInsight() {
  try {
    const response = await fetch(`${API_BASE_URL}/insight`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'AI 요약 API 응답 오류');
    chartInsight.textContent = data.insight;
  } catch (error) {
    chartInsight.textContent = `한 줄 평을 불러오지 못했습니다. ${error.message}`;
    chartInsight.classList.add('error');
  }
}

if (chartRanking && chartInsight && chartStatus) {
  loadTop10();
  loadInsight();
}
