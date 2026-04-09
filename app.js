async function initDashboard() {
    try {
        // 캐시를 방지하기 위해 뒤에 타임스탬프를 붙여 데이터를 새로 읽어옵니다.
        const response = await fetch(`./data/current/aggregated.json?v=${new Date().getTime()}`);
        const data = await response.json();
        
        document.getElementById('last-update').innerText = `Last Updated: ${new Date().toLocaleDateString()}`;
        renderMap(data);
        renderStateList(data);
    } catch (e) {
        console.error("Data load error:", e);
        document.getElementById('state-list').innerHTML = "<p class='text-red-500'>데이터를 불러올 수 없습니다.</p>";
    }
}

// 주 코드(TX)를 지도 데이터용 Full Name(Texas)으로 변환하는 매핑
const stateMapping = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia",
    "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois", "IN": "Indiana", "IA": "Iowa",
    "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri",
    "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming"
};

function renderMap(data) {
    const width = 800;
    const height = 500;
    // 기존 SVG 삭제 후 새로 생성
    d3.select("#map-container").selectAll("svg").remove();
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
                const fullName = d.properties.name;
                // Full Name으로 주 코드를 찾아서 데이터 매칭
                const stateCode = Object.keys(stateMapping).find(key => stateMapping[key] === fullName);
                const stateData = data[stateCode];

                if (!stateData) return "#e5e7eb"; // 데이터 없음 (회색)
                
                const status = stateData.adalimumab.status;
                const detail = stateData.adalimumab.detail;

                if (status === 'preferred') {
                    if (detail === 'Exclusive') return "#1e40af"; // Exclusive (진한 파랑 - 기획안 강조색)
                    return "#2d5a27"; // 1 of N (초록색)
                }
                return "#c8102e"; // Non-Preferred (빨간색)
            })
            .attr("stroke", "#fff")
            .attr("stroke-width", 1);
    });
}

function renderStateList(data) {
    const list = document.getElementById('state-list');
    // 데이터를 알파벳 순으로 정렬하여 리스트업
    const sortedStates = Object.entries(data).sort();
    
    list.innerHTML = sortedStates.map(([state, prod]) => `
        <div class="flex justify-between items-center p-3 border-b hover:bg-gray-50 transition">
            <span class="font-bold text-gray-700">${state}</span>
            <div class="text-right">
                <div class="text-xs font-semibold ${prod.adalimumab.status === 'preferred' ? 'text-green-600' : 'text-red-600'}">
                    ${prod.adalimumab.status.toUpperCase()}
                </div>
                <div class="text-[10px] text-gray-500">${prod.adalimumab.detail}</div>
            </div>
        </div>
    `).join('');
}

initDashboard();
