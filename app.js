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

// 주 이름 매핑 테이블
const stateMapping = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO",
    "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ",
    "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
};

function getStateCode(name) {
    return stateMapping[name] || name;
}

// 2. 미국 지도 렌더링 (D3.js 기반)
function renderMap(data) {
    const width = 800;
    const height = 500;
    
    // Clear previous map if re-rendering
    d3.select("#map-container").selectAll("*").remove();

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
                if (!stateData || !stateData.adalimumab) return "#e5e7eb"; // No Data: Grey
                
                const status = stateData.adalimumab.status;
                const detail = stateData.adalimumab.detail;

                if (status === 'preferred') {
                    if (detail === 'Exclusive') {
                        return '#2D5A27'; // Preferred (Exclusive): Dark green
                    } else {
                        return '#70A266'; // Preferred (1 of N): Light green
                    }
                } else if (status === 'non-preferred') {
                    return '#C8102E'; // Non-Preferred: Red
                }
                
                return "#e5e7eb";
            })
            .attr("stroke", "#ffffff")
            .attr("stroke-width", 1)
            // Add native tooltip support
            .append("title")
            .text(d => {
                const stateName = d.properties.name; 
                const stateData = data[stateName] || data[getStateCode(stateName)];
                if (!stateData || !stateData.adalimumab) return `${stateName}: No Data`;
                return `${stateName}: ${stateData.adalimumab.status.toUpperCase()} (${stateData.adalimumab.detail})`;
            });
    });
}

function renderStateList(data) {
    const listContainer = document.getElementById('state-list');
    listContainer.innerHTML = Object.entries(data).map(([state, products]) => {
        if (!products.adalimumab) return '';
        
        let bgColor = "bg-gray-100 text-gray-800";
        if (products.adalimumab.status === 'preferred') {
            if (products.adalimumab.detail === 'Exclusive') {
                bgColor = 'bg-green-200 text-green-900 border border-green-300';
            } else {
                bgColor = 'bg-green-100 text-green-800';
            }
        } else if (products.adalimumab.status === 'non-preferred') {
            bgColor = 'bg-red-100 text-red-800';
        }

        return `
        <div class="flex justify-between items-center p-3 border-b hover:bg-gray-50 transition">
            <span class="font-medium text-gray-700">${state}</span>
            <div class="flex flex-col items-end">
                <span class="px-3 py-1 rounded-full text-xs font-bold ${bgColor}">
                    ${products.adalimumab.status.toUpperCase()}
                </span>
                <span class="text-xs text-gray-500 mt-1">${products.adalimumab.detail}</span>
            </div>
        </div>
    `}).join('');
}

initDashboard();
