// SIGNAL COMMAND PRO v2.0 - Complete JavaScript with Traffic Lights & Green Wave

let map, waveMap, trafficMap;
let trafficData = { junctions: [], segments: [], green_waves: [] };
let markers = {}, signalMarkers = {}, segmentLines = {}, routePolylines = [];
let isLiveMode = true;
let selectedHour = new Date().getHours();
let emergencyMode = false;
let predictionHistory = [];
let sensorDataPoints = [];
let forecastChart, trafficPatternChart, situationDistChart, signalTimingChart, vehicleTypesChart, topRoadsChart, classDistChart, featureImportanceChart, sensorStreamChart;
let selectedJunction = null;
let currentRoutes = [];
let selectedRouteIndex = 0;

const JUNCTIONS = [
    { id: 1, name: "MG Road & Jubilee Hills", lat: 17.4251, lng: 78.4495 },
    { id: 2, name: "Banjara Hills Road No. 36", lat: 17.4156, lng: 78.4375 },
    { id: 3, name: "Kukatpally Main Road", lat: 17.4943, lng: 78.3996 },
    { id: 4, name: "Ameerpet Crossroads", lat: 17.4379, lng: 78.4483 },
    { id: 5, name: "Hitech City Gate", lat: 17.4417, lng: 78.3819 },
    { id: 6, name: "Charminar Circle", lat: 17.3616, lng: 78.4747 },
    { id: 7, name: "Madhapur IT Park", lat: 17.4509, lng: 78.3856 },
    { id: 8, name: "Gachibowli Junction", lat: 17.4400, lng: 78.3489 },
    { id: 9, name: "Koti College Road", lat: 17.3856, lng: 78.4747 },
    { id: 10, name: "Shamshabad Airport", lat: 17.2403, lng: 78.4294 },
    { id: 11, name: "Secunderabad Station", lat: 17.4349, lng: 78.5031 },
    { id: 12, name: "Dilsukhnagar", lat: 17.3683, lng: 78.4012 },
    { id: 13, name: "Uppal Kalan", lat: 17.4089, lng: 78.5631 },
    { id: 14, name: "LB Nagar", lat: 17.3456, lng: 78.5528 },
    { id: 15, name: "Shankarmutt", lat: 17.4067, lng: 78.4678 }
];

const SEGMENTS = [
    { id: 1, from: 1, to: 2, name: "MG Road - Banjara Hills" },
    { id: 2, from: 1, to: 4, name: "MG Road - Ameerpet" },
    { id: 3, from: 2, to: 5, name: "Banjara Hills - Hitech City" },
    { id: 4, from: 2, to: 7, name: "Banjara Hills - Madhapur" },
    { id: 5, from: 3, to: 8, name: "Kukatpally - Gachibowli" },
    { id: 6, from: 4, to: 9, name: "Ameerpet - Koti" },
    { id: 7, from: 5, to: 7, name: "Hitech City - Madhapur" },
    { id: 8, from: 6, to: 9, name: "Charminar - Koti" },
    { id: 9, from: 7, to: 8, name: "Madhapur - Gachibowli" },
    { id: 10, from: 9, to: 15, name: "Koti - Shankarmutt" },
    { id: 11, from: 11, to: 14, name: "Secunderabad - LB Nagar" },
    { id: 12, from: 10, to: 12, name: "Airport - Dilsukhnagar" },
    { id: 13, from: 12, to: 6, name: "Dilsukhnagar - Charminar" },
    { id: 14, from: 13, to: 11, name: "Uppal - Secunderabad" },
    { id: 15, from: 14, to: 13, name: "LB Nagar - Uppal" },
    { id: 16, from: 15, to: 4, name: "Shankarmutt - Ameerpet" },
    { id: 17, from: 3, to: 5, name: "Kukatpally - Hitech City" },
    { id: 18, from: 8, to: 5, name: "Gachibowli - Hitech City" },
    { id: 19, from: 1, to: 11, name: "MG Road - Secunderabad" },
    { id: 20, from: 6, to: 12, name: "Charminar - Dilsukhnagar" },
    { id: 21, from: 4, to: 7, name: "Ameerpet - Madhapur" },
    { id: 22, from: 2, to: 4, name: "Banjara Hills - Ameerpet" },
    { id: 23, from: 9, to: 6, name: "Koti - Charminar" },
    { id: 24, from: 12, to: 14, name: "Dilsukhnagar - LB Nagar" },
    { id: 25, from: 15, to: 1, name: "Shankarmutt - MG Road" }
];

const GREEN_WAVE_ROUTES = [
    { id: 1, name: "MG Road Corridor", segments: [1, 2, 6, 10], color: "#22c55e" },
    { id: 2, name: "IT Hub Corridor", segments: [3, 7, 9], color: "#3b82f6" },
    { id: 3, name: "Airport Expressway", segments: [12, 20, 13], color: "#f97316" }
];

const REAL_HOURLY = {
    0: 25, 1: 18, 2: 12, 3: 8, 4: 6, 5: 15,
    6: 45, 7: 78, 8: 92, 9: 75, 10: 58, 11: 62,
    12: 68, 13: 72, 14: 65, 15: 70, 16: 85, 17: 95,
    18: 88, 19: 65, 20: 48, 21: 38, 22: 32, 23: 28
};

function initApp() {
    initMap();
    initClock();
    initTabs();
    populateJunctionSelects();
    initHourBars();
    loadAllData();
    setInterval(loadAllData, 5000);
}

function initMap() {
    trafficMap = L.map('trafficMap').setView([17.3850, 78.4867], 12);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap contributors © CARTO',
        maxZoom: 19
    }).addTo(trafficMap);
}

function initClock() {
    function updateClock() {
        const now = new Date();
        document.getElementById('clockTime').textContent = now.toLocaleTimeString('en-US', { hour12: true });
        document.getElementById('clockDate').textContent = now.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
    }
    updateClock();
    setInterval(updateClock, 1000);
}

function initTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(btn.dataset.tab).classList.add('active');
            
            if (btn.dataset.tab === 'forecast') initForecastChart();
            if (btn.dataset.tab === 'analysis') initAnalysisCharts();
            if (btn.dataset.tab === 'segments') initSegmentsChart();
            if (btn.dataset.tab === 'model') initModelCharts();
            if (btn.dataset.tab === 'sensors') initSensorChart();
            if (btn.dataset.tab === 'greenwave') initGreenWaveMap();
        });
    });
}

function populateJunctionSelects() {
    const originSelect = document.getElementById('originSelect');
    const destSelect = document.getElementById('destSelect');
    const signalJunctionSelect = document.getElementById('signalJunctionSelect');
    JUNCTIONS.forEach(j => {
        const option = `<option value="${j.id}">${j.name}</option>`;
        originSelect.innerHTML += option;
        destSelect.innerHTML += option;
        signalJunctionSelect.innerHTML += option;
    });
}

function initHourBars() {
    const container = document.getElementById('hourBars');
    const hourClickBars = document.getElementById('hourClickBars');
    for (let h = 0; h < 24; h++) {
        const score = REAL_HOURLY[h];
        const pct = (score / 100) * 100;
        const color = pct < 30 ? '#22c55e' : pct < 60 ? '#eab308' : pct < 80 ? '#f97316' : '#ef4444';
        
        const bar = document.createElement('div');
        bar.className = 'hour-bar';
        bar.style.background = color;
        bar.style.height = Math.max(pct * 0.3, 4) + 'px';
        bar.onclick = () => selectHour(h);
        container.appendChild(bar);
        
        const clickBar = document.createElement('div');
        clickBar.className = 'hcb-bar';
        clickBar.style.background = color;
        clickBar.textContent = h;
        clickBar.onclick = () => { setTimeTravelMode(); selectHour(h); };
        hourClickBars.appendChild(clickBar);
    }
}

function setLiveMode() {
    isLiveMode = true;
    document.getElementById('liveModeBtn')?.classList.add('active');
    document.getElementById('timeTravelBtn')?.classList.remove('active');
    document.getElementById('timeDisplay').style.display = 'flex';
    document.getElementById('timeSliderContainer').style.display = 'none';
    selectedHour = new Date().getHours();
    loadAllData();
}

function setTimeTravelMode() {
    isLiveMode = false;
    document.getElementById('timeTravelBtn')?.classList.add('active');
    document.getElementById('liveModeBtn')?.classList.remove('active');
    document.getElementById('timeDisplay').style.display = 'none';
    document.getElementById('timeSliderContainer').style.display = 'block';
}

function selectHour(h) {
    selectedHour = h;
    document.getElementById('timeSlider').value = h;
    updateTimeSlider();
    loadAllData();
}

function updateTimeSlider() {
    const h = parseInt(document.getElementById('timeSlider').value);
    selectedHour = h;
    const label = h === 0 ? '12:00 AM' : h < 12 ? `${h}:00 AM` : h === 12 ? '12:00 PM' : `${h-12}:00 PM`;
    document.getElementById('sliderLabel').textContent = label;
    document.getElementById('currentTimeDisplay').textContent = label;
    loadAllData();
}

function toggleEmergency() {
    emergencyMode = document.getElementById('emergencyCheck').checked;
    const banner = document.getElementById('emergencyBanner');
    banner.style.display = emergencyMode ? 'block' : 'none';
    if (emergencyMode) {
        document.getElementById('emergencyETA').textContent = '3 min';
    }
}

async function loadAllData() {
    try {
        const response = await fetch('/api/traffic');
        trafficData = await response.json();
        document.getElementById('flaskStatus').querySelector('.status-dot').className = 'status-dot connected';
        document.getElementById('flaskStatus').querySelector('.status-label').textContent = 'Flask API Connected';
    } catch {
        document.getElementById('flaskStatus').querySelector('.status-dot').className = 'status-dot disconnected';
        document.getElementById('flaskStatus').querySelector('.status-label').textContent = 'Demo Mode';
        trafficData = generateSimulatedData();
    }
    updateUI();
    updateMap();
    updateSignalTimings();
    updateAlerts();
    updateSegmentsTable();
    updateSignalOptimizer();
    updateGreenWaveRoutes();
}

function generateSimulatedData() {
    const baseFactor = REAL_HOURLY[selectedHour] / 60;
    const junctions = JUNCTIONS.map(j => {
        const vehicles = Math.round(40 + baseFactor * 80 * (0.8 + Math.random() * 0.4));
        const score = Math.min(vehicles / 1.5, 100);
        const nsState = Math.random() > 0.5 ? 'green' : Math.random() > 0.5 ? 'yellow' : 'red';
        const ewState = nsState === 'green' ? 'red' : nsState === 'red' ? 'green' : 'yellow';
        return {
            id: j.id, name: j.name, lat: j.lat, lng: j.lng, vehicleCount: vehicles, score,
            situation: getSituation(score), traffic_light: {
                phase: nsState === 'green' ? 'NS_GREEN' : ewState === 'green' ? 'EW_GREEN' : 'ALL_RED',
                north_south: nsState, east_west: ewState,
                queue_length_north: Math.round(vehicles * 0.2), queue_length_south: Math.round(vehicles * 0.15),
                queue_length_east: Math.round(vehicles * 0.15), queue_length_west: Math.round(vehicles * 0.1)
            }
        };
    });
    const segments = SEGMENTS.map(s => {
        const fromJ = junctions.find(j => j.id === s.from);
        const toJ = junctions.find(j => j.id === s.to);
        const avgScore = ((fromJ?.score || 50) + (toJ?.score || 50)) / 2 * (0.8 + Math.random() * 0.4);
        return { ...s, score: Math.round(avgScore), situation: getSituation(avgScore), green_wave: [1, 2, 3, 7, 9, 12].includes(s.id) };
    });
    return { junctions, segments, green_waves: calculateLocalGreenWaves() };
}

function calculateLocalGreenWaves() {
    return GREEN_WAVE_ROUTES.map(r => ({
        route_id: r.id, route_name: r.name, color: r.color,
        segments: r.segments, synchronization_score: Math.round(75 + Math.random() * 20),
        total_travel_time: Math.round(5 + Math.random() * 10),
        optimal_speed: 40
    }));
}

function getSituation(score) {
    if (score < 30) return 'Low';
    if (score < 60) return 'Normal';
    if (score < 80) return 'Heavy';
    return 'High';
}

function getSituationColor(sit) {
    return { Low: '#22c55e', Normal: '#eab308', Heavy: '#f97316', High: '#ef4444' }[sit] || '#3b82f6';
}

function updateUI() {
    const totalVehicles = trafficData.junctions.reduce((s, j) => s + j.vehicleCount, 0);
    const avgScore = trafficData.junctions.reduce((s, j) => s + (j.score || 50), 0) / trafficData.junctions.length;
    const criticalCount = trafficData.segments.filter(s => (s.score || 50) > 75).length;
    const citySit = getSituation(avgScore);
    const totalStops = trafficData.junctions.reduce((s, j) => {
        const tl = j.traffic_light || {};
        return s + (tl.queue_length_north || 0) + (tl.queue_length_south || 0) + (tl.queue_length_east || 0) + (tl.queue_length_west || 0);
    }, 0);
    
    document.getElementById('vehiclesToday').textContent = (totalVehicles * 12).toLocaleString();
    document.getElementById('co2Tracked').textContent = Math.round(totalVehicles * 0.21) + ' kg';
    document.getElementById('stopsSaved').textContent = Math.round(totalStops * 0.35);
    document.getElementById('criticalRoadsCount').textContent = criticalCount;
    document.getElementById('criticalCount').textContent = criticalCount;
    document.getElementById('citySpeed').textContent = Math.round(45 - avgScore * 0.3) + ' km/h';
    document.getElementById('greenWavesActive').textContent = trafficData.green_waves?.length || 0;
    document.getElementById('greenWaveCount').textContent = trafficData.green_waves?.length || 0;
    document.getElementById('liveVehicleCount').textContent = totalVehicles;
    
    const cityBadge = document.getElementById('cityBadge');
    cityBadge.textContent = citySit;
    cityBadge.style.background = getSituationColor(citySit);
    cityBadge.style.color = '#fff';
    
    document.getElementById('overviewHour').textContent = new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    document.getElementById('sitBadge').textContent = citySit;
    document.getElementById('sitBadge').style.background = getSituationColor(citySit);
    document.getElementById('sitBadge').style.color = '#fff';
    document.getElementById('sitScore').textContent = Math.round(avgScore) + '%';
    document.getElementById('congestionFill').style.width = avgScore + '%';
    document.getElementById('congestionFill').style.background = getSituationColor(citySit);
    
    const cars = Math.round(totalVehicles * 0.45), bikes = Math.round(totalVehicles * 0.35);
    const buses = Math.round(totalVehicles * 0.10), trucks = Math.round(totalVehicles * 0.10);
    document.getElementById('carCountDisplay').textContent = cars;
    document.getElementById('bikeCountDisplay').textContent = bikes;
    document.getElementById('busCountDisplay').textContent = buses;
    document.getElementById('truckCountDisplay').textContent = trucks;
}

function updateMap() {
    Object.values(markers).forEach(m => trafficMap.removeLayer(m));
    markers = {};
    
    trafficData.junctions.forEach(j => {
        const tl = j.traffic_light || { north_south: 'red', east_west: 'red' };
        const nsColor = tl.north_south === 'green' ? '#22c55e' : tl.north_south === 'yellow' ? '#eab308' : '#ef4444';
        
        const icon = L.divIcon({
            className: 'traffic-marker',
            html: `<div style="position:relative;width:30px;height:30px;">
                <div style="position:absolute;top:0;left:0;width:12px;height:12px;border-radius:50%;background:${nsColor};box-shadow:0 0 10px ${nsColor};border:2px solid white;"></div>
                <div style="position:absolute;top:0;right:0;width:12px;height:12px;border-radius:50%;background:${tl.east_west === 'green' ? '#22c55e' : tl.east_west === 'yellow' ? '#eab308' : '#ef4444'};box-shadow:0 0 10px ${tl.east_west === 'green' ? '#22c55e' : tl.east_west === 'yellow' ? '#eab308' : '#ef4444'};border:2px solid white;"></div>
            </div>`,
            iconSize: [30, 30], iconAnchor: [15, 15]
        });
        
        const marker = L.marker([j.lat, j.lng], { icon })
            .addTo(trafficMap)
            .bindPopup(`<strong>${j.name}</strong><br>Vehicles: ${j.vehicleCount}<br>Score: ${j.score || 50}%<br>NS: ${tl.north_south?.toUpperCase()} | EW: ${tl.east_west?.toUpperCase()}`);
        
        marker.on('click', () => showJunctionDetail(j));
        markers[j.id] = marker;
    });
    
    // Update segments with green wave highlighting
    trafficData.segments.forEach(s => {
        const fromJ = trafficData.junctions.find(j => j.id === s.from);
        const toJ = trafficData.junctions.find(j => j.id === s.to);
        if (!fromJ || !toJ) return;
        
        const color = getSituationColor(s.situation || 'Normal');
        const isGreenWave = s.green_wave;
        const dashArray = isGreenWave ? '10, 5' : null;
        
        if (segmentLines[s.id]) {
            segmentLines[s.id].setStyle({ color, weight: isGreenWave ? 5 : 4, dashArray });
        } else {
            const line = L.polyline([[fromJ.lat, fromJ.lng], [toJ.lat, toJ.lng]], { color, weight: isGreenWave ? 5 : 4, opacity: 0.7, dashArray }).addTo(trafficMap);
            line.bindPopup(`<strong>${s.name}</strong><br>Score: ${s.score || 50}%${isGreenWave ? '<br>🌊 Green Wave Route' : ''}`);
            segmentLines[s.id] = line;
        }
    });
}

function updateSignalTimings() {
    const container = document.getElementById('signalTimings');
    container.innerHTML = trafficData.junctions.slice(0, 10).map(j => {
        const tl = j.traffic_light || {};
        const nsColor = tl.north_south === 'green' ? '#22c55e' : tl.north_south === 'yellow' ? '#eab308' : '#ef4444';
        const ewColor = tl.east_west === 'green' ? '#22c55e' : tl.east_west === 'yellow' ? '#eab308' : '#ef4444';
        return `
            <div class="signal-timing-item">
                <div class="traffic-light-icon">
                    <div class="light ${tl.north_south || 'off'}"></div>
                    <div class="light ${tl.east_west || 'off'}"></div>
                </div>
                <span class="junction-name">${j.name.split(' ')[0]}</span>
            </div>
        `;
    }).join('');
}

function showJunctionDetail(j) {
    selectedJunction = j;
    document.getElementById('junctionDetail').style.display = 'block';
    document.getElementById('jdName').textContent = j.name;
    document.getElementById('jdVehicles').textContent = j.vehicleCount;
    document.getElementById('jdSpeed').textContent = Math.round(45 - (j.score || 50) * 0.3) + ' km/h';
    
    const tl = j.traffic_light || {};
    document.getElementById('jdQueueNS').textContent = (tl.queue_length_north || 0) + (tl.queue_length_south || 0);
    document.getElementById('jdQueueEW').textContent = (tl.queue_length_east || 0) + (tl.queue_length_west || 0);
    
    const nsColor = tl.north_south === 'green' ? 'green' : tl.north_south === 'yellow' ? 'yellow' : 'red';
    const ewColor = tl.east_west === 'green' ? 'green' : tl.east_west === 'yellow' ? 'yellow' : 'red';
    
    document.getElementById('trafficLightDisplay').innerHTML = `
        <div class="tl-column">
            <div class="tl-label">N/S</div>
            <div class="tl-lights">
                <div class="tl-light ${tl.north_south === 'red' ? 'red' : 'off'}"></div>
                <div class="tl-light ${tl.north_south === 'yellow' ? 'yellow' : 'off'}"></div>
                <div class="tl-light ${tl.north_south === 'green' ? 'green' : 'off'}"></div>
            </div>
        </div>
        <div class="tl-column">
            <div class="tl-label">E/W</div>
            <div class="tl-lights">
                <div class="tl-light ${tl.east_west === 'red' ? 'red' : 'off'}"></div>
                <div class="tl-light ${tl.east_west === 'yellow' ? 'yellow' : 'off'}"></div>
                <div class="tl-light ${tl.east_west === 'green' ? 'green' : 'off'}"></div>
            </div>
        </div>
    `;
}

async function setSignalPhase(phase) {
    const junctionId = parseInt(document.getElementById('signalJunctionSelect').value);
    try {
        await fetch('/api/signal-control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ junction_id: junctionId, action: 'set_phase', phase })
        });
        loadAllData();
    } catch (e) { console.log('Demo mode - signal control simulated'); }
}

async function resetSignal() {
    const junctionId = parseInt(document.getElementById('signalJunctionSelect').value);
    try {
        await fetch('/api/signal-control', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ junction_id: junctionId, action: 'reset' })
        });
        loadAllData();
    } catch (e) { console.log('Demo mode - reset simulated'); }
}

// ML PREDICT
function updateSlider(type) {
    const val = document.getElementById(type + 'Slider')?.value || 0;
    const displayEl = document.getElementById(type + 'Val');
    if (displayEl) {
        if (type === 'hour') {
            const h = parseInt(val);
            displayEl.textContent = h === 0 ? '12:00 AM' : h < 12 ? `${h}:00 AM` : h === 12 ? '12:00 PM' : `${h-12}:00 PM`;
        } else {
            displayEl.textContent = val;
        }
    }
}

async function runPrediction() {
    const inputs = {
        carCount: parseInt(document.getElementById('carSlider').value),
        bikeCount: parseInt(document.getElementById('bikeSlider').value),
        busCount: parseInt(document.getElementById('busSlider').value),
        truckCount: parseInt(document.getElementById('truckSlider').value),
        hour: parseInt(document.getElementById('hourSlider').value),
        day: parseInt(document.getElementById('daySelect').value)
    };
    
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(inputs)
        });
        const result = await response.json();
        displayPrediction(result, inputs);
    } catch {
        displayPrediction({
            prediction: getSituation(50), confidence: 0.92, score: 50,
            signal_timing: { recommended_green_ns: 45, recommended_green_ew: 35, cycle_time: 90 }
        }, inputs);
    }
}

function displayPrediction(result, inputs) {
    const container = document.getElementById('predictResults');
    const color = getSituationColor(result.prediction);
    const signalPlan = result.signal_timing || { recommended_green_ns: 45, recommended_green_ew: 35, cycle_time: 90 };
    
    container.innerHTML = `
        <div class="prediction-result">
            <div class="pred-result-badge" style="background:${color}20;color:${color};border:2px solid ${color};">
                ${result.prediction}
            </div>
            <div class="result-metrics">
                <div class="rm-item"><div class="rm-label">Score</div><div class="rm-value">${result.score || 50}</div></div>
                <div class="rm-item"><div class="rm-label">Speed</div><div class="rm-value">${Math.round(45 - (result.score || 50) * 0.3)} km/h</div></div>
                <div class="rm-item"><div class="rm-label">Delay</div><div class="rm-value">${Math.round((result.score || 50) * 0.2)} min</div></div>
                <div class="rm-item"><div class="rm-label">Confidence</div><div class="rm-value">${Math.round((result.confidence || 0.9) * 100)}%</div></div>
            </div>
            <div class="signal-plan-result">
                <div class="sp-item"><div class="sp-label">NS Green</div><div class="sp-value">${signalPlan.recommended_green_ns}s</div></div>
                <div class="sp-item"><div class="sp-label">EW Green</div><div class="sp-value">${signalPlan.recommended_green_ew}s</div></div>
                <div class="sp-item"><div class="sp-label">Cycle</div><div class="sp-value">${signalPlan.cycle_time}s</div></div>
            </div>
        </div>
    `;
    
    addToHistory(result, inputs, signalPlan);
}

function addToHistory(result, inputs, signalPlan) {
    predictionHistory.unshift({
        time: new Date().toLocaleTimeString(), ...inputs,
        score: result.score || 50, prediction: result.prediction,
        signalNS: signalPlan.recommended_green_ns,
        signalEW: signalPlan.recommended_green_ew,
        confidence: Math.round((result.confidence || 0.9) * 100) + '%'
    });
    if (predictionHistory.length > 10) predictionHistory.pop();
    renderHistory();
}

function renderHistory() {
    const tbody = document.getElementById('historyBody');
    tbody.innerHTML = predictionHistory.map(h => `
        <tr>
            <td>${h.time}</td><td>${h.carCount}</td><td>${h.bikeCount}</td><td>${h.busCount}</td><td>${h.truckCount}</td>
            <td>${h.hour}:00</td>
            <td><span class="status-badge sb-${h.prediction.toLowerCase()}">${h.score}</span></td>
            <td><span class="status-badge sb-${h.prediction.toLowerCase()}">${h.prediction}</span></td>
            <td>${h.signalNS}s</td><td>${h.signalEW}s</td><td>${h.confidence}</td>
        </tr>
    `).join('');
}

// FORECAST
function initForecastChart() {
    if (forecastChart) return;
    const ctx = document.getElementById('forecastChart').getContext('2d');
    const labels = Array.from({length: 24}, (_, i) => i + ':00');
    const data = labels.map(h => REAL_HOURLY[h % 24]);
    
    forecastChart = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets: [{ label: 'Congestion Score', data, borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.1)', fill: true, tension: 0.4 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#64748b' } } }, scales: { y: { max: 100, grid: { color: '#1e3a5f' }, ticks: { color: '#64748b' } }, x: { grid: { display: false }, ticks: { color: '#64748b' } } } }
    });
    
    const currentScore = REAL_HOURLY[selectedHour];
    const situation = getSituation(currentScore);
    document.getElementById('heroScore').textContent = currentScore;
    document.getElementById('heroScore').style.color = getSituationColor(situation);
    document.getElementById('heroSituation').textContent = situation;
    document.getElementById('heroSituation').style.background = getSituationColor(situation);
    document.getElementById('heroSituation').style.color = '#fff';
    document.getElementById('heroSpeed').textContent = Math.round(45 - currentScore * 0.3) + ' km/h';
    document.getElementById('heroDelay').textContent = Math.round(currentScore * 0.2) + ' min';
    document.getElementById('heroConfidence').textContent = '92%';
    
    const nsGreen = Math.round(30 + (currentScore / 100) * 40);
    const ewGreen = Math.round(25 + (currentScore / 100) * 35);
    const cycle = Math.round(60 + (currentScore / 100) * 60);
    document.getElementById('spNS').textContent = nsGreen + 's';
    document.getElementById('spEW').textContent = ewGreen + 's';
    document.getElementById('spCycle').textContent = cycle + 's';
    
    const nextGrid = document.getElementById('nextHoursGrid');
    nextGrid.innerHTML = '';
    for (let i = 1; i <= 6; i++) {
        const h = (selectedHour + i) % 24;
        const score = REAL_HOURLY[h];
        const sit = getSituation(score);
        const advice = score < 40 ? 'Good' : score < 70 ? 'Allow extra' : 'Avoid';
        nextGrid.innerHTML += `<div class="nh-card"><div class="nh-hour">+${i}h (${h}:00)</div><div class="nh-score" style="color:${getSituationColor(sit)}">${score}%</div><div class="nh-status">${sit}</div><div class="nh-advice" style="background:${advice === 'Good' ? '#22c55e20' : advice === 'Avoid' ? '#ef444420' : '#eab30820'};color:${advice === 'Good' ? '#22c55e' : advice === 'Avoid' ? '#ef4444' : '#eab308'}">${advice}</div></div>`;
    }
    
    const sortedHours = Object.entries(REAL_HOURLY).sort((a, b) => a[1] - b[1]);
    document.getElementById('bestWindows').innerHTML = sortedHours.slice(0, 3).map(([h, s]) => `<div class="window-item"><span class="wi-time">${h}:00</span><span class="wi-score" style="color:#22c55e">${s}%</span></div>`).join('');
    document.getElementById('worstWindows').innerHTML = sortedHours.reverse().slice(0, 3).map(([h, s]) => `<div class="window-item"><span class="wi-time">${h}:00</span><span class="wi-score" style="color:#ef4444">${s}%</span></div>`).join('');
}

// ANALYSIS
function initAnalysisCharts() {
    if (trafficPatternChart) return;
    
    const hours = Array.from({length: 24}, (_, i) => i + ':00');
    const vehicles = hours.map(() => REAL_HOURLY[parseInt(hours[hours.indexOf(_)]) % 24] * 1.2);
    
    trafficPatternChart = new Chart(document.getElementById('trafficPatternChart').getContext('2d'), {
        type: 'line',
        data: { labels: hours, datasets: [{ label: 'Vehicles', data: hours.map(h => REAL_HOURLY[parseInt(h)] * 1.2), borderColor: '#3b82f6', backgroundColor: 'rgba(59, 130, 246, 0.2)', fill: true, tension: 0.4 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { color: '#1e3a5f' }, ticks: { color: '#64748b' } }, x: { grid: { display: false }, ticks: { color: '#64748b' } } } }
    });
    
    situationDistChart = new Chart(document.getElementById('situationDistChart').getContext('2d'), {
        type: 'doughnut',
        data: { labels: ['Low', 'Normal', 'Heavy', 'High'], datasets: [{ data: [1138, 5279, 1819, 692], backgroundColor: ['#22c55e', '#eab308', '#f97316', '#ef4444'] }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#64748b' } } } }
    });
    
    signalTimingChart = new Chart(document.getElementById('signalTimingChart').getContext('2d'), {
        type: 'bar',
        data: {
            labels: hours,
            datasets: [
                { label: 'NS Green', data: hours.map(h => Math.round(30 + (REAL_HOURLY[parseInt(h)] / 100) * 40)), backgroundColor: '#22c55e' },
                { label: 'EW Green', data: hours.map(h => Math.round(25 + (REAL_HOURLY[parseInt(h)] / 100) * 35)), backgroundColor: '#3b82f6' }
            ]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#64748b' } } }, scales: { y: { max: 70, grid: { color: '#1e3a5f' }, ticks: { color: '#64748b' } }, x: { grid: { display: false }, ticks: { color: '#64748b' } } } }
    });
    
    const cars = hours.map(h => 30 + REAL_HOURLY[parseInt(h)] * 0.4);
    const bikes = hours.map(h => 20 + REAL_HOURLY[parseInt(h)] * 0.3);
    vehicleTypesChart = new Chart(document.getElementById('vehicleTypesChart').getContext('2d'), {
        type: 'line',
        data: { labels: hours, datasets: [
            { label: 'Cars', data: cars, borderColor: '#3b82f6', tension: 0.4 },
            { label: 'Bikes', data: bikes, borderColor: '#22c55e', tension: 0.4 }
        ] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#64748b' } } }, scales: { y: { grid: { color: '#1e3a5f' }, ticks: { color: '#64748b' } }, x: { grid: { display: false }, ticks: { color: '#64748b' } } } }
    });
}

// SEGMENTS
function initSegmentsChart() {
    if (topRoadsChart) return;
    const sorted = [...trafficData.segments].sort((a, b) => (b.score || 50) - (a.score || 50)).slice(0, 8);
    topRoadsChart = new Chart(document.getElementById('topRoadsChart').getContext('2d'), {
        type: 'bar',
        data: { labels: sorted.map(s => s.name.substring(0, 15)), datasets: [{ label: 'Congestion %', data: sorted.map(s => s.score || 50), backgroundColor: sorted.map(s => getSituationColor(getSituation(s.score || 50))) }] },
        options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y', plugins: { legend: { display: false } }, scales: { x: { max: 100, grid: { color: '#1e3a5f' }, ticks: { color: '#64748b' } }, y: { grid: { display: false }, ticks: { color: '#64748b' } } } }
    });
}

function updateSegmentsTable() {
    const sorted = [...trafficData.segments].sort((a, b) => (b.score || 50) - (a.score || 50));
    document.getElementById('segmentsTableBody').innerHTML = sorted.map(s => {
        const fromJ = JUNCTIONS.find(j => j.id === s.from);
        const toJ = JUNCTIONS.find(j => j.id === s.to);
        const sit = getSituation(s.score || 50);
        return `<tr>
            <td>${s.id}</td><td>${s.name}</td><td>${fromJ?.name.substring(0, 10)}...</td><td>${toJ?.name.substring(0, 10)}...</td>
            <td>${s.score || 50}%</td><td>${Math.round(45 - (s.score || 50) * 0.3)} km/h</td><td>${s.flow_rate || '--'}</td>
            <td>${s.green_wave ? '<span class="green-wave-badge">🌊 Active</span>' : '-'}</td>
            <td><span class="status-badge sb-${sit.toLowerCase()}">${sit}</span></td>
        </tr>`;
    }).join('');
}

// SENSORS
function initSensorChart() {
    if (sensorStreamChart) return;
    sensorDataPoints = Array.from({length: 30}, () => ({ total: 50 + Math.random() * 30, cars: 30 + Math.random() * 15 }));
    sensorStreamChart = new Chart(document.getElementById('sensorStreamChart').getContext('2d'), {
        type: 'line',
        data: { labels: Array.from({length: 30}, (_, i) => i), datasets: [
            { label: 'Total', data: sensorDataPoints.map(d => d.total), borderColor: '#3b82f6', tension: 0.4 },
            { label: 'Cars', data: sensorDataPoints.map(d => d.cars), borderColor: '#22c55e', tension: 0.4 }
        ] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#64748b' } } }, scales: { y: { grid: { color: '#1e3a5f' }, ticks: { color: '#64748b' } }, x: { grid: { display: false }, ticks: { color: '#64748b' } } } }
    });
    
    const grid = document.getElementById('sensorCardsGrid');
    const sensors = [
        { icon: '🚗', label: 'Loop Detector', value: '45', unit: 'veh/min' },
        { icon: '📸', label: 'Speed Radar', value: '32', unit: 'km/h' },
        { icon: '🤖', label: 'Camera AI', value: 'Active', unit: 'tracking' },
        { icon: '🌤️', label: 'Weather', value: 'Clear', unit: 'conditions' },
        { icon: '⚠️', label: 'Incident', value: 'Normal', unit: 'flow' }
    ];
    grid.innerHTML = sensors.map(s => `
        <div class="sensor-card-item">
            <div class="sc-icon">${s.icon}</div>
            <h4>${s.label}</h4>
            <div class="sc-value">${s.value}</div>
            <div class="sc-unit">${s.unit}</div>
        </div>
    `).join('');
}

// ALERTS
function updateAlerts() {
    const alerts = [];
    trafficData.segments.forEach(s => {
        if ((s.score || 50) > 80) alerts.push({ severity: 'critical', location: s.name, message: `Critical: ${s.score || 50}%` });
        else if ((s.score || 50) > 65) alerts.push({ severity: 'high', location: s.name, message: `Heavy: ${s.score || 50}%` });
        else if ((s.score || 50) > 50) alerts.push({ severity: 'medium', location: s.name, message: `Moderate: ${s.score || 50}%` });
    });
    
    document.getElementById('totalAlerts').textContent = alerts.length;
    document.getElementById('criticalAlerts').textContent = alerts.filter(a => a.severity === 'critical').length;
    document.getElementById('highAlerts').textContent = alerts.filter(a => a.severity === 'high').length;
    document.getElementById('mediumAlerts').textContent = alerts.filter(a => a.severity === 'medium').length;
    
    document.getElementById('alertsFeed').innerHTML = alerts.map(a => `
        <div class="alert-card ${a.severity}">
            <div class="alert-severity">${a.severity === 'critical' ? '<span class="blink-dot"></span>CRITICAL' : a.severity.toUpperCase()}</div>
            <div class="alert-content">
                <div class="alert-location">${a.location}</div>
                <div class="alert-message">${a.message}</div>
            </div>
            <div class="alert-time">${new Date().toLocaleTimeString()}</div>
        </div>
    `).join('') || '<p style="text-align:center;color:var(--text-muted);padding:40px;">No alerts</p>';
}

// SIGNAL OPTIMIZER
function updateSignalOptimizer() {
    const sorted = [...trafficData.segments].sort((a, b) => (b.score || 50) - (a.score || 50)).slice(0, 8);
    document.getElementById('signalCards').innerHTML = sorted.map(s => {
        const sit = getSituation(s.score || 50);
        const greenNS = Math.round(60 - (s.score || 50) * 0.4);
        const greenEW = 90 - greenNS - 5;
        const greenPct = (greenNS / 90) * 100;
        const amberPct = (5 / 90) * 100;
        const redPct = 100 - greenPct - amberPct;
        return `
            <div class="signal-card">
                <div class="sc-header"><h4>${s.name}</h4><div class="sc-junctions">Signal Optimization</div></div>
                <div class="sc-congestion">
                    <span class="sc-score" style="color:${getSituationColor(sit)}">${s.score || 50}%</span>
                    <span class="status-badge sb-${sit.toLowerCase()}">${sit}</span>
                </div>
                <div class="sc-metrics">
                    <div class="sc-metric"><div class="scm-label">NS Green</div><div class="scm-value">${greenNS}s</div></div>
                    <div class="sc-metric"><div class="scm-label">EW Green</div><div class="scm-value">${greenEW}s</div></div>
                    <div class="sc-metric"><div class="scm-label">Efficiency</div><div class="scm-value">${Math.round(100 - (s.score || 50) * 0.5)}%</div></div>
                </div>
                <div class="signal-bar">
                    <div class="sb-green" style="width:${greenPct}%"></div>
                    <div class="sb-amber" style="width:${amberPct}%"></div>
                    <div class="sb-red" style="width:${redPct}%"></div>
                </div>
            </div>
        `;
    }).join('');
}

// GREEN WAVE
function updateGreenWaveRoutes() {
    const container = document.getElementById('greenwaveRoutes');
    if (!trafficData.green_waves) return;
    
    container.innerHTML = trafficData.green_waves.map(gw => `
        <div class="wave-route-card">
            <h4>🌊 ${gw.route_name}</h4>
            <div class="wr-stat"><span>Sync Score</span><strong>${gw.synchronization_score}%</strong></div>
            <div class="wr-stat"><span>Travel Time</span><strong>${gw.total_travel_time} min</strong></div>
            <div class="wr-stat"><span>Optimal Speed</span><strong>${gw.optimal_speed} km/h</strong></div>
            <div class="wr-stat"><span>Segments</span><strong>${gw.segments.length}</strong></div>
        </div>
    `).join('');
}

function updateGreenWave() {
    const speed = document.getElementById('waveSpeedSlider').value;
    document.getElementById('waveSpeedValue').textContent = speed + ' km/h';
}

async function optimizeGreenWave() {
    const speed = parseInt(document.getElementById('waveSpeedSlider').value);
    try {
        const response = await fetch('/api/green-wave/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ speed_limit: speed })
        });
        const result = await response.json();
        document.getElementById('travelTimeReduction').textContent = result.estimated_benefits.travel_time_reduction;
        document.getElementById('stopsReduction').textContent = result.estimated_benefits.stops_reduction;
        document.getElementById('fuelSavings').textContent = result.estimated_benefits.fuel_savings;
        document.getElementById('emissionReduction').textContent = result.estimated_benefits.emission_reduction;
    } catch {
        document.getElementById('travelTimeReduction').textContent = Math.round(15 + Math.random() * 10) + '%';
        document.getElementById('stopsReduction').textContent = Math.round(25 + Math.random() * 15) + '%';
        document.getElementById('fuelSavings').textContent = Math.round(10 + Math.random() * 8) + '%';
        document.getElementById('emissionReduction').textContent = Math.round(12 + Math.random() * 10) + '%';
    }
}

function initGreenWaveMap() {
    if (waveMap) return;
    waveMap = L.map('waveMap').setView([17.3850, 78.4867], 12);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { attribution: '© CARTO', maxZoom: 19 }).addTo(waveMap);
    
    // Draw green wave corridors
    GREEN_WAVE_ROUTES.forEach(route => {
        const coords = [];
        route.segments.forEach(segId => {
            const seg = SEGMENTS.find(s => s.id === segId);
            if (seg) {
                const from = JUNCTIONS.find(j => j.id === seg.from);
                const to = JUNCTIONS.find(j => j.id === seg.to);
                if (from) coords.push([from.lat, from.lng]);
                if (to) coords.push([to.lat, to.lng]);
            }
        });
        if (coords.length > 1) {
            L.polyline(coords, { color: route.color, weight: 6, opacity: 0.8 }).addTo(waveMap);
        }
    });
}

// ROUTE
function findRoute() {
    const origin = parseInt(document.getElementById('originSelect').value);
    const dest = parseInt(document.getElementById('destSelect').value);
    if (origin === dest) return;
    
    const route = dijkstra(origin, dest);
    currentRoutes = [
        { name: 'Fastest', ...route },
        { name: 'Alternate', time: route.time * 1.2, distance: route.distance * 1.1, path: [...route.path] },
        { name: 'Shortest', time: route.time * 1.1, distance: route.distance * 0.9, path: route.path }
    ];
    
    displayRoutes();
    drawRoutes();
}

function dijkstra(start, end) {
    const path = [start];
    let current = start;
    const visited = new Set([start]);
    
    while (current !== end && path.length < 10) {
        const connected = SEGMENTS.filter(s => (s.from === current || s.to === current) && !visited.has(s.from === current ? s.to : s.from));
        if (connected.length === 0) break;
        const next = connected[Math.floor(Math.random() * connected.length)];
        const nextJ = next.from === current ? next.to : next.from;
        path.push(nextJ);
        visited.add(nextJ);
        current = nextJ;
    }
    
    const segments = path.slice(0, -1).map((p, i) => SEGMENTS.find(s => (s.from === p && s.to === path[i + 1]) || (s.to === p && s.from === path[i + 1])) || { score: 50 });
    const avgScore = segments.reduce((s, seg) => s + (seg.score || 50), 0) / Math.max(segments.length, 1);
    
    return { path, time: Math.round(5 + avgScore * 0.3), distance: path.length * 0.8, score: Math.round(avgScore), stops: Math.round(path.length * 0.5) };
}

function displayRoutes() {
    document.getElementById('routeBreakdown').style.display = 'block';
    const route = currentRoutes[selectedRouteIndex];
    document.getElementById('routeDistance').textContent = route.distance.toFixed(1) + ' km';
    document.getElementById('routeTime').textContent = route.time + ' min';
    document.getElementById('routeScore').textContent = route.score + '%';
    document.getElementById('routeStops').textContent = route.stops;
    
    document.getElementById('routeNodes').innerHTML = route.path.map((j, i) => {
        const junction = JUNCTIONS.find(jt => jt.id === j);
        return `<span class="path-chip" style="border-left:2px solid ${i === 0 ? '#22c55e' : i === route.path.length - 1 ? '#f97316' : '#3b82f6'}">${junction?.name.split(' ')[0]}</span>`;
    }).join('');
    
    document.getElementById('routeResults').innerHTML = currentRoutes.map((r, i) => `
        <div class="route-result-card" style="border-left-color:${i === 0 ? '#3b82f6' : i === 1 ? '#22c55e' : '#eab308'}">
            <div class="rr-name">${r.name} Route</div>
            <div class="rr-stats"><span>Time: <strong>${r.time} min</strong></span><span>Stops: <strong>${r.stops}</strong></span></div>
        </div>
    `).join('');
}

function selectRoute(index) {
    selectedRouteIndex = index;
    document.querySelectorAll('.route-tab').forEach((t, i) => t.classList.toggle('active', i === index));
    displayRoutes();
    drawRoutes();
}

function drawRoutes() {
    routePolylines.forEach(l => trafficMap.removeLayer(l));
    routePolylines = [];
    
    const route = currentRoutes[selectedRouteIndex];
    const colors = ['#3b82f6', '#22c55e', '#eab308'];
    const routeCoords = route.path.map(j => { const junction = JUNCTIONS.find(jt => jt.id === j); return [junction.lat, junction.lng]; });
    
    const polyline = L.polyline(routeCoords, { color: colors[selectedRouteIndex], weight: 6, opacity: 0.9 }).addTo(trafficMap);
    routePolylines.push(polyline);
}

// MODEL
function initModelCharts() {
    if (classDistChart) return;
    
    classDistChart = new Chart(document.getElementById('classDistChart').getContext('2d'), {
        type: 'bar',
        data: { labels: ['Low', 'Normal', 'Heavy', 'High'], datasets: [{ label: 'Records', data: [1138, 5279, 1819, 692], backgroundColor: ['#22c55e', '#eab308', '#f97316', '#ef4444'] }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { color: '#1e3a5f' }, ticks: { color: '#64748b' } }, x: { grid: { display: false }, ticks: { color: '#64748b' } } } }
    });
    
    const featImp = [
        { name: 'Total', value: 32.4 }, { name: 'CarCount', value: 28.1 }, { name: 'TruckCount', value: 15.3 },
        { name: 'BusCount', value: 8.7 }, { name: 'Hour', value: 5.2 }, { name: 'RushHour', value: 3.8 },
        { name: 'BikeCount', value: 2.4 }, { name: 'DayNum', value: 1.8 }, { name: 'Weekend', value: 1.2 }
    ];
    
    featureImportanceChart = new Chart(document.getElementById('featureImportanceChart').getContext('2d'), {
        type: 'bar',
        data: { labels: featImp.map(f => f.name), datasets: [{ label: 'Importance %', data: featImp.map(f => f.value), backgroundColor: '#3b82f6' }] },
        options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y', plugins: { legend: { display: false } }, scales: { x: { max: 35, grid: { color: '#1e3a5f' }, ticks: { color: '#64748b' } }, y: { grid: { display: false }, ticks: { color: '#64748b' } } } }
    });
}

document.addEventListener('DOMContentLoaded', initApp);
