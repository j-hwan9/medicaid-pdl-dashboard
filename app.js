// 1. 데이터 로드
async function initDashboard() {
    try {
        const response = await fetch('./data/current/aggregated.json');
        const pdlData = await response.json();
        
        document.getElementById('last-update').innerText = `Last Updated: ${new Date().toLocaleDateString()}`;
        renderMap(pdlData);
        renderStateList(pdlData);
    } catch (error) {
        console.error("데이터를 불러오는데 실패했습니다:", error);
        document.getElementById('state-list').innerHTML = "<p class='text-red-500'>데이터가 없습니다. 크롤러를 먼저 실행하세요.</p>";
    }
}

// 2. 미국 지도 렌더링 (D3.js 기반)
function renderMap(data) {
    const width = 800;
    const height = 500;
    const svg = d3.select("#map-container")
        .append("svg")
        .attr("viewBox", `0 0 ${width} ${height}`);

    const projection = d3.geoAlbersUsa().scale(1000).translate([width / 2, height / 2]);
    const path = d3.geoPath().projection(projection);

    d3.json("https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json").then(us => {
        svg.append("g")
            .selectAll("path")
            .data(topojson.feature(us, us.objects.states).features)
            .enter().append("path")
            .attr("d", path)
            .attr("class", "state")
            .attr("fill", d => {
                const stateName = d.properties.name; 
                const stateData = data[stateName] || data[getStateCode(stateName)];
                if (!stateData) return "#e5e7eb";
                return stateData.adalimumab.status === 'preferred' ? '#2D5A27' : '#C8102E';
            })
            .attr("stroke", "#ffffff")
            .attr("stroke-width", 1);
    });
}

function renderStateList(data) {
    const listContainer = document.getElementById('state-list');
    listContainer.innerHTML = Object.entries(data).map(([state, products]) => `
        <div class="flex justify-between items-center p-3 border-b hover:bg-gray-50 transition">
            <span class="font-medium text-gray-700">${state}</span>
            <span class="px-3 py-1 rounded-full text-xs font-bold ${
                products.adalimumab.status === 'preferred' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }">${products.adalimumab.status.toUpperCase()}</span>
        </div>
    `).join('');
}

function getStateCode(name) {
    // 주 이름 <-> 코드 변환 매핑 생략 (실제 구현 시 필요)
    return name;
}

initDashboard();