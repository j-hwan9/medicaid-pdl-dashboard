async function initDashboard() {
    try {
        const response = await fetch('./data/current/aggregated.json');
        const data = await response.json();
        
        document.getElementById('last-update').innerText = `Last Updated: ${new Date().toLocaleDateString()}`;
        renderMap(data);
        renderStateList(data);
    } catch (e) {
        console.error("Data load error:", e);
    }
}

function renderMap(data) {
    const width = 800;
    const height = 500;
    const svg = d3.select("#map-container").append("svg").attr("viewBox", `0 0 ${width} ${height}`);
    const projection = d3.geoAlbersUsa().scale(1000).translate([width / 2, height / 2]);
    const path = d3.geoPath().projection(projection);

    d3.json("https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json").then(us => {
        svg.append("g")
            .selectAll("path")
            .data(topojson.feature(us, us.objects.states).features)
            .enter().append("path")
            .attr("d", path)
            .attr("fill", d => {
                const stateName = d.properties.name;
                // 주 이름(Full Name)을 코드(TX, FL 등)로 변환하는 로직 필요 (여기선 생략)
                // 데이터의 키값과 매칭하여 색상 결정
                return "#2D5A27"; // 기본 초록색
            })
            .attr("stroke", "#fff");
    });
}

function renderStateList(data) {
    const list = document.getElementById('state-list');
    list.innerHTML = Object.entries(data).map(([state, prod]) => `
        <div class="flex justify-between p-2 border-b">
            <span><b>${state}</b></span>
            <span>${prod.adalimumab.detail}</span>
        </div>
    `).join('');
}

initDashboard();
