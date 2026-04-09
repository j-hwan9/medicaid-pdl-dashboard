// ── 설정 ──────────────────────────────────────────────
const DATA_URL = './data/current/aggregated.json';
const SELECTED_DRUG = 'adalimumab'; // 추후 드롭다운으로 확장 가능

const COLOR = {
  preferred:     '#2D5A27',
  'non-preferred': '#C8102E',
  error:         '#6B7280',
  not_found:     '#D1D5DB',
  default:       '#E5E7EB',
};

// ── 데이터 로드 ────────────────────────────────────────
async function loadData() {
  const res = await fetch(DATA_URL);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ── 지도 렌더링 (D3 + TopoJSON) ───────────────────────
async function renderMap(stateData) {
  const container = document.getElementById('map-container');
  const W = container.clientWidth || 700;
  const H = 500;

  const svg = d3.select('#map-container')
    .append('svg')
    .attr('viewBox', `0 0 ${W} ${H}`)
    .attr('preserveAspectRatio', 'xMidYMid meet')
    .style('width', '100%')
    .style('height', '100%');

  const projection = d3.geoAlbersUsa().fitSize([W, H], { type: 'Sphere' });
  const path = d3.geoPath().projection(projection);

  // TopoJSON 로드
  const us = await d3.json('https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json');
  const fipsToAbbr = getFipsMap();

  // Tooltip
  const tooltip = d3.select('body').append('div')
    .style('position', 'absolute')
    .style('background', 'white')
    .style('border', '1px solid #E5E7EB')
    .style('border-radius', '8px')
    .style('padding', '8px 12px')
    .style('font-size', '13px')
    .style('pointer-events', 'none')
    .style('box-shadow', '0 2px 8px rgba(0,0,0,0.15)')
    .style('opacity', 0);

  svg.selectAll('path')
    .data(topojson.feature(us, us.objects.states).features)
    .join('path')
    .attr('d', path)
    .attr('fill', d => {
      const abbr = fipsToAbbr[d.id];
      const drugData = stateData[abbr]?.[SELECTED_DRUG];
      return COLOR[drugData?.status] ?? COLOR.default;
    })
    .attr('stroke', 'white')
    .attr('stroke-width', 0.8)
    .style('cursor', 'pointer')
    .on('mouseover', function(event, d) {
      const abbr = fipsToAbbr[d.id];
      const drugData = stateData[abbr]?.[SELECTED_DRUG];
      d3.select(this).attr('opacity', 0.8);
      tooltip
        .style('opacity', 1)
        .html(`
          <div class="font-bold">${abbr}</div>
          <div>Status: <span style="color:${COLOR[drugData?.status] ?? '#000'};font-weight:600">${drugData?.status ?? 'N/A'}</span></div>
          ${drugData?.pa_required ? `<div>PA: ${drugData.pa_required}</div>` : ''}
          ${drugData?.detail ? `<div class="text-gray-400 text-xs">${drugData.detail}</div>` : ''}
        `);
    })
    .on('mousemove', function(event) {
      tooltip
        .style('left', (event.pageX + 12) + 'px')
        .style('top', (event.pageY - 28) + 'px');
    })
    .on('mouseout', function() {
      d3.select(this).attr('opacity', 1);
      tooltip.style('opacity', 0);
    });
}

// ── State List 렌더링 ──────────────────────────────────
function renderList(stateData) {
  const container = document.getElementById('state-list');
  container.innerHTML = '';

  const states = Object.entries(stateData).sort(([a], [b]) => a.localeCompare(b));

  for (const [abbr, drugs] of states) {
    const drug = drugs[SELECTED_DRUG];
    if (!drug) continue;

    const color = COLOR[drug.status] ?? COLOR.default;
    const label = drug.status.charAt(0).toUpperCase() + drug.status.slice(1);

    const el = document.createElement('div');
    el.className = 'flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-50 transition-colors';
    el.innerHTML = `
      <span class="font-medium text-gray-700">${abbr}</span>
      <div class="flex items-center gap-2">
        ${drug.pa_required && drug.pa_required !== 'No PA'
          ? `<span class="text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full">PA</span>`
          : ''}
        <span class="text-xs font-semibold px-3 py-1 rounded-full text-white" style="background:${color}">${label}</span>
      </div>
    `;
    container.appendChild(el);
  }
}

// ── 요약 카드 렌더링 ───────────────────────────────────
function renderSummary(stateData) {
  const counts = { preferred: 0, 'non-preferred': 0, error: 0, other: 0 };
  for (const drugs of Object.values(stateData)) {
    const s = drugs[SELECTED_DRUG]?.status ?? 'other';
    if (s in counts) counts[s]++;
    else counts.other++;
  }

  const summaryEl = document.getElementById('summary-cards');
  if (!summaryEl) return;
  summaryEl.innerHTML = `
    <div class="bg-green-50 border border-green-200 rounded-xl p-4 text-center">
      <div class="text-3xl font-bold text-green-700">${counts.preferred}</div>
      <div class="text-sm text-green-600 mt-1">Preferred</div>
    </div>
    <div class="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
      <div class="text-3xl font-bold text-red-700">${counts['non-preferred']}</div>
      <div class="text-sm text-red-600 mt-1">Non-Preferred</div>
    </div>
    <div class="bg-gray-50 border border-gray-200 rounded-xl p-4 text-center">
      <div class="text-3xl font-bold text-gray-500">${counts.other + counts.error}</div>
      <div class="text-sm text-gray-500 mt-1">Pending / Error</div>
    </div>
  `;
}

// ── FIPS → State Abbr 매핑 ─────────────────────────────
function getFipsMap() {
  return {
    "01":"AL","02":"AK","04":"AZ","05":"AR","06":"CA","08":"CO","09":"CT",
    "10":"DE","12":"FL","13":"GA","15":"HI","16":"ID","17":"IL","18":"IN",
    "19":"IA","20":"KS","21":"KY","22":"LA","23":"ME","24":"MD","25":"MA",
    "26":"MI","27":"MN","28":"MS","29":"MO","30":"MT","31":"NE","32":"NV",
    "33":"NH","34":"NJ","35":"NM","36":"NY","37":"NC","38":"ND","39":"OH",
    "40":"OK","41":"OR","42":"PA","44":"RI","45":"SC","46":"SD","47":"TN",
    "48":"TX","49":"UT","50":"VT","51":"VA","53":"WA","54":"WV","55":"WI",
    "56":"WY"
  };
}

// ── 메인 ──────────────────────────────────────────────
(async () => {
  try {
    const json = await loadData();
    const stateData = json.states ?? json; // 구버전 호환

    document.getElementById('last-update').textContent =
      `Last Updated: ${json.last_updated ?? 'Unknown'}`;

    renderSummary(stateData);
    await renderMap(stateData);
    renderList(stateData);

  } catch (err) {
    console.error('Failed to load data:', err);
    document.getElementById('state-list').innerHTML =
      `<p class="text-red-400 text-center py-10">데이터 로드 실패: ${err.message}</p>`;
  }
})();
