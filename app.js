// API 베이스 URL
const API_BASE = window.API_BASE_URL || (
    window.location.hostname === 'localhost' 
        ? 'http://localhost:8000' 
        : window.location.origin
);

// 전역 상태
let allRegions = [];
let currentRegion = null;
let networkData = null;
let allSido = [];
let expandedSidos = new Set();
let expandedSigungus = new Set();
let availableYears = [];
let selectedYear = "2023"; // 항상 최신 연도 사용

// ============================================
// 초기화
// ============================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 InsightForge 시작...');
    console.log('📍 API_BASE:', API_BASE);
    
    try {
        // 사용 가능한 연도 로드 (최신 연도 자동 선택)
        const yearsResponse = await fetch(`${API_BASE}/api/years`);
        const yearsData = await yearsResponse.json();
        availableYears = yearsData.years || [];
        selectedYear = availableYears[availableYears.length - 1] || "2023";
        console.log(`✅ 최신 연도: ${selectedYear}`);
        
        await loadNationalData();
    } catch (error) {
        console.error('❌ 초기화 실패:', error);
        document.getElementById('regionList').innerHTML = `
            <div class="text-center py-8 text-red-500">
                <p class="font-bold">로드 실패</p>
                <p class="text-sm mt-2">${error.message}</p>
                <button onclick="location.reload()" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    새로고침
                </button>
            </div>
        `;
    }
});

// 연도 로드 함수 제거 (자동으로 최신 연도 사용)

// ============================================
// 전국 데이터 로드
// ============================================

async function loadNationalData() {
    try {
        console.log('📡 전국 데이터 요청 중...');
        const response = await fetch(`${API_BASE}/api/national/sido`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('📦 받은 데이터:', data);
        
        // API가 직접 배열을 반환함
        allSido = Array.isArray(data) ? data : (data.sido_list || []);
        
        console.log('📦 시도 목록 길이:', allSido.length);
        
        if (allSido.length === 0) {
            throw new Error('시도 목록이 비어있습니다');
        }
        
        renderNationalList();
        console.log(`✅ ${allSido.length}개 시도 로드 완료`);
    } catch (error) {
        console.error('❌ 전국 데이터 로드 실패:', error);
        document.getElementById('regionList').innerHTML = `
            <div class="text-center py-8 text-red-500">
                <p class="font-bold">데이터를 불러올 수 없습니다</p>
                <p class="text-sm mt-2">${error.message}</p>
                <button onclick="loadNationalData()" class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                    다시 시도
                </button>
            </div>
        `;
        throw error;
    }
}

async function loadRegions() {
    try {
        const response = await fetch(`${API_BASE}/api/regions`);
        const data = await response.json();
        
        allRegions = data.regions || [];
        
        renderRegionList(allRegions);
        console.log(`✅ ${allRegions.length}개 읍면동 로드 (${data.gu_count}개 구)`);
    } catch (error) {
        console.error('❌ 지역 데이터 로드 실패:', error);
    }
}

// ============================================
// 전국 시도 목록 렌더링
// ============================================

function renderNationalList() {
    const regionList = document.getElementById('regionList');
    
    if (!regionList) {
        console.error('❌ regionList 요소를 찾을 수 없습니다');
        return;
    }
    
    console.log(`🎨 ${allSido.length}개 시도 렌더링 중...`);
    
    let html = '<div class="space-y-2">';
    
    allSido.forEach(sido => {
        const sidoCode = sido.sido_cd || sido.code;
        const sidoName = sido.sido_nm || sido.name;
        const isExpanded = expandedSidos.has(sidoCode);
        const popText = sido.total_population ? `${sido.total_population.toLocaleString()}명` : '-';
        
        html += `
            <div>
                <div class="font-semibold text-gray-900 px-3 py-2 bg-blue-50 rounded cursor-pointer hover:bg-blue-100 border border-blue-200 flex items-center justify-between"
                     onclick='toggleSido("${sidoCode}")'>
                    <div class="flex items-center gap-2">
                        <svg class="w-3 h-3 transform transition-transform ${isExpanded ? 'rotate-90' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                        <span class="text-sm font-bold">${sidoName}</span>
                    </div>
                    <div class="flex items-center gap-3 text-xs">
                        <span class="text-gray-600">${sido.sigungu_count}개 시군구</span>
                        <span class="text-blue-600 font-semibold">${popText}</span>
                    </div>
                </div>
                ${isExpanded ? `<div id="sido-${sidoCode}" class="ml-4 mt-1"></div>` : ''}
            </div>
        `;
    });
    
    html += '</div>';
    regionList.innerHTML = html;
    console.log('✅ 렌더링 완료');
}

async function toggleSido(sidoCode) {
    if (expandedSidos.has(sidoCode)) {
        expandedSidos.delete(sidoCode);
        renderNationalList();
    } else {
        expandedSidos.add(sidoCode);
        renderNationalList();
        await loadSigunguList(sidoCode);
    }
}
window.toggleSido = toggleSido;

async function loadSigunguList(sidoCode) {
    try {
        const response = await fetch(`${API_BASE}/api/national/sido/${sidoCode}`);
        const data = await response.json();
        
        const container = document.getElementById(`sido-${sidoCode}`);
        if (!container) return;
        
        let html = '<div class="space-y-1">';
        
        const sigunguList = data.sigungu_list || [];
        
        sigunguList.forEach(sigungu => {
            const sigunguCode = sigungu.sigungu_code;
            const sigunguName = sigungu.sigungu_name;
            const emdongCount = sigungu.emdong_list ? sigungu.emdong_list.length : 0;
            const isExpanded = expandedSigungus.has(sigunguCode);
            const popText = sigungu.total_population ? `${sigungu.total_population.toLocaleString()}명` : '-';
            
            html += `
                <div class="ml-2">
                    <div class="px-2 py-1.5 bg-white rounded border border-gray-200 flex items-center justify-between text-sm">
                        <div class="flex items-center gap-2">
                            <svg class="w-2.5 h-2.5 transform transition-transform ${isExpanded ? 'rotate-90' : ''} cursor-pointer hover:text-blue-600" 
                                 fill="none" stroke="currentColor" viewBox="0 0 24 24"
                                 onclick='toggleSigungu("${sigunguCode}")'>
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                            </svg>
                            <span class="cursor-pointer hover:text-blue-600" onclick='selectSigungu("${sigunguCode}")'>${sigunguName}</span>
                        </div>
                        <div class="flex items-center gap-2 text-xs">
                            <span class="text-gray-500">${emdongCount}개</span>
                            <span class="text-green-600">${popText}</span>
                        </div>
                    </div>
                    ${isExpanded ? `<div id="sigungu-${sigunguCode}" class="ml-3 mt-1"></div>` : ''}
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
        
    } catch (error) {
        console.error('❌ 시군구 로드 실패:', error);
    }
}

async function toggleSigungu(sigunguCode) {
    if (expandedSigungus.has(sigunguCode)) {
        expandedSigungus.delete(sigunguCode);
        // 부모 시도 다시 로드
        const sido = allSido.find(s => expandedSidos.has(s.sido_cd || s.code));
        if (sido) await loadSigunguList(sido.sido_cd || sido.code);
    } else {
        expandedSigungus.add(sigunguCode);
        
        // 시군구 상세 정보도 로드
        try {
            const response = await fetch(`${API_BASE}/api/national/sigungu/${sigunguCode}/detail`);
            const data = await response.json();
            console.log('📦 시군구 상세 데이터 (toggle):', data);
            renderSigunguDetail(data);
            
            // 시계열 그래프도 로드 (정치인 정보는 나중에)
            loadSigunguTimeseries(sigunguCode, []);
        } catch (error) {
            console.error('❌ 시군구 상세 정보 로드 실패:', error);
        }
        
        // 부모 시도 다시 로드
        const sido = allSido.find(s => expandedSidos.has(s.sido_cd || s.code));
        if (sido) await loadSigunguList(sido.sido_cd || sido.code);
        await loadEmdongList(sigunguCode);
    }
}
window.toggleSigungu = toggleSigungu;

async function selectSigungu(sigunguCode) {
    console.log('🔍 시군구 선택:', sigunguCode);
    
    // 시군구 상세 정보 로드
    try {
        const response = await fetch(`${API_BASE}/api/national/sigungu/${sigunguCode}/detail`);
        const data = await response.json();
        
        console.log('📦 시군구 상세 데이터:', data);
        renderSigunguDetail(data);
        
        // 시계열 그래프 먼저 렌더링 (정치인 정보는 나중에)
        loadSigunguTimeseries(sigunguCode, []);
        
    } catch (error) {
        console.error('❌ 시군구 상세 정보 로드 실패:', error);
    }
    
    // 읍면동 목록도 확장
    if (!expandedSigungus.has(sigunguCode)) {
        await toggleSigungu(sigunguCode);
    }
}
// 전역 등록
window.selectSigungu = selectSigungu;

async function loadEmdongList(sigunguCode) {
    try {
        const response = await fetch(`${API_BASE}/api/national/sigungu/${sigunguCode}`);
        const data = await response.json();
        
        console.log('📦 시군구 데이터:', data);
        
        const container = document.getElementById(`sigungu-${sigunguCode}`);
        if (!container) {
            console.error('❌ 컨테이너를 찾을 수 없습니다:', `sigungu-${sigunguCode}`);
            return;
        }
        
        let html = '<div class="space-y-0.5">';
        
        const emdongList = data.emdong_list || [];
        console.log(`📋 읍면동 목록 개수: ${emdongList.length}`);
        
        emdongList.forEach(emdong => {
            const emdongCode = emdong.emdong_code;
            const emdongName = emdong.emdong_name;
            
            html += `
                <div class="px-2 py-1 hover:bg-purple-50 rounded cursor-pointer border border-gray-100 text-xs transition-colors"
                     onclick='selectEmdong("${emdongCode}")'>
                    <div class="flex justify-between items-center">
                        <span class="text-gray-700">${emdongName}</span>
                        <span class="text-gray-500 text-xs">${emdongCode}</span>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        container.innerHTML = html;
        
    } catch (error) {
        console.error('❌ 읍면동 로드 실패:', error);
    }
}

async function selectEmdong(emdongCode) {
    try {
        console.log(`🔍 읍면동 선택: ${emdongCode}`);
        
        // Enhanced API에서 모든 데이터 가져오기
        const response = await fetch(`${API_BASE}/api/emdong/${emdongCode}/enhanced?year=${selectedYear}`);
        
        if (!response.ok) {
            throw new Error(`API 오류: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('📦 읍면동 데이터:', data);
        
        currentRegion = data;
        
        // 정치인 정보 가져오기 (있다면)
        try {
            const politiciansResponse = await fetch(`${API_BASE}/api/politicians/emdong/${emdongCode}`);
            const politiciansData = await politiciansResponse.json();
            data.politicians = politiciansData || [];
        } catch (e) {
            console.log('정치인 정보 없음');
            data.politicians = [];
        }
        
        renderEmdongDetail(data);
        
        // 시계열 그래프 렌더링 (정치인 데이터 전달)
        loadEmdongTimeseries(emdongCode, data.politicians);
        
        // 시계열 데이터도 가져오기 (있는 경우)
        loadTimeseriesData(emdongCode);
        
    } catch (error) {
        console.error('❌ 읍면동 상세 정보 로드 실패:', error);
    }
}
window.selectEmdong = selectEmdong;

async function loadTimeseriesData(emdongCode) {
    try {
        // 연령별 상세 데이터 (정확한 인구 수치 포함)
        const enhancedResponse = await fetch(`${API_BASE}/api/emdong/${emdongCode}/enhanced`);
        const enhancedData = await enhancedResponse.json();
        
        if (enhancedData.timeseries) {
            // 연령별 상세 데이터로 시계열 차트 렌더링
            renderTimeseriesChart(enhancedData);
            renderEnhancedStats(enhancedData);
        }
    } catch (error) {
        console.log('시계열 데이터 없음 (정상)');
    }
}

function renderTimeseriesChart(data) {
    const chartDiv = document.getElementById('timeseriesChart');
    if (!chartDiv) return;
    
    const timeseries = data.timeseries || {};
    const years = data.years || [];
    
    if (years.length < 2) {
        chartDiv.innerHTML = '';
        return;
    }
    
    // 전역 저장 (상세 그래프용)
    window.currentTimeseriesData = data;
    
    // 미니 차트 렌더링
    renderMiniCharts(timeseries, years);
    
    // 데이터 추출 (연령별 상세 데이터 우선 사용)
    const populations = [];
    const households = [];
    const companies = [];
    
    years.forEach(year => {
        const yearData = timeseries[year] || {};
        // 연령별 상세 데이터가 있으면 우선 사용 (정확한 인구)
        if (yearData.basic && yearData.basic.total_population > 0) {
            const population = yearData.basic.total_population;
            populations.push(population);
            // 가구수 = 인구 / 평균가구원수
            const avgSize = yearData.household?.avg_family_member_cnt || 2.0;
            households.push(Math.round(population / avgSize));
        } else {
            populations.push(yearData.household?.family_member_cnt || 0);
            households.push(yearData.household?.household_cnt || 0);
        }
        companies.push(yearData.company?.corp_cnt || 0);
    });
    
    chartDiv.innerHTML = `
        <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
            <div class="flex items-center justify-between mb-4">
                <h3 class="font-bold text-lg flex items-center">
                    <svg class="w-5 h-5 mr-2 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                    </svg>
                    시계열 변화 (${years[0]} ~ ${years[years.length-1]})
                </h3>
                <button onclick="showDetailedChart()" class="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors flex items-center text-sm">
                    <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path>
                    </svg>
                    항목별 추이
                </button>
            </div>
            <div class="grid grid-cols-3 gap-6">
                <div>
                    <div class="text-sm text-gray-600 mb-3">인구 추이</div>
                    ${renderSparkline(populations, years, 'blue')}
                    <div class="text-xs text-gray-500 mt-2 flex justify-between">
                        <span>${years[0]}: ${populations[0].toLocaleString()}</span>
                        <span>${years[years.length-1]}: ${populations[populations.length-1].toLocaleString()}</span>
                    </div>
                </div>
                <div>
                    <div class="text-sm text-gray-600 mb-3">가구수 추이</div>
                    ${renderSparkline(households, years, 'green')}
                    <div class="text-xs text-gray-500 mt-2 flex justify-between">
                        <span>${years[0]}: ${households[0].toLocaleString()}</span>
                        <span>${years[years.length-1]}: ${households[households.length-1].toLocaleString()}</span>
                    </div>
                </div>
                <div>
                    <div class="text-sm text-gray-600 mb-3">사업체 추이</div>
                    ${renderSparkline(companies, years, 'orange')}
                    <div class="text-xs text-gray-500 mt-2 flex justify-between">
                        <span>${years[0]}: ${companies[0].toLocaleString()}</span>
                        <span>${years[years.length-1]}: ${companies[companies.length-1].toLocaleString()}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderSparkline(values, years, color) {
    if (!values || values.length === 0) return '<div class="text-gray-400 text-xs">데이터 없음</div>';
    
    const max = Math.max(...values);
    const min = Math.min(...values);
    const range = max - min || 1;
    
    const points = values.map((v, i) => {
        const x = (i / (values.length - 1)) * 100;
        const y = 100 - ((v - min) / range * 100);
        return `${x},${y}`;
    }).join(' ');
    
    const colorMap = {
        'blue': '#3b82f6',
        'green': '#10b981',
        'orange': '#f97316'
    };
    
    return `
        <svg viewBox="0 0 100 30" class="w-full h-16 bg-gray-50 rounded">
            <polyline points="${points}" 
                fill="none" 
                stroke="${colorMap[color]}" 
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"/>
        </svg>
    `;
}

// ============================================
// 미니 차트 렌더링 (통계 카드용)
// ============================================

function renderMiniCharts(timeseries, years) {
    // 데이터 추출 (연령별 상세 데이터 우선)
    const populations = [];
    const households = [];
    const houses = [];
    const companies = [];
    
    years.forEach(year => {
        const yearData = timeseries[year] || {};
        // 연령별 상세 데이터가 있으면 우선 사용
        if (yearData.basic && yearData.basic.total_population > 0) {
            const population = yearData.basic.total_population;
            populations.push(population);
            // 가구수 = 인구 / 평균가구원수
            const avgSize = yearData.household?.avg_family_member_cnt || 2.0;
            households.push(Math.round(population / avgSize));
        } else {
            populations.push(yearData.household?.family_member_cnt || 0);
            households.push(yearData.household?.household_cnt || 0);
        }
        houses.push(yearData.house?.house_cnt || 0);
        companies.push(yearData.company?.corp_cnt || 0);
    });
    
    // DOM이 완전히 렌더링된 후 미니 차트 그리기
    setTimeout(() => {
        renderMiniChart('miniChart-population', populations, '#ffffff');
        renderMiniChart('miniChart-household', households, '#ffffff');
        renderMiniChart('miniChart-house', houses, '#ffffff');
        renderMiniChart('miniChart-company', companies, '#ffffff');
    }, 100);
}

function renderMiniChart(elementId, values, color) {
    const element = document.getElementById(elementId);
    if (!element || !values || values.length < 2) return;
    
    const max = Math.max(...values);
    const min = Math.min(...values);
    const range = max - min || 1;
    
    // 점 좌표 생성
    const points = values.map((v, i) => {
        const x = (i / (values.length - 1)) * 100;
        const y = 30 - ((v - min) / range * 25); // 5px 여백
        return `${x},${y}`;
    }).join(' ');
    
    // 변화율 계산
    const firstValue = values[0];
    const lastValue = values[values.length - 1];
    const changePercent = firstValue ? ((lastValue - firstValue) / firstValue * 100) : 0;
    const isPositive = changePercent >= 0;
    const arrow = isPositive ? '↗' : '↘';
    
    element.innerHTML = `
        <svg viewBox="0 0 100 30" class="w-full h-full">
            <polyline points="${points}" 
                fill="none" 
                stroke="${color}" 
                stroke-width="1.5"
                opacity="0.8"
                stroke-linecap="round"
                stroke-linejoin="round"/>
        </svg>
        <div class="text-xs opacity-90 mt-0.5 flex items-center justify-between">
            <span>${values[0].toLocaleString()}</span>
            <span class="font-semibold">${arrow} ${Math.abs(changePercent).toFixed(1)}%</span>
            <span>${values[values.length - 1].toLocaleString()}</span>
        </div>
    `;
}

// ============================================
// 연령별 상세 통계 렌더링
// ============================================

function renderEnhancedStats(data) {
    const latest = data.latest || {};
    const basic = latest.basic || {};
    const ageGroups = latest.age_groups || {};
    
    // 연령 통계 섹션을 정치인 섹션 뒤에 추가
    const detailView = document.getElementById('detailView');
    if (!detailView) return;
    
    // 기존 연령 통계 섹션 제거
    const existingAgeSection = document.getElementById('ageStatsSection');
    if (existingAgeSection) {
        existingAgeSection.remove();
    }
    
    // 새 섹션 생성
    const ageSection = document.createElement('div');
    ageSection.id = 'ageStatsSection';
    ageSection.className = 'max-w-5xl mb-6';
    
    ageSection.innerHTML = `
        <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
            <h3 class="font-bold text-lg mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
                연령 통계 (${selectedYear}년)
            </h3>
            
            <!-- 주요 지표 -->
            <div class="grid grid-cols-4 gap-4 mb-6">
                <div class="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
                    <div class="text-xs text-blue-600 mb-1">평균 연령</div>
                    <div class="text-2xl font-bold text-blue-900">${basic.avg_age || 0}<span class="text-sm">세</span></div>
                </div>
                <div class="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
                    <div class="text-xs text-purple-600 mb-1">노령화지수</div>
                    <div class="text-2xl font-bold text-purple-900">${(basic.aging_index || 0).toFixed(1)}</div>
                </div>
                <div class="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg border border-orange-200">
                    <div class="text-xs text-orange-600 mb-1">노년부양비</div>
                    <div class="text-2xl font-bold text-orange-900">${(basic.oldage_support_ratio || 0).toFixed(1)}<span class="text-sm">%</span></div>
                </div>
                <div class="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
                    <div class="text-xs text-green-600 mb-1">인구밀도</div>
                    <div class="text-2xl font-bold text-green-900">${(basic.population_density || 0).toLocaleString()}<span class="text-sm text-xs">명/km²</span></div>
                </div>
            </div>
            
            <!-- 연령대별 인구 -->
            ${renderAgeGroupChart(ageGroups)}
        </div>
    `;
    
    // 정치인 섹션 뒤에 삽입
    const politiciansSection = document.querySelector('#detailView .max-w-5xl');
    if (politiciansSection && politiciansSection.nextSibling) {
        politiciansSection.parentNode.insertBefore(ageSection, politiciansSection.nextSibling.nextSibling);
    } else {
        detailView.appendChild(ageSection);
    }
}

function renderAgeGroupChart(ageGroups) {
    if (!ageGroups || Object.keys(ageGroups).length === 0) {
        return '<div class="text-gray-400 text-sm">연령대 데이터 없음</div>';
    }
    
    const ageOrder = ["0-9세", "10-19세", "20-29세", "30-39세", "40-49세", "50-59세", "60-69세", "70-79세", "80세 이상"];
    const maxPop = Math.max(...ageOrder.map(age => (ageGroups[age]?.total || 0)));
    
    return `
        <div class="space-y-3">
            <h4 class="font-semibold text-sm text-gray-700 mb-3">연령대별 인구 분포</h4>
            ${ageOrder.map(age => {
                const data = ageGroups[age] || {male: 0, female: 0, total: 0};
                const malePercent = maxPop ? (data.male / maxPop * 100) : 0;
                const femalePercent = maxPop ? (data.female / maxPop * 100) : 0;
                
                return `
                    <div class="flex items-center gap-3">
                        <div class="w-20 text-xs text-gray-600 text-right">${age}</div>
                        <div class="flex-1 flex items-center gap-1">
                            <div class="flex-1 h-6 flex justify-end">
                                <div class="h-full bg-blue-500 rounded-l transition-all" 
                                     style="width: ${malePercent}%"
                                     title="남성: ${data.male.toLocaleString()}명"></div>
                            </div>
                            <div class="w-16 text-center text-xs font-semibold text-gray-700">
                                ${data.total.toLocaleString()}
                            </div>
                            <div class="flex-1 h-6 flex">
                                <div class="h-full bg-pink-500 rounded-r transition-all" 
                                     style="width: ${femalePercent}%"
                                     title="여성: ${data.female.toLocaleString()}명"></div>
                            </div>
                        </div>
                        <div class="w-32 text-xs text-gray-500 flex justify-between">
                            <span class="text-blue-600">♂ ${data.male.toLocaleString()}</span>
                            <span class="text-pink-600">♀ ${data.female.toLocaleString()}</span>
                        </div>
                    </div>
                `;
            }).join('')}
            <div class="mt-4 pt-4 border-t border-gray-200 flex justify-center gap-6 text-xs">
                <div class="flex items-center gap-2">
                    <div class="w-4 h-4 bg-blue-500 rounded"></div>
                    <span class="text-gray-600">남성</span>
                </div>
                <div class="flex items-center gap-2">
                    <div class="w-4 h-4 bg-pink-500 rounded"></div>
                    <span class="text-gray-600">여성</span>
                </div>
            </div>
        </div>
    `;
}

// ============================================
// 정치인 섹션 렌더링
// ============================================

function renderPoliticiansSection(politicians) {
    if (!politicians || politicians.length === 0) {
        return '';
    }
    
    const partyColors = {
        '더불어민주당': 'bg-blue-100 text-blue-800 border-blue-300',
        '국민의힘': 'bg-red-100 text-red-800 border-red-300',
        '무소속': 'bg-gray-100 text-gray-800 border-gray-300',
        '진보당': 'bg-green-100 text-green-800 border-green-300',
        '기타': 'bg-purple-100 text-purple-800 border-purple-300'
    };
    
    const typeOrder = {
        '서울시장': 1,
        '구청장': 2,
        '국회의원': 3,
        '시의원': 4,
        '구의원': 5
    };
    
    return `
        <div class="bg-white p-6 rounded-lg shadow border border-gray-200 mb-6">
            <h3 class="font-bold text-lg mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                </svg>
                지역 정치인
            </h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                ${politicians.map(p => {
                    const colorClass = partyColors[p.party] || partyColors['기타'];
                    
                    // 아이콘 매핑
                    const icons = {
                        '서울시장': '🏛️',
                        '구청장': '🏢',
                        '국회의원': '🏛️',
                        '시의원': '🏙️',
                        '구의원': '🏘️'
                    };
                    const icon = icons[p.position] || '👤';
                    
                    return `
                        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                            <div class="text-2xl mb-2">${icon}</div>
                            <div class="text-xs text-gray-500 mb-1">${p.position || '정치인'}</div>
                            <div class="font-bold text-lg mb-2">${p.name}</div>
                            <div class="text-sm text-gray-600 mb-2">${p.district || ''}</div>
                            <div class="inline-block px-2 py-1 text-xs rounded border ${colorClass}">
                                ${p.party}
                            </div>
                            ${p.committee ? `<div class="text-xs text-gray-500 mt-2">${p.committee}</div>` : ''}
                        </div>
                    `;
                }).join('')}
            </div>
        </div>
    `;
}

// ============================================
// 항목별 추이 상세 차트
// ============================================

function showDetailedChart() {
    const data = window.currentTimeseriesData;
    if (!data) return;
    
    const timeseries = data.timeseries || {};
    const years = data.years || [];
    
    // 모든 항목 데이터 추출
    const datasets = extractAllDatasets(timeseries, years);
    
    // 모달 생성
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-white rounded-xl shadow-2xl max-w-7xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                <h2 class="text-2xl font-bold text-gray-900 flex items-center">
                    <svg class="w-6 h-6 mr-2 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                    </svg>
                    항목별 추이 분석
                </h2>
                <button onclick="this.closest('.fixed').remove()" class="text-gray-400 hover:text-gray-600">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            
            <div class="p-6">
                <!-- 카테고리 탭 -->
                <div class="mb-6 flex space-x-2 overflow-x-auto pb-2">
                    ${renderCategoryTabs()}
                </div>
                
                <!-- 차트 영역 -->
                <div id="detailedChartContent">
                    ${renderCategoryCharts('household', datasets, years)}
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function renderCategoryTabs() {
    const categories = [
        { id: 'household', name: '가구/인구', icon: '👨‍👩‍👧‍👦' },
        { id: 'house', name: '주택', icon: '🏠' },
        { id: 'company', name: '사업체', icon: '🏢' }
    ];
    
    return categories.map((cat, idx) => `
        <button onclick="switchChartCategory('${cat.id}')" 
            class="chart-tab px-6 py-3 rounded-lg font-medium transition-all ${idx === 0 ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}"
            data-category="${cat.id}">
            ${cat.icon} ${cat.name}
        </button>
    `).join('');
}

function switchChartCategory(category) {
    const data = window.currentTimeseriesData;
    if (!data) return;
    
    const timeseries = data.timeseries || {};
    const years = data.years || [];
    const datasets = extractAllDatasets(timeseries, years);
    
    // 탭 스타일 변경
    document.querySelectorAll('.chart-tab').forEach(tab => {
        if (tab.dataset.category === category) {
            tab.className = 'chart-tab px-6 py-3 rounded-lg font-medium transition-all bg-indigo-600 text-white';
        } else {
            tab.className = 'chart-tab px-6 py-3 rounded-lg font-medium transition-all bg-gray-100 text-gray-600 hover:bg-gray-200';
        }
    });
    
    // 차트 업데이트
    document.getElementById('detailedChartContent').innerHTML = renderCategoryCharts(category, datasets, years);
}

function extractAllDatasets(timeseries, years) {
    const datasets = {
        household: {},
        house: {},
        company: {}
    };
    
    years.forEach(year => {
        const yearData = timeseries[year] || {};
        
        // 가구/인구 (연령별 데이터 우선 사용)
        let population = 0;
        let households = 0;
        let avgSize = 0;
        
        if (yearData.basic && yearData.basic.total_population > 0) {
            population = yearData.basic.total_population;
            avgSize = yearData.household?.avg_family_member_cnt || 2.0;
            households = Math.round(population / avgSize);
        } else {
            const household = yearData.household || {};
            population = household.family_member_cnt || 0;
            households = household.household_cnt || 0;
            avgSize = household.avg_family_member_cnt || 0;
        }
        
        if (!datasets.household.population) datasets.household.population = [];
        if (!datasets.household.households) datasets.household.households = [];
        if (!datasets.household.avgSize) datasets.household.avgSize = [];
        
        datasets.household.population.push(population);
        datasets.household.households.push(households);
        datasets.household.avgSize.push(avgSize);
        
        // 주택
        const house = yearData.house || {};
        if (!datasets.house.total) datasets.house.total = [];
        if (!datasets.house.detached) datasets.house.detached = [];
        if (!datasets.house.apt) datasets.house.apt = [];
        if (!datasets.house.multi) datasets.house.multi = [];
        
        datasets.house.total.push(house.house_cnt || 0);
        datasets.house.detached.push(house.detached_house_cnt || 0);
        datasets.house.apt.push(house.apt_cnt || 0);
        datasets.house.multi.push(house.multi_house_cnt || 0);
        
        // 사업체
        const company = yearData.company || {};
        if (!datasets.company.total) datasets.company.total = [];
        if (!datasets.company.employees) datasets.company.employees = [];
        if (!datasets.company.avgEmployees) datasets.company.avgEmployees = [];
        
        datasets.company.total.push(company.corp_cnt || 0);
        datasets.company.employees.push(company.corp_emp_cnt || 0);
        datasets.company.avgEmployees.push(company.avg_corp_emp_cnt || 0);
    });
    
    return datasets;
}

function renderCategoryCharts(category, datasets, years) {
    const categoryConfig = {
        household: [
            { key: 'population', name: '인구수', unit: '명', color: '#3b82f6' },
            { key: 'households', name: '가구수', unit: '가구', color: '#10b981' },
            { key: 'avgSize', name: '평균 가구원수', unit: '명/가구', color: '#f59e0b' }
        ],
        house: [
            { key: 'total', name: '전체 주택', unit: '호', color: '#8b5cf6' },
            { key: 'detached', name: '단독주택', unit: '호', color: '#ec4899' },
            { key: 'apt', name: '아파트', unit: '호', color: '#06b6d4' },
            { key: 'multi', name: '다가구주택', unit: '호', color: '#f97316' }
        ],
        company: [
            { key: 'total', name: '사업체수', unit: '개', color: '#6366f1' },
            { key: 'employees', name: '종사자수', unit: '명', color: '#14b8a6' },
            { key: 'avgEmployees', name: '평균 종사자수', unit: '명/사업체', color: '#f59e0b' }
        ]
    };
    
    const items = categoryConfig[category] || [];
    const data = datasets[category] || {};
    
    return `
        <div class="grid grid-cols-1 gap-6">
            ${items.map(item => {
                const values = data[item.key] || [];
                if (values.length === 0) return '';
                
                return renderLineChart(item.name, values, years, item.unit, item.color);
            }).join('')}
        </div>
    `;
}

function renderLineChart(title, values, years, unit, color) {
    const max = Math.max(...values);
    const min = Math.min(...values);
    const range = max - min || 1;
    
    // SVG 포인트 생성
    const width = 800;
    const height = 200;
    const padding = 40;
    const chartWidth = width - padding * 2;
    const chartHeight = height - padding * 2;
    
    const points = values.map((v, i) => {
        const x = padding + (i / (values.length - 1)) * chartWidth;
        const y = padding + chartHeight - ((v - min) / range * chartHeight);
        return `${x},${y}`;
    }).join(' ');
    
    // 변화율 계산
    const firstValue = values[0];
    const lastValue = values[values.length - 1];
    const changeRate = firstValue ? ((lastValue - firstValue) / firstValue * 100).toFixed(1) : 0;
    const isPositive = changeRate >= 0;
    
    return `
        <div class="bg-gray-50 p-6 rounded-lg border border-gray-200">
            <div class="flex items-center justify-between mb-4">
                <h4 class="font-bold text-lg">${title}</h4>
                <div class="text-right">
                    <div class="text-2xl font-bold" style="color: ${color}">${lastValue.toLocaleString()} ${unit}</div>
                    <div class="text-sm ${isPositive ? 'text-green-600' : 'text-red-600'}">
                        ${isPositive ? '▲' : '▼'} ${Math.abs(changeRate)}% (${years[0]}→${years[years.length-1]})
                    </div>
                </div>
            </div>
            
            <svg viewBox="0 0 ${width} ${height}" class="w-full bg-white rounded">
                <!-- 그리드 라인 -->
                ${Array.from({length: 5}, (_, i) => {
                    const y = padding + (chartHeight / 4) * i;
                    const value = max - (range / 4) * i;
                    return `
                        <line x1="${padding}" y1="${y}" x2="${width - padding}" y2="${y}" 
                            stroke="#e5e7eb" stroke-width="1"/>
                        <text x="${padding - 5}" y="${y + 5}" 
                            text-anchor="end" font-size="12" fill="#6b7280">
                            ${Math.round(value).toLocaleString()}
                        </text>
                    `;
                }).join('')}
                
                <!-- 데이터 라인 -->
                <polyline points="${points}" 
                    fill="none" 
                    stroke="${color}" 
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"/>
                
                <!-- 데이터 포인트 -->
                ${values.map((v, i) => {
                    const x = padding + (i / (values.length - 1)) * chartWidth;
                    const y = padding + chartHeight - ((v - min) / range * chartHeight);
                    return `
                        <circle cx="${x}" cy="${y}" r="4" fill="${color}"/>
                        <text x="${x}" y="${height - 10}" 
                            text-anchor="middle" font-size="12" fill="#6b7280">
                            ${years[i]}
                        </text>
                    `;
                }).join('')}
            </svg>
        </div>
    `;
}

function renderSigunguDetail(data) {
    console.log('🎨 renderSigunguDetail 호출됨');
    console.log('📦 받은 데이터:', data);
    
    const detailView = document.getElementById('detailView');
    
    // 새로운 데이터 구조 사용
    const household = data.household || {};
    const company = data.company || {};
    const housing = data.house || {};  // 백엔드는 'house' 키 사용
    
    // 총 인구 계산
    const totalPopulation = (household.male_population || 0) + (household.female_population || 0);
    const maleRatio = totalPopulation > 0 ? ((household.male_population || 0) / totalPopulation * 100) : 0;
    
    console.log('📊 계산된 값:', {
        totalPopulation,
        maleRatio,
        household_cnt: household.household_cnt,
        house_cnt: housing.house_cnt
    });
    
    detailView.innerHTML = `
        <div class="max-w-5xl">
            <!-- 헤더 -->
            <div class="mb-6">
                <h2 class="text-3xl font-bold text-gray-900">${data.full_address || ''}</h2>
                <p class="text-gray-600 mt-1">시군구 코드: ${data.sigungu_code}</p>
            </div>
            
            <!-- 시계열 차트 영역 -->
            <div id="timeseriesChart" class="mb-6"></div>
            
            <!-- 주요 통계 카드 -->
            <div class="grid grid-cols-4 gap-4 mb-6">
                <div class="bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-xl shadow-lg text-white">
                    <div class="text-sm opacity-90 mb-1">총 인구</div>
                    <div class="text-3xl font-bold">${totalPopulation ? totalPopulation.toLocaleString() : '-'}</div>
                    <div class="text-xs opacity-75 mt-1">명</div>
                </div>
                
                <div class="bg-gradient-to-br from-pink-500 to-pink-600 p-6 rounded-xl shadow-lg text-white">
                    <div class="text-sm opacity-90 mb-1">성비</div>
                    <div class="text-3xl font-bold">${maleRatio ? maleRatio.toFixed(1) : '-'}%</div>
                    <div class="text-xs opacity-75 mt-1">남성 비율</div>
                </div>
                
                <div class="bg-gradient-to-br from-green-500 to-green-600 p-6 rounded-xl shadow-lg text-white">
                    <div class="text-sm opacity-90 mb-1">총 세대수</div>
                    <div class="text-3xl font-bold">${household.household_cnt ? household.household_cnt.toLocaleString() : '-'}</div>
                    <div class="text-xs opacity-75 mt-1">가구</div>
                </div>
                
                <div class="bg-gradient-to-br from-orange-500 to-orange-600 p-6 rounded-xl shadow-lg text-white">
                    <div class="text-sm opacity-90 mb-1">총 주택수</div>
                    <div class="text-3xl font-bold">${housing.house_cnt ? housing.house_cnt.toLocaleString() : '-'}</div>
                    <div class="text-xs opacity-75 mt-1">호</div>
                </div>
            </div>
            
            <!-- 추가 정보 -->
            <div class="bg-white p-6 rounded-lg shadow border border-gray-200 mb-6">
                <h3 class="font-bold text-lg mb-4 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                    </svg>
                    상세 정보
                </h3>
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-blue-50 p-4 rounded-lg border border-blue-200">
                        <div class="text-sm text-gray-600 mb-1">남성 인구</div>
                        <div class="text-2xl font-bold text-blue-600">${household.male_population ? household.male_population.toLocaleString() : '-'}</div>
                        <div class="text-xs text-gray-500">명</div>
                    </div>
                    <div class="bg-pink-50 p-4 rounded-lg border border-pink-200">
                        <div class="text-sm text-gray-600 mb-1">여성 인구</div>
                        <div class="text-2xl font-bold text-pink-600">${household.female_population ? household.female_population.toLocaleString() : '-'}</div>
                        <div class="text-xs text-gray-500">명</div>
                    </div>
                    <div class="bg-green-50 p-4 rounded-lg border border-green-200">
                        <div class="text-sm text-gray-600 mb-1">사업체 수</div>
                        <div class="text-2xl font-bold text-green-600">${company.corp_cnt ? company.corp_cnt.toLocaleString() : '-'}</div>
                        <div class="text-xs text-gray-500">개</div>
                    </div>
                    <div class="bg-orange-50 p-4 rounded-lg border border-orange-200">
                        <div class="text-sm text-gray-600 mb-1">종사자 수</div>
                        <div class="text-2xl font-bold text-orange-600">${company.tot_worker ? company.tot_worker.toLocaleString() : '-'}</div>
                        <div class="text-xs text-gray-500">명</div>
                    </div>
                </div>
            </div>
            
            <!-- 정치인 정보 섹션 -->
            <div id="politicianSection" class="mb-6"></div>
            
            <!-- 데이터 출처 -->
            <div class="bg-gray-50 p-4 rounded-lg border border-gray-200 text-sm text-gray-600">
                📊 데이터 출처: ${data.data_source || '주민등록 2025-09 (인구/가구 합산)'} | 사업체/주택: SGIS 2023 (집계)
            </div>
        </div>
    `;
    
    // 정치인 정보 로드
    loadSigunguPoliticians(data.sigungu_code, data.full_address);
}


async function loadSigunguPoliticians(sigunguCode, fullAddress) {
    const section = document.getElementById('politicianSection');
    if (!section) return;
    
    // 서울 구 이름 추출 (예: "서울특별시 강남구" -> "강남구")
    const guMatch = fullAddress.match(/([가-힣]+구)/);
    if (!guMatch) {
        section.innerHTML = '';
        return;
    }
    
    const guName = guMatch[1];
    
    // 현재 정치인 정보 로드 (제8회 기준)
    let politicians = [];
    
    try {
        // 시의원 데이터
        const siResponse = await fetch(`${API_BASE}/api/politicians/si_uiwon`);
        const siData = await siResponse.json();
        if (siData[guName]) {
            politicians.push(...siData[guName].map(p => ({...p, position: '시의원'})));
        }
        
        // 구의원 데이터
        const guResponse = await fetch(`${API_BASE}/api/politicians/gu_uiwon`);
        const guData = await guResponse.json();
        if (guData[guName]) {
            politicians.push(...guData[guName].map(p => ({...p, position: '구의원'})));
        }
        
        // 국회의원 데이터 (해당 구)
        const naResponse = await fetch(`${API_BASE}/api/politicians/national_assembly`);
        const naData = await naResponse.json();
        const naPoliticians = naData.filter(p => p.district && p.district.includes(guName));
        politicians.push(...naPoliticians.map(p => ({...p, position: '국회의원'})));
        
    } catch (error) {
        console.error('정치인 정보 로드 실패:', error);
    }
    
    if (politicians.length === 0) {
        section.innerHTML = '';
        return;
    }
    
    // 정치인 정보 렌더링
    const byPosition = {};
    politicians.forEach(p => {
        const pos = p.position || '기타';
        if (!byPosition[pos]) byPosition[pos] = [];
        byPosition[pos].push(p);
    });
    
    let html = `
        <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
            <h3 class="font-bold text-lg mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                </svg>
                ${guName} 정치인 (제8회 현재)
            </h3>
            <div class="grid grid-cols-1 gap-4">
    `;
    
    Object.entries(byPosition).forEach(([position, pols]) => {
        const colorClass = {
            '국회의원': 'blue',
            '시의원': 'green',
            '구의원': 'purple'
        }[position] || 'gray';
        
        html += `
            <div class="bg-${colorClass}-50 p-4 rounded-lg border border-${colorClass}-200">
                <div class="font-bold text-${colorClass}-800 mb-2">${position} (${pols.length}명)</div>
                <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                    ${pols.map(p => `
                        <div class="text-sm">
                            <span class="font-medium">${p.name}</span>
                            <span class="text-gray-600 text-xs">(${p.party || '-'})</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    });
    
    html += `
            </div>
            <div class="mt-4 text-sm text-gray-500">
                💡 타임라인 차트에서 제5-8회 지방선거(2010-2026), 제16-22대 국회의원(2000-2028) 임기를 확인할 수 있습니다.
            </div>
        </div>
    `;
    
    section.innerHTML = html;
    
    // 시계열 차트에 정치인 정보 반영
    loadSigunguTimeseries(sigunguCode, politicians);
}

function renderEmdongDetail(emdong) {
    console.log('🎨 renderEmdongDetail 호출됨');
    console.log('📦 렌더링할 데이터:', emdong);
    
    const detailView = document.getElementById('detailView');
    
    if (!detailView) {
        console.error('❌ detailView 요소를 찾을 수 없습니다');
        return;
    }
    
    const household = emdong.household || {};
    const house = emdong.house || {};
    const company = emdong.company || {};
    
    // 주민등록 데이터는 실제 단위, SGIS 데이터는 100배 필요
    const is_jumin_data = emdong.data_source && emdong.data_source.includes('주민등록');
    const multiplier = is_jumin_data ? 1 : 100;
    
    const household_real = {
        household_cnt: (household.household_cnt || 0) * multiplier,
        family_member_cnt: (household.family_member_cnt || 0) * multiplier,
        avg_family_member_cnt: household.avg_family_member_cnt || 0,
        male_population: (household.male_population || 0) * multiplier,
        female_population: (household.female_population || 0) * multiplier
    };
    
    const house_real = {
        house_cnt: (house.house_cnt || 0) * 100  // 주택은 SGIS만
    };
    
    const company_real = {
        corp_cnt: (company.corp_cnt || 0) * 100,  // 사업체는 SGIS만
        tot_worker: (company.tot_worker || 0) * 100
    };
    
    console.log('📊 가구 (실제):', household_real, `[출처: ${emdong.data_source || 'SGIS'}]`);
    console.log('🏢 사업체 (실제):', company_real);
    console.log('🏠 주택 (실제):', house_real);
    
    detailView.innerHTML = `
        <div class="max-w-5xl">
            <!-- 헤더 -->
            <div class="mb-6">
                <h2 class="text-3xl font-bold text-gray-900">${emdong.full_address || (emdong.sido_name + ' ' + emdong.sigungu_name + ' ' + emdong.emdong_name)}</h2>
                <p class="text-gray-600 mt-1">행정동 코드: ${emdong.emdong_code || emdong.code} | 인구 데이터: ${emdong.data_year || selectedYear + '년'}</p>
            </div>
            
            <!-- 시계열 차트 영역 -->
            <div id="timeseriesChart" class="mb-6"></div>
            
            <!-- 정치인 정보 -->
            ${renderPoliticiansSection(emdong.politicians || [])}
            
            <!-- 주요 통계 카드 (미니 그래프 포함) -->
            <div id="mainStatsCards" class="grid grid-cols-4 gap-4 mb-6">
                <div class="bg-gradient-to-br from-blue-500 to-blue-600 p-4 rounded-xl shadow-lg text-white">
                    <div class="text-xs opacity-90 mb-1">인구 (${emdong.data_year || selectedYear + '년'})</div>
                    <div class="text-2xl font-bold mb-1">${household_real.family_member_cnt.toLocaleString()}<span class="text-sm ml-1">명</span></div>
                    <div class="h-12 mb-1" id="miniChart-population" style="min-height: 48px;"></div>
                </div>
                
                <div class="bg-gradient-to-br from-green-500 to-green-600 p-4 rounded-xl shadow-lg text-white">
                    <div class="text-xs opacity-90 mb-1">가구수 (${emdong.data_year || selectedYear + '년'})</div>
                    <div class="text-2xl font-bold mb-1">${household_real.household_cnt.toLocaleString()}<span class="text-sm ml-1">가구</span></div>
                    <div class="h-12 mb-1" id="miniChart-household" style="min-height: 48px;"></div>
                </div>
                
                <div class="bg-gradient-to-br from-purple-500 to-purple-600 p-4 rounded-xl shadow-lg text-white">
                    <div class="text-xs opacity-90 mb-1">주택수 (${selectedYear}년)</div>
                    <div class="text-2xl font-bold mb-1">${house_real.house_cnt.toLocaleString()}<span class="text-sm ml-1">호</span></div>
                    <div class="h-12 mb-1" id="miniChart-house" style="min-height: 48px;"></div>
                </div>
                
                <div class="bg-gradient-to-br from-orange-500 to-orange-600 p-4 rounded-xl shadow-lg text-white">
                    <div class="text-xs opacity-90 mb-1">사업체 (${selectedYear}년)</div>
                    <div class="text-2xl font-bold mb-1">${company_real.corp_cnt.toLocaleString()}<span class="text-sm ml-1">개</span></div>
                    <div class="h-12 mb-1" id="miniChart-company" style="min-height: 48px;"></div>
                </div>
            </div>
            
            <!-- 상세 통계 -->
            <div class="grid grid-cols-2 gap-6 mb-6">
                <!-- 가구 정보 -->
                <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
                    <h3 class="font-bold text-lg mb-4 flex items-center">
                        <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
                        </svg>
                        가구 정보
                    </h3>
                    <div class="space-y-3">
                        <div class="flex justify-between items-center py-2 border-b border-gray-100">
                            <span class="text-gray-700">총 가구수</span>
                            <span class="font-semibold">${household_real.household_cnt.toLocaleString()}가구</span>
                        </div>
                        <div class="flex justify-between items-center py-2 border-b border-gray-100">
                            <span class="text-gray-700">총 인구</span>
                            <span class="font-semibold">${household_real.family_member_cnt.toLocaleString()}명</span>
                        </div>
                        <div class="flex justify-between items-center py-2">
                            <span class="text-gray-700">평균 가구원수</span>
                            <span class="font-semibold text-blue-600">${household_real.avg_family_member_cnt.toFixed(1)}명</span>
                        </div>
                    </div>
                </div>
                
                <!-- 사업체 정보 -->
                <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
                    <h3 class="font-bold text-lg mb-4 flex items-center">
                        <svg class="w-5 h-5 mr-2 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                        </svg>
                        사업체 정보
                    </h3>
                    <div class="space-y-3">
                        <div class="flex justify-between items-center py-2 border-b border-gray-100">
                            <span class="text-gray-700">사업체수</span>
                            <span class="font-semibold">${company_real.corp_cnt.toLocaleString()}개</span>
                        </div>
                        <div class="flex justify-between items-center py-2 border-b border-gray-100">
                            <span class="text-gray-700">종사자수</span>
                            <span class="font-semibold">${company_real.tot_worker.toLocaleString()}명</span>
                        </div>
                        <div class="flex justify-between items-center py-2">
                            <span class="text-gray-700">평균 종사자수</span>
                            <span class="font-semibold text-orange-600">${company_real.corp_cnt ? (company_real.tot_worker / company_real.corp_cnt).toFixed(1) : 0}명/사업체</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
                <strong>📊 데이터 출처:</strong> ${emdong.data_source ? '주민등록인구통계 2025년 9월' : '통계지리정보서비스(SGIS) 2023년'} (인구/가구) | SGIS 2023년 (사업체/주택)
            </div>
        </div>
    `;
}

// ============================================
// 지역 목록 렌더링
// ============================================

// 전역 상태: 접힌/펼쳐진 구
let expandedGus = new Set();
let expandedSeoul = false;

function renderRegionList(regions) {
    const regionList = document.getElementById('regionList');
    
    // 시도별로 그룹화
    const bySido = {};
    regions.forEach(region => {
        const sido = region.sido || '기타';
        if (!bySido[sido]) bySido[sido] = [];
        bySido[sido].push(region);
    });
    
    let html = '';
    
    Object.keys(bySido).sort().forEach(sido => {
        const sidoRegions = bySido[sido];
        const totalPop = sidoRegions.reduce((sum, r) => sum + (r.population || 0), 0);
        const isExpanded = expandedSeoul && sido === '서울특별시';
        
        // 시도 헤더
        html += `
            <div class="mb-2">
                <div class="font-bold text-gray-900 px-3 py-2 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg cursor-pointer hover:from-blue-100 hover:to-blue-150 flex items-center justify-between"
                     onclick='toggleSeoul()'>
                    <div class="flex items-center gap-2">
                        <svg class="w-4 h-4 transform transition-transform ${isExpanded ? 'rotate-90' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                        <span>${sido}</span>
                    </div>
                    <span class="text-xs text-gray-600">${sidoRegions.length}개 동</span>
                </div>
                
                ${isExpanded ? renderSeoulGus(sidoRegions) : ''}
            </div>
        `;
    });
    
    regionList.innerHTML = html;
}

function renderSeoulGus(regions) {
    // 구별로 그룹화
    const byGu = {};
    regions.forEach(region => {
        const gu = region.sigungu || '기타';
        if (!byGu[gu]) byGu[gu] = [];
        byGu[gu].push(region);
    });
    
    let html = '<div class="mt-2 space-y-2">';
    
    Object.keys(byGu).sort().forEach(gu => {
        const guRegions = byGu[gu];
        const isExpanded = expandedGus.has(gu);
        
        html += `
            <div class="ml-2">
                <div class="font-semibold text-gray-700 px-2 py-1.5 bg-white rounded cursor-pointer hover:bg-blue-50 border border-gray-200 flex items-center justify-between"
                     onclick='toggleGu("${gu}")'>
                    <div class="flex items-center gap-2">
                        <svg class="w-3 h-3 transform transition-transform ${isExpanded ? 'rotate-90' : ''}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                        <span class="text-sm">${gu}</span>
                    </div>
                    <span class="text-xs text-gray-500">${guRegions.length}동</span>
                </div>
                
                ${isExpanded ? `
                <div class="mt-1 ml-4 space-y-1">
                    ${guRegions.map(region => {
                        const pop = region.population || 0;
                        const popText = pop > 0 ? `${(pop / 1000).toFixed(1)}천` : '-';
                        
                        return `
                            <div class="p-2 hover:bg-blue-50 rounded cursor-pointer border border-gray-100 text-sm transition-colors"
                                 onclick='selectRegion("${region.code}")'>
                                <div class="flex justify-between items-center">
                                    <span class="text-gray-700">${region.dong || region.name}</span>
                                    <span class="text-xs text-gray-500">${popText}</span>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
                ` : ''}
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

function toggleSeoul() {
    expandedSeoul = !expandedSeoul;
    renderRegionList(allRegions);
}

function toggleGu(gu) {
    if (expandedGus.has(gu)) {
        expandedGus.delete(gu);
    } else {
        expandedGus.add(gu);
    }
    renderRegionList(allRegions);
}

// ============================================
// GDP, 교통, 안전 정보 렌더링 함수
// ============================================

function renderGdpInfo(regionData) {
    const gdpData = regionData.gdpData;
    if (!gdpData || !gdpData.yearlyGdp) return '<div></div>';
    
    const years = Object.keys(gdpData.yearlyGdp).sort();
    const latestYear = years[years.length - 1];
    const latestGdp = gdpData.yearlyGdp[latestYear];
    const prevYear = years[years.length - 2];
    const prevGdp = gdpData.yearlyGdp[prevYear];
    const growthRate = prevGdp ? ((latestGdp - prevGdp) / prevGdp * 100) : 0;
    
    return `
        <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
            <h3 class="font-bold text-lg mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                경제 (GRDP)
            </h3>
            <div class="space-y-3">
                <div class="flex justify-between py-2 border-b border-gray-100">
                    <span class="text-gray-700">${latestYear}년 GRDP</span>
                    <span class="font-semibold text-blue-600">${(latestGdp / 1000000).toFixed(1)}조원</span>
                </div>
                <div class="flex justify-between py-2">
                    <span class="text-gray-700">전년 대비</span>
                    <span class="font-semibold ${growthRate > 0 ? 'text-green-600' : 'text-red-600'}">
                        ${growthRate > 0 ? '+' : ''}${growthRate.toFixed(1)}%
                    </span>
                </div>
            </div>
        </div>
    `;
}

function renderTrafficInfo(regionData) {
    const trafficData = regionData.trafficData;
    if (!trafficData || !trafficData.yearlyData) return '<div></div>';
    
    const years = Object.keys(trafficData.yearlyData).sort();
    const latestYear = years[years.length - 1];
    const latestTraffic = trafficData.yearlyData[latestYear];
    const prevYear = years[years.length - 2];
    const prevTraffic = trafficData.yearlyData[prevYear];
    const growthRate = prevTraffic ? ((latestTraffic.totalUsage - prevTraffic.totalUsage) / prevTraffic.totalUsage * 100) : 0;
    
    return `
        <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
            <h3 class="font-bold text-lg mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
                교통
            </h3>
            <div class="space-y-3">
                <div class="flex justify-between py-2 border-b border-gray-100">
                    <span class="text-gray-700">${latestYear}년 이용</span>
                    <span class="font-semibold text-green-600">${(latestTraffic.totalUsage / 1000000).toFixed(1)}백만명</span>
                </div>
                <div class="flex justify-between py-2">
                    <span class="text-gray-700">전년 대비</span>
                    <span class="font-semibold ${growthRate > 0 ? 'text-green-600' : 'text-red-600'}">
                        ${growthRate > 0 ? '+' : ''}${growthRate.toFixed(1)}%
                    </span>
                </div>
            </div>
        </div>
    `;
}

function renderSafetyInfo(regionData) {
    const safetyData = regionData.safetyData;
    if (!safetyData) return '<div></div>';
    
    return `
        <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
            <h3 class="font-bold text-lg mb-4 flex items-center">
                <svg class="w-5 h-5 mr-2 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                </svg>
                안전·복지
            </h3>
            <div class="space-y-3">
                ${safetyData.elderlyLivingAlone ? `
                <div class="flex justify-between py-2 border-b border-gray-100">
                    <span class="text-gray-700">독거노인</span>
                    <span class="font-semibold text-orange-600">${safetyData.elderlyLivingAlone.toLocaleString()}명</span>
                </div>
                ` : ''}
                ${safetyData.disabledPopulation ? `
                <div class="flex justify-between py-2 border-b border-gray-100">
                    <span class="text-gray-700">장애인</span>
                    <span class="font-semibold">${safetyData.disabledPopulation.toLocaleString()}명</span>
                </div>
                ` : ''}
                ${safetyData.crimeRate ? `
                <div class="flex justify-between py-2">
                    <span class="text-gray-700">범죄율</span>
                    <span class="font-semibold text-red-600">${safetyData.crimeRate.toFixed(2)}%</span>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

// ============================================
// 지역 검색 필터
// ============================================

function filterRegions() {
    const query = document.getElementById('regionSearch').value.toLowerCase();
    
    if (!query) {
        renderRegionList(allRegions);
        return;
    }
    
    const filtered = allRegions.filter(region => {
        const searchText = `${region.sigungu} ${region.dong}`.toLowerCase();
        return searchText.includes(query);
    });
    
    renderRegionList(filtered);
}

// ============================================
// 지역 선택
// ============================================

async function selectRegion(code) {
    try {
        const response = await fetch(`${API_BASE}/api/regions/${encodeURIComponent(code)}`);
        const regionData = await response.json();
        
        currentRegion = regionData;
        renderRegionDetail(regionData, code);
        
    } catch (error) {
        console.error('❌ 지역 상세 정보 로드 실패:', error);
    }
}

// ============================================
// 지역 상세 정보 렌더링
// ============================================

function renderRegionDetail(regionData, code) {
    const detailView = document.getElementById('detailView');
    
    const popData = regionData.population_data || {};
    const realEstateData = regionData.realEstateData || {};
    
    const sido = regionData.sido_name || '서울특별시';
    const sigungu = regionData.sigungu_name || '';
    const dong = regionData.dong_name || '';
    
    detailView.innerHTML = `
        <div class="max-w-5xl">
            <!-- 헤더 -->
            <div class="mb-6">
                <h2 class="text-3xl font-bold text-gray-900">${sido} ${sigungu} ${dong}</h2>
                <p class="text-gray-600 mt-1">행정동 코드: ${regionData.admin_dong_code || code}</p>
            </div>
            
            <!-- 주요 통계 카드 -->
            <div class="grid grid-cols-4 gap-4 mb-6">
                <div class="bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-xl shadow-lg text-white">
                    <div class="text-sm opacity-90 mb-1">총 인구</div>
                    <div class="text-3xl font-bold">${(popData.total_population || 0).toLocaleString()}</div>
                    <div class="text-xs opacity-75 mt-1">명</div>
                </div>
                
                <div class="bg-gradient-to-br from-green-500 to-green-600 p-6 rounded-xl shadow-lg text-white">
                    <div class="text-sm opacity-90 mb-1">평균 연령</div>
                    <div class="text-3xl font-bold">${(popData.total_avg_age || 0).toFixed(1)}</div>
                    <div class="text-xs opacity-75 mt-1">세</div>
                </div>
                
                <div class="bg-gradient-to-br from-purple-500 to-purple-600 p-6 rounded-xl shadow-lg text-white">
                    <div class="text-sm opacity-90 mb-1">인구 밀도</div>
                    <div class="text-3xl font-bold">${(popData.population_density || 0).toLocaleString()}</div>
                    <div class="text-xs opacity-75 mt-1">명/km²</div>
                </div>
                
                <div class="bg-gradient-to-br from-orange-500 to-orange-600 p-6 rounded-xl shadow-lg text-white">
                    <div class="text-sm opacity-90 mb-1">고령자 비율</div>
                    <div class="text-3xl font-bold">${(popData.aged_65_plus_ratio || 0).toFixed(1)}</div>
                    <div class="text-xs opacity-75 mt-1">%</div>
                </div>
            </div>
            
            <!-- 상세 통계 -->
            <div class="grid grid-cols-2 gap-6 mb-6">
                <!-- 인구 구성 -->
                <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
                    <h3 class="font-bold text-lg mb-4 flex items-center">
                        <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                        </svg>
                        인구 구성
                    </h3>
                    <div class="space-y-3">
                        <div class="flex justify-between items-center py-2 border-b border-gray-100">
                            <span class="text-gray-700">남성</span>
                            <span class="font-semibold text-blue-600">${(popData.male_population || 0).toLocaleString()}명 (${(popData.male_ratio || 0).toFixed(1)}%)</span>
                        </div>
                        <div class="flex justify-between items-center py-2 border-b border-gray-100">
                            <span class="text-gray-700">여성</span>
                            <span class="font-semibold text-pink-600">${(popData.female_population || 0).toLocaleString()}명 (${(popData.female_ratio || 0).toFixed(1)}%)</span>
                        </div>
                        <div class="flex justify-between items-center py-2 border-b border-gray-100">
                            <span class="text-gray-700">세대수</span>
                            <span class="font-semibold">${(popData.household_count || 0).toLocaleString()}세대</span>
                        </div>
                        <div class="flex justify-between items-center py-2">
                            <span class="text-gray-700">세대당 인구</span>
                            <span class="font-semibold">${(popData.avg_household_size || 0).toFixed(2)}명</span>
                        </div>
                    </div>
                </div>
                
                <!-- 고령화 지표 -->
                <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
                    <h3 class="font-bold text-lg mb-4 flex items-center">
                        <svg class="w-5 h-5 mr-2 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                        </svg>
                        연령 구조
                    </h3>
                    <div class="space-y-3">
                        <div class="flex justify-between items-center py-2 border-b border-gray-100">
                            <span class="text-gray-700">65세 이상</span>
                            <span class="font-semibold text-orange-600">${(popData.aged_65_plus_total || 0).toLocaleString()}명</span>
                        </div>
                        <div class="flex justify-between items-center py-2 border-b border-gray-100">
                            <span class="text-gray-700">고령자 비율</span>
                            <span class="font-semibold">${(popData.aged_65_plus_ratio || 0).toFixed(1)}%</span>
                        </div>
                        <div class="flex justify-between items-center py-2 border-b border-gray-100">
                            <span class="text-gray-700">중위연령</span>
                            <span class="font-semibold">${(popData.total_median_age || 0).toFixed(1)}세</span>
                        </div>
                        <div class="flex justify-between items-center py-2">
                            <span class="text-gray-700">외국인</span>
                            <span class="font-semibold text-purple-600">${(popData.foreigner_count || 0).toLocaleString()}명 (${(popData.foreigner_ratio || 0).toFixed(1)}%)</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 부동산 정보 -->
            ${realEstateData.mae_price_index ? `
            <div class="bg-white p-6 rounded-lg shadow border border-gray-200 mb-6">
                <h3 class="font-bold text-lg mb-4 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
                    </svg>
                    부동산 가격지수 (2024년)
                </h3>
                <div class="grid grid-cols-2 gap-4">
                    <div class="bg-blue-50 p-4 rounded-lg">
                        <div class="text-sm text-gray-600 mb-1">매매가격지수</div>
                        <div class="text-2xl font-bold text-blue-600">${(realEstateData.mae_price_index['2024'] || 0).toFixed(1)}</div>
                    </div>
                    <div class="bg-green-50 p-4 rounded-lg">
                        <div class="text-sm text-gray-600 mb-1">전세가격지수</div>
                        <div class="text-2xl font-bold text-green-600">${(realEstateData.jeon_price_index ? realEstateData.jeon_price_index['2024'] : 0).toFixed(1)}</div>
                    </div>
                </div>
            </div>
            ` : ''}
            
            <!-- GDP, 교통, 안전 정보 -->
            <div class="grid grid-cols-3 gap-6 mb-6">
                ${renderGdpInfo(regionData)}
                ${renderTrafficInfo(regionData)}
                ${renderSafetyInfo(regionData)}
            </div>
            
            <!-- 추가 통계 -->
            <div class="grid grid-cols-2 gap-6 mb-6">
                <!-- 복지 정보 -->
                <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
                    <h3 class="font-bold text-lg mb-4 flex items-center">
                        <svg class="w-5 h-5 mr-2 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
                        </svg>
                        복지
                    </h3>
                    <div class="space-y-3">
                        <div class="flex justify-between py-2 border-b border-gray-100">
                            <span class="text-gray-700">수급자</span>
                            <span class="font-semibold">${(popData.welfare_recipients || 0).toLocaleString()}명</span>
                        </div>
                        <div class="flex justify-between py-2 border-b border-gray-100">
                            <span class="text-gray-700">수급 세대</span>
                            <span class="font-semibold">${(popData.welfare_households || 0).toLocaleString()}세대</span>
                        </div>
                        <div class="flex justify-between py-2">
                            <span class="text-gray-700">수급 비율</span>
                            <span class="font-semibold text-green-600">${(popData.welfare_ratio || 0).toFixed(1)}%</span>
                        </div>
                    </div>
                </div>
                
                <!-- 면적 정보 -->
                <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
                    <h3 class="font-bold text-lg mb-4 flex items-center">
                        <svg class="w-5 h-5 mr-2 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"></path>
                        </svg>
                        지역 정보
                    </h3>
                    <div class="space-y-3">
                        <div class="flex justify-between py-2 border-b border-gray-100">
                            <span class="text-gray-700">면적</span>
                            <span class="font-semibold">${(popData.area || 0).toFixed(2)} km²</span>
                        </div>
                        <div class="flex justify-between py-2 border-b border-gray-100">
                            <span class="text-gray-700">인구 증감률</span>
                            <span class="font-semibold ${(popData.population_growth_rate || 0) > 0 ? 'text-green-600' : 'text-red-600'}">
                                ${(popData.population_growth_rate || 0) > 0 ? '+' : ''}${(popData.population_growth_rate || 0).toFixed(2)}%
                            </span>
                        </div>
                        <div class="flex justify-between py-2">
                            <span class="text-gray-700">성비</span>
                            <span class="font-semibold">남 ${(popData.male_ratio || 0).toFixed(1)} : 여 ${(popData.female_ratio || 0).toFixed(1)}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 정치인 정보 -->
            <div class="bg-white p-6 rounded-lg shadow border border-gray-200 mb-6">
                <h3 class="font-bold text-lg mb-4 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                    </svg>
                    정치인 정보
                </h3>
                <div id="politicianInfo" class="text-gray-500">
                    로딩 중...
                </div>
            </div>
            
            <!-- 비교/순위 버튼 -->
            <div class="flex gap-4">
                <button onclick="showComparison('${sigungu}')" class="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center gap-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                    </svg>
                    구 비교
                </button>
                <button onclick="showRankings('${sigungu}')" class="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors flex items-center justify-center gap-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                    </svg>
                    순위 보기
                </button>
                <button onclick="toggleLDAPanel()" class="flex-1 px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition-colors flex items-center justify-center gap-2">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    LDA 분석
                </button>
            </div>
        </div>
    `;
    
    // 정치인 정보 로드
    loadPoliticianInfo(sigungu, dong);
}

// ============================================
// 비교 및 순위 기능
// ============================================

function showComparison(gu) {
    alert(`${gu} 비교 기능 - 구현 예정`);
}

function showRankings(gu) {
    const detailView = document.getElementById('detailView');
    detailView.innerHTML = `
        <div class="max-w-5xl">
            <div class="mb-6">
                <h2 class="text-3xl font-bold text-gray-900">서울시 구별 순위</h2>
                <p class="text-gray-600 mt-1">25개 구 비교</p>
            </div>
            
            <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
                <div class="text-center py-12 text-gray-500">
                    순위 데이터 로딩 중...
                </div>
            </div>
        </div>
    `;
    
    // 순위 데이터 로드
    loadRankings();
}

async function loadRankings() {
    // 전체 지역 데이터로 순위 계산
    const rankings = {
        population: [...allRegions].sort((a, b) => (b.population || 0) - (a.population || 0)),
        avg_age: [...allRegions].sort((a, b) => (b.avg_age || 0) - (a.avg_age || 0)),
        density: [...allRegions].sort((a, b) => (b.density || 0) - (a.density || 0))
    };
    
    const detailView = document.getElementById('detailView');
    detailView.innerHTML = `
        <div class="max-w-5xl">
            <div class="mb-6">
                <h2 class="text-3xl font-bold text-gray-900">서울시 읍면동 순위</h2>
                <p class="text-gray-600 mt-1">426개 읍면동 비교</p>
            </div>
            
            <div class="grid grid-cols-3 gap-6">
                <!-- 인구 순위 -->
                <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
                    <h3 class="font-bold text-lg mb-4 text-blue-600">인구 TOP 10</h3>
                    <div class="space-y-2">
                        ${rankings.population.slice(0, 10).map((region, idx) => `
                            <div class="flex items-center gap-3 p-2 hover:bg-blue-50 rounded cursor-pointer" onclick='selectRegion("${region.code}")'>
                                <div class="w-6 h-6 rounded-full ${idx < 3 ? 'bg-yellow-500' : 'bg-gray-300'} flex items-center justify-center text-white text-xs font-bold">
                                    ${idx + 1}
                                </div>
                                <div class="flex-1">
                                    <div class="text-sm font-semibold">${region.sigungu} ${region.dong}</div>
                                    <div class="text-xs text-gray-500">${(region.population || 0).toLocaleString()}명</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <!-- 평균나이 순위 -->
                <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
                    <h3 class="font-bold text-lg mb-4 text-green-600">평균나이 TOP 10</h3>
                    <div class="space-y-2">
                        ${rankings.avg_age.slice(0, 10).map((region, idx) => `
                            <div class="flex items-center gap-3 p-2 hover:bg-green-50 rounded cursor-pointer" onclick='selectRegion("${region.code}")'>
                                <div class="w-6 h-6 rounded-full ${idx < 3 ? 'bg-yellow-500' : 'bg-gray-300'} flex items-center justify-center text-white text-xs font-bold">
                                    ${idx + 1}
                                </div>
                                <div class="flex-1">
                                    <div class="text-sm font-semibold">${region.sigungu} ${region.dong}</div>
                                    <div class="text-xs text-gray-500">${(region.avg_age || 0).toFixed(1)}세</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <!-- 인구밀도 순위 -->
                <div class="bg-white p-6 rounded-lg shadow border border-gray-200">
                    <h3 class="font-bold text-lg mb-4 text-purple-600">인구밀도 TOP 10</h3>
                    <div class="space-y-2">
                        ${rankings.density.slice(0, 10).map((region, idx) => `
                            <div class="flex items-center gap-3 p-2 hover:bg-purple-50 rounded cursor-pointer" onclick='selectRegion("${region.code}")'>
                                <div class="w-6 h-6 rounded-full ${idx < 3 ? 'bg-yellow-500' : 'bg-gray-300'} flex items-center justify-center text-white text-xs font-bold">
                                    ${idx + 1}
                                </div>
                                <div class="flex-1">
                                    <div class="text-sm font-semibold">${region.sigungu} ${region.dong}</div>
                                    <div class="text-xs text-gray-500">${(region.density || 0).toLocaleString()}명/km²</div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
}

// ============================================
// 정치인 정보 로드
// ============================================

async function loadPoliticianInfo(sigungu, dong) {
    const container = document.getElementById('politicianInfo');
    
    try {
        // 국회의원, 시의원, 구청장, 구의원 정보
        container.innerHTML = `
            <div class="space-y-4">
                <div class="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                    <div class="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                        국
                    </div>
                    <div>
                        <div class="font-semibold">국회의원</div>
                        <div class="text-sm text-gray-600">데이터 로딩 중...</div>
                    </div>
                </div>
                
                <div class="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                    <div class="w-10 h-10 bg-green-600 rounded-full flex items-center justify-center text-white font-bold">
                        구
                    </div>
                    <div>
                        <div class="font-semibold">구청장</div>
                        <div class="text-sm text-gray-600">${sigungu}</div>
                    </div>
                </div>
                
                <div class="text-sm text-gray-500 mt-4">
                    * 정치인 LDA 분석 기능은 개발 중입니다
                </div>
            </div>
        `;
    } catch (error) {
        container.innerHTML = '<div class="text-gray-500">정치인 정보를 불러올 수 없습니다</div>';
    }
}

// ============================================
// 네트워크 지도
// ============================================

async function showNetworkMap() {
    document.getElementById('networkModal').classList.remove('hidden');
    
    if (!networkData) {
        await loadNetworkData();
    }
    
    renderNetwork();
}

function closeNetworkMap(event) {
    if (event && event.target.id !== 'networkModal') return;
    document.getElementById('networkModal').classList.add('hidden');
}

async function loadNetworkData() {
    try {
        const response = await fetch(`${API_BASE}/api/network/assembly`);
        networkData = await response.json();
        console.log('✅ 네트워크 데이터 로드 완료');
    } catch (error) {
        console.error('❌ 네트워크 데이터 로드 실패:', error);
    }
}

function renderNetwork() {
    const container = document.getElementById('networkCanvas');
    
    if (!networkData) {
        container.innerHTML = '<div class="flex items-center justify-center h-full"><div class="text-gray-500">네트워크 데이터 로딩 중...</div></div>';
        return;
    }
    
    const mode = document.getElementById('networkMode').value;
    
    container.innerHTML = `
        <div class="flex items-center justify-center h-full flex-col gap-4">
            <div class="text-2xl font-bold text-gray-700">
                ${mode === 'issue' ? '의원-이슈 연결망' : '의원-의원 연결망'}
            </div>
            <div class="text-gray-600">
                ${networkData.members ? Object.keys(networkData.members).length : 0}명 의원
            </div>
            <div class="text-gray-600">
                ${mode === 'issue' ? 
                    `${networkData.issues ? Object.keys(networkData.issues).length : 0}개 이슈` :
                    `${networkData.member_connections ? networkData.member_connections.length : 0}개 연결`
                }
            </div>
            <div class="text-sm text-gray-500 mt-4">
                D3.js 네트워크 시각화 구현 중...
            </div>
        </div>
    `;
}

function updateNetworkMode() {
    renderNetwork();
}

function searchMembers() {
    const query = document.getElementById('memberSearch').value;
    console.log('의원 검색:', query);
}

// ============================================
// LDA 패널 토글
// ============================================

function toggleLDAPanel() {
    const panel = document.getElementById('ldaPanel');
    panel.classList.toggle('hidden');
}

// ============================================
// 전역 검색
// ============================================

document.getElementById('globalSearch')?.addEventListener('keyup', function(e) {
    const query = e.target.value;
    if (query.length >= 2) {
        performGlobalSearch(query);
    }
});

async function performGlobalSearch(query) {
    try {
        const response = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        console.log('검색 결과:', results);
    } catch (error) {
        console.error('검색 실패:', error);
    }
}

// ============================================
// 시계열 그래프 (D3.js)
// ============================================

async function loadAndRenderTimeseries(emdongCode, politicians) {
    try {
        const response = await fetch(`${API_BASE}/api/emdong/${emdongCode}/timeseries`);
        const data = await response.json();
        
        if (!data.timeseries || data.timeseries.length === 0) {
            console.log('시계열 데이터 없음');
            return;
        }
        
        // 인구 + 사업체/주택 데이터 모두 전달
        renderTimeseriesChart(data.timeseries, politicians, data.yearly_business);
        
    } catch (error) {
        console.error('시계열 데이터 로드 실패:', error);
    }
}

function renderTimeseriesChart(timeseriesData, politicians, yearlyBusiness) {
    const container = document.getElementById('timeseriesChart');
    if (!container) return;
    
    // 컨테이너 초기화 및 지표 선택 버튼 추가
    container.innerHTML = `
        <div class="bg-white p-4 rounded-lg shadow border border-gray-200">
            <div class="flex justify-between items-center mb-3">
                <h3 class="font-bold text-lg">시계열 분석 - 정치와 지역 성장 관계분석</h3>
                <div class="flex gap-2">
                    <button onclick="switchMetric('population')" id="btn-population" class="px-3 py-1 text-xs rounded bg-blue-600 text-white">인구</button>
                    <button onclick="switchMetric('business')" id="btn-business" class="px-3 py-1 text-xs rounded bg-gray-200 text-gray-700">사업체</button>
                    <button onclick="switchMetric('housing')" id="btn-housing" class="px-3 py-1 text-xs rounded bg-gray-200 text-gray-700">주택</button>
                </div>
            </div>
            <div id="chartContainer"></div>
            <div id="periodInfo" class="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg hidden">
                <div class="flex justify-between items-center">
                    <div>
                        <span class="text-sm font-semibold text-blue-900">선택 기간: </span>
                        <span id="selectedPeriod" class="text-sm text-blue-700"></span>
                    </div>
                    <button onclick="showPeriodPoliticians()" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-semibold flex items-center gap-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                        </svg>
                        해당 기간 지역 정치인 보기
                    </button>
                </div>
            </div>
            <div id="periodStats"></div>
        </div>
    `;
    
    // 차트 크기 (적당한 높이)
    const margin = {top: 30, right: 100, bottom: 50, left: 70};
    const width = container.clientWidth - margin.left - margin.right - 40;
    const height = 280 - margin.top - margin.bottom;
    
    // 정치인 임기 정보 구조화 (지방선거 5-8회 + 국회의원 16-22대)
    const politicianTerms = [];
    
    if (politicians && politicians.length > 0) {
        // 직위별 그룹화
        const byPosition = {};
        politicians.forEach(p => {
            const pos = p.position || p.type || '기타';
            if (!byPosition[pos]) byPosition[pos] = [];
            byPosition[pos].push(p);
        });
        
        // 각 직위별 색상
        const positionColors = {
            '서울시장': '#ef4444',
            '구청장': '#f97316',
            '국회의원': '#3b82f6',
            '시의원': '#10b981',
            '구의원': '#8b5cf6'
        };
        
        // 지방선거 임기 (시의원, 구의원, 시장, 구청장)
        const localElectionTerms = [
            {round: 5, start: '2010-07-01', end: '2014-06-30'},
            {round: 6, start: '2014-07-01', end: '2018-06-30'},
            {round: 7, start: '2018-07-01', end: '2022-06-30'},
            {round: 8, start: '2022-07-01', end: '2026-06-30'}
        ];
        
        const localPositions = ['시의원', '구의원', '서울시장', '구청장'];
        
        localElectionTerms.forEach(({round, start, end}) => {
            Object.entries(byPosition).forEach(([position, pols]) => {
                if (localPositions.includes(position)) {
                    politicianTerms.push({
                        startDate: new Date(start),
                        endDate: new Date(end),
                        politicians: pols,
                        position: position,
                        color: positionColors[position] || '#6b7280',
                        label: `${position} (제${round}회)`
                    });
                }
            });
        });
        
        // 국회의원 임기
        const nationalElectionTerms = [
            {term: 16, start: '2000-05-30', end: '2004-05-29'},
            {term: 17, start: '2004-05-30', end: '2008-05-29'},
            {term: 18, start: '2008-05-30', end: '2012-05-29'},
            {term: 19, start: '2012-05-30', end: '2016-05-29'},
            {term: 20, start: '2016-05-30', end: '2020-05-29'},
            {term: 21, start: '2020-05-30', end: '2024-05-29'},
            {term: 22, start: '2024-05-30', end: '2028-05-29'}
        ];
        
        if (byPosition['국회의원']) {
            nationalElectionTerms.forEach(({term, start, end}) => {
                politicianTerms.push({
                    startDate: new Date(start),
                    endDate: new Date(end),
                    politicians: byPosition['국회의원'],
                    position: '국회의원',
                    color: positionColors['국회의원'],
                    label: `국회의원 (제${term}대)`
                });
            });
        }
    }
    
    // 현재 데이터 저장 (지표 전환용)
    window.currentTimeseriesData = timeseriesData;
    window.currentYearlyBusiness = yearlyBusiness;
    window.currentPoliticians = politicians;
    window.currentPoliticianTerms = politicianTerms;
    window.currentChartSize = {width, height, margin};
    
    // 인구 그래프 먼저 그리기
    drawPopulationChart();
}

// 선택된 기간의 정치인 보기
function showPeriodPoliticians() {
    const selectedPeriod = window.selectedPeriod;
    if (!selectedPeriod) {
        alert('기간을 선택해주세요. 그래프를 드래그하여 기간을 선택할 수 있습니다.');
        return;
    }
    
    const allTerms = window.currentPoliticianTerms || [];
    
    // 선택된 기간과 겹치는 정치인 임기 찾기
    const overlappingTerms = allTerms.filter(term => {
        return term.startDate <= selectedPeriod.end && term.endDate >= selectedPeriod.start;
    });
    
    if (overlappingTerms.length === 0) {
        alert('선택한 기간에 해당하는 정치인이 없습니다.');
        return;
    }
    
    // 직위별로 그룹화
    const byPosition = {};
    overlappingTerms.forEach(term => {
        const position = term.position;
        if (!byPosition[position]) byPosition[position] = [];
        
        // 정치인들을 정당별로 분류
        const byParty = {};
        term.politicians.forEach(p => {
            const party = p.party || '무소속';
            if (!byParty[party]) byParty[party] = [];
            byParty[party].push(p);
        });
        
        byPosition[position].push({
            label: term.label,
            byParty: byParty,
            color: term.color
        });
    });
    
    // 정당별 색상
    const partyColors = {
        '국민의힘': '#E61E2B',
        '더불어민주당': '#1E90FF',
        '민주당': '#1E90FF',
        '조국혁신당': '#FF6B9D',
        '개혁신당': '#00A0E9',
        '진보당': '#EA5504',
        '무소속': '#808080',
        '새누리당': '#B8003C',
        '자유한국당': '#B8003C',
        '정의당': '#FFCC00',
        '기타': '#999999'
    };
    
    const startYear = selectedPeriod.start.getFullYear();
    const endYear = selectedPeriod.end.getFullYear();
    
    let html = `
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onclick="this.remove()">
            <div class="bg-white rounded-lg shadow-2xl max-w-4xl w-full max-h-[85vh] overflow-y-auto m-4" onclick="event.stopPropagation()">
                <div class="sticky top-0 bg-gradient-to-r from-indigo-600 to-blue-600 text-white p-6 z-10">
                    <div class="flex justify-between items-center">
                        <div>
                            <h2 class="text-2xl font-bold">${startYear}년 ~ ${endYear}년 지역 정치인</h2>
                            <p class="text-sm opacity-90 mt-1">선택 기간에 재직한 모든 정치인 명단</p>
                        </div>
                        <button onclick="this.closest('.fixed').remove()" class="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="p-6">
    `;
    
    // 직위별로 표시 (국회의원 > 시의원 > 구의원 순)
    const positionOrder = ['국회의원', '시의원', '구의원', '서울시장', '구청장'];
    const positionNames = {
        '국회의원': '🏛️ 국회의원',
        '시의원': '🏢 시의원',
        '구의원': '🏘️ 구의원',
        '서울시장': '👔 서울시장',
        '구청장': '👔 구청장'
    };
    
    positionOrder.forEach(position => {
        if (!byPosition[position]) return;
        
        html += `
            <div class="mb-8">
                <h3 class="text-xl font-bold mb-4 pb-2 border-b-2 border-gray-200">${positionNames[position] || position}</h3>
        `;
        
        byPosition[position].forEach(termData => {
            html += `
                <div class="mb-6 bg-gray-50 p-4 rounded-lg">
                    <h4 class="font-semibold text-lg mb-3" style="color: ${termData.color};">${termData.label}</h4>
                    <div class="space-y-3">
            `;
            
            // 정당별로 정렬 (인원 많은 순)
            const sortedParties = Object.entries(termData.byParty).sort((a, b) => b[1].length - a[1].length);
            
            sortedParties.forEach(([party, politicians]) => {
                const partyColor = partyColors[party] || '#999999';
                
                html += `
                    <div class="border-l-4 pl-4 py-2" style="border-color: ${partyColor};">
                        <div class="flex items-center justify-between mb-2">
                            <div class="flex items-center gap-2">
                                <div class="w-3 h-3 rounded-full" style="background-color: ${partyColor};"></div>
                                <span class="font-bold">${party}</span>
                                <span class="text-sm text-gray-600">${politicians.length}명</span>
                            </div>
                        </div>
                        <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
                            ${politicians.map(p => `
                                <div class="text-sm px-2 py-1 bg-white rounded border border-gray-200 hover:shadow-md transition-shadow">
                                    <div class="font-medium">${p.name}</div>
                                    ${p.district && p.district !== position ? `<div class="text-xs text-gray-500 truncate">${p.district}</div>` : ''}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        });
        
        html += `</div>`;
    });
    
    html += `
                </div>
            </div>
        </div>
    `;
    
    // 팝업 추가
    const popup = document.createElement('div');
    popup.innerHTML = html;
    document.body.appendChild(popup.firstElementChild);
}
window.showPeriodPoliticians = showPeriodPoliticians;

// 이전 함수 제거 (미사용)
function showPoliticianDetail_OLD(term) {
    // 정당별 그룹화
    const byParty = {};
    term.politicians.forEach(p => {
        const party = p.party || '무소속';
        if (!byParty[party]) byParty[party] = [];
        byParty[party].push(p);
    });
    
    // 정당별 색상
    const partyColors = {
        '국민의힘': '#E61E2B',
        '더불어민주당': '#1E90FF',
        '민주당': '#1E90FF',
        '조국혁신당': '#FF6B9D',
        '개혁신당': '#00A0E9',
        '진보당': '#EA5504',
        '무소속': '#808080',
        '새누리당': '#B8003C',
        '자유한국당': '#B8003C',
        '정의당': '#FFCC00',
        '기타': '#999999'
    };
    
    const startYear = term.startDate.getFullYear();
    const endYear = term.endDate.getFullYear();
    
    let html = `
        <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onclick="this.remove()">
            <div class="bg-white rounded-lg shadow-2xl max-w-3xl w-full max-h-[80vh] overflow-y-auto m-4" onclick="event.stopPropagation()">
                <div class="sticky top-0 bg-gradient-to-r from-${term.position === '국회의원' ? 'blue' : term.position === '시의원' ? 'green' : 'purple'}-600 to-${term.position === '국회의원' ? 'blue' : term.position === '시의원' ? 'green' : 'purple'}-700 text-white p-6">
                    <div class="flex justify-between items-center">
                        <div>
                            <h2 class="text-2xl font-bold">${term.label}</h2>
                            <p class="text-sm opacity-90 mt-1">${startYear}년 ~ ${endYear}년 (${endYear - startYear}년간)</p>
                        </div>
                        <button onclick="this.closest('.fixed').remove()" class="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div class="p-6">
                    <!-- 요약 정보 -->
                    <div class="grid grid-cols-3 gap-4 mb-6">
                        <div class="bg-blue-50 p-4 rounded-lg border border-blue-200">
                            <div class="text-sm text-gray-600">총 인원</div>
                            <div class="text-2xl font-bold text-blue-600">${term.politicians.length}명</div>
                        </div>
                        <div class="bg-green-50 p-4 rounded-lg border border-green-200">
                            <div class="text-sm text-gray-600">정당 수</div>
                            <div class="text-2xl font-bold text-green-600">${Object.keys(byParty).length}개</div>
                        </div>
                        <div class="bg-purple-50 p-4 rounded-lg border border-purple-200">
                            <div class="text-sm text-gray-600">직위</div>
                            <div class="text-2xl font-bold text-purple-600">${term.position}</div>
                        </div>
                    </div>
                    
                    <!-- 정당별 목록 -->
                    <h3 class="font-bold text-lg mb-4">정당별 명단</h3>
                    <div class="space-y-4">
    `;
    
    // 정당별로 정렬 (인원 많은 순)
    const sortedParties = Object.entries(byParty).sort((a, b) => b[1].length - a[1].length);
    
    sortedParties.forEach(([party, politicians]) => {
        const partyColor = partyColors[party] || '#999999';
        
        html += `
            <div class="border rounded-lg p-4" style="border-color: ${partyColor};">
                <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center">
                        <div class="w-4 h-4 rounded-full mr-2" style="background-color: ${partyColor};"></div>
                        <span class="font-bold text-lg">${party}</span>
                    </div>
                    <span class="text-sm text-gray-600">${politicians.length}명</span>
                </div>
                <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2">
                    ${politicians.map(p => `
                        <div class="text-sm px-2 py-1 bg-gray-50 rounded border border-gray-200">
                            <span class="font-medium">${p.name}</span>
                            ${p.district && p.district !== term.position ? `<div class="text-xs text-gray-500 truncate">${p.district}</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    });
    
    html += `
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 팝업 추가
    const popup = document.createElement('div');
    popup.innerHTML = html;
    document.body.appendChild(popup.firstElementChild);
}
window.showPoliticianDetail = showPoliticianDetail;

function drawPopulationChart() {
    const {width, height, margin} = window.currentChartSize;
    const timeseriesData = window.currentTimeseriesData;
    const politicianTerms = window.currentPoliticianTerms || [];
    
    console.log('📊 정치인 임기 정보:', politicianTerms);
    
    // 컨테이너 초기화
    d3.select('#chartContainer').html('');
    
    // SVG 생성
    const svg = d3.select('#chartContainer')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .style('background', 'white')
        .style('border-radius', '8px')
        .style('box-shadow', '0 1px 3px rgba(0,0,0,0.1)')
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // 날짜 파싱
    const parseDate = d3.timeParse('%Y-%m');
    timeseriesData.forEach(d => {
        d.parsedDate = parseDate(d.date);
    });
    
    // X축: 시간 (2000년부터 표시 - 정치인 임기 고려)
    const dataExtent = d3.extent(timeseriesData, d => d.parsedDate);
    const extendedStart = new Date('2000-01-01');
    const extendedEnd = dataExtent[1] > new Date('2026-01-01') ? dataExtent[1] : new Date('2028-12-31');
    
    const x = d3.scaleTime()
        .domain([extendedStart, extendedEnd])
        .range([0, width]);
    
    // Y축: 인구
    const y = d3.scaleLinear()
        .domain([
            d3.min(timeseriesData, d => Math.min(d.population, d.male, d.female)) * 0.95,
            d3.max(timeseriesData, d => d.population) * 1.05
        ])
        .range([height, 0]);
    
    // X축 그리기 (3년 간격으로 표시 - 밀집도 완화)
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x)
            .ticks(d3.timeYear.every(3))  // 3년 간격
            .tickFormat(d3.timeFormat('%Y')))
        .selectAll('text')
        .style('font-size', '12px')
        .style('font-weight', 'bold');
    
    // Y축 그리기
    svg.append('g')
        .call(d3.axisLeft(y)
            .ticks(5)
            .tickFormat(d => d.toLocaleString()))
        .selectAll('text')
        .style('font-size', '11px');
    
    // 직위별 색상 (심플하게)
    const positionColors = {
        '서울시장': '#ef4444',
        '구청장': '#f97316',
        '국회의원': '#3b82f6',
        '시의원': '#10b981',
        '구의원': '#8b5cf6'
    };
    
    // 정치인 임기 배경 표시 (간결한 형태)
    politicianTerms.forEach((term, idx) => {
        const termStart = term.startDate;
        const termEnd = term.endDate;
        
        // 그래프 범위 내에 있는지 확인
        const xDomain = x.domain();
        if (termEnd >= xDomain[0] && termStart <= xDomain[1]) {
            const startX = Math.max(0, x(termStart));
            const endX = Math.min(width, x(termEnd));
            
            // 직위별로 높이 구분 (간단하게)
            const totalBars = politicianTerms.length;
            const barHeight = Math.min(20, height / (totalBars * 1.2));  // 최대 20px
            const yPos = height - (idx + 1) * barHeight * 1.2;  // 아래에서 위로
            
            // 주요 정당 추출 (최대 2개)
            const partyCount = {};
            term.politicians.forEach(p => {
                const party = p.party || '무소속';
                partyCount[party] = (partyCount[party] || 0) + 1;
            });
            const mainParties = Object.entries(partyCount)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 2)
                .map(p => p[0]);
            
            // 배경 바 (직위 색상, 반투명)
            svg.append('rect')
                .attr('x', startX)
                .attr('y', yPos)
                .attr('width', endX - startX)
                .attr('height', barHeight)
                .attr('fill', term.color)
                .attr('opacity', 0.15)
                .attr('stroke', term.color)
                .attr('stroke-width', 1.5)
                .attr('rx', 3);
            
            // 임기 정보 텍스트 (간결하게)
            const barWidth = endX - startX;
            if (barWidth > 60) {
                const labelText = `${term.label} (${mainParties.join('·')})`;
                
                svg.append('text')
                    .attr('x', startX + 5)
                    .attr('y', yPos + barHeight / 2 + 4)
                    .style('font-size', '10px')
                    .style('font-weight', '600')
                    .attr('fill', term.color)
                    .text(labelText)
                    .append('title')
                    .text(`${term.position} ${term.label}\n정치인 ${term.politicians.length}명\n주요 정당: ${mainParties.join(', ')}`);
            }
        }
    });
    
    // 총 인구 라인 표시 (정치인 바 위에)
    const line = d3.line()
        .x(d => x(d.parsedDate))
        .y(d => y(d.population))
        .curve(d3.curveMonotoneX);
    
    // 인구 라인을 맨 위 레이어에
    const populationLayer = svg.append('g')
        .attr('class', 'population-layer');
    
    populationLayer.append('path')
        .datum(timeseriesData)
        .attr('fill', 'none')
        .attr('stroke', '#3b82f6')
        .attr('stroke-width', 3)
        .attr('d', line);
    
    // 범례 추가 (간결하게)
    const legend = svg.append('g')
        .attr('transform', `translate(${width - 80}, -20)`);
    
    legend.append('line')
        .attr('x1', 0)
        .attr('x2', 20)
        .attr('y1', 0)
        .attr('y2', 0)
        .attr('stroke', '#3b82f6')
        .attr('stroke-width', 3);
    
    legend.append('text')
        .attr('x', 25)
        .attr('y', 5)
        .style('font-size', '11px')
        .style('font-weight', '500')
        .text('인구');
    
    // 드래그 선택 기능 추가
    const brush = d3.brushX()
        .extent([[0, 0], [width, height]])
        .on('end', function(event) {
            if (!event.selection) {
                // 선택 해제
                window.selectedPeriod = null;
                document.getElementById('periodInfo').classList.add('hidden');
                return;
            }
            
            const [x0, x1] = event.selection;
            const startDate = x.invert(x0);
            const endDate = x.invert(x1);
            
            // 선택된 기간 저장
            window.selectedPeriod = {
                start: startDate,
                end: endDate
            };
            
            // 기간 정보 표시
            const startYear = startDate.getFullYear();
            const endYear = endDate.getFullYear();
            const startMonth = startDate.getMonth() + 1;
            const endMonth = endDate.getMonth() + 1;
            
            document.getElementById('selectedPeriod').textContent = 
                `${startYear}년 ${startMonth}월 ~ ${endYear}년 ${endMonth}월`;
            document.getElementById('periodInfo').classList.remove('hidden');
        });
    
    svg.append('g')
        .attr('class', 'brush')
        .call(brush);
    
    // 인터랙티브 영역 (보이지 않는 넓은 영역)
    svg.selectAll('.hover-area')
        .data(timeseriesData)
        .enter()
        .append('rect')
        .attr('class', 'hover-area')
        .attr('x', (d, i) => {
            if (i === 0) return x(d.parsedDate);
            const prevDate = timeseriesData[i-1].parsedDate;
            return (x(prevDate) + x(d.parsedDate)) / 2;
        })
        .attr('y', 0)
        .attr('width', (d, i) => {
            if (i === timeseriesData.length - 1) return width - x(d.parsedDate);
            const nextDate = timeseriesData[i+1].parsedDate;
            return (x(nextDate) - x(d.parsedDate)) / 2;
        })
        .attr('height', height)
        .attr('fill', 'transparent')
        .on('mouseover', function(event, d) {
            // 포인트 표시
            svg.append('circle')
                .attr('class', 'hover-dot')
                .attr('cx', x(d.parsedDate))
                .attr('cy', y(d.population))
                .attr('r', 5)
                .attr('fill', '#1e40af')
                .attr('stroke', 'white')
                .attr('stroke-width', 2);
            
            // 세로선
            svg.append('line')
                .attr('class', 'hover-line')
                .attr('x1', x(d.parsedDate))
                .attr('x2', x(d.parsedDate))
                .attr('y1', 0)
                .attr('y2', height)
                .attr('stroke', '#cbd5e1')
                .attr('stroke-width', 1)
                .attr('stroke-dasharray', '3,3');
            
            // 툴팁 표시
            d3.select('body')
                .append('div')
                .attr('class', 'tooltip')
                .style('position', 'absolute')
                .style('background', 'white')
                .style('padding', '10px 14px')
                .style('border', '2px solid #3b82f6')
                .style('border-radius', '6px')
                .style('box-shadow', '0 4px 6px rgba(0,0,0,0.15)')
                .style('pointer-events', 'none')
                .style('font-size', '13px')
                .html(`
                    <div style="font-weight: bold; color: #1e40af; margin-bottom: 6px;">${d.date}</div>
                    <div>총 인구: <strong>${d.population.toLocaleString()}명</strong></div>
                    <div>남성: ${d.male.toLocaleString()}명</div>
                    <div>여성: ${d.female.toLocaleString()}명</div>
                    <div style="margin-top: 4px; padding-top: 4px; border-top: 1px solid #e5e7eb;">
                        증감: <strong style="color: ${d.change >= 0 ? '#10b981' : '#ef4444'}">${d.change >= 0 ? '+' : ''}${d.change.toLocaleString()}명</strong>
                    </div>
                `)
                .style('left', (event.pageX + 15) + 'px')
                .style('top', (event.pageY - 10) + 'px');
        })
        .on('mouseout', function() {
            d3.selectAll('.tooltip').remove();
            d3.selectAll('.hover-dot').remove();
            d3.selectAll('.hover-line').remove();
        });
    
    // 범례 제거 (총 인구만 표시하므로 불필요)
    
    // 제목
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', -15)
        .attr('text-anchor', 'middle')
        .style('font-size', '14px')
        .style('font-weight', 'bold')
        .text('월별 인구 변화 추이');
    
    // Y축 레이블
    svg.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', -50)
        .attr('x', -height / 2)
        .attr('text-anchor', 'middle')
        .style('font-size', '11px')
        .attr('fill', '#6b7280')
        .text('인구 (명)');
}

// 선택 기간 통계 표시
function showPeriodStats(selectedData) {
    const container = document.getElementById('periodStats') || createPeriodStatsContainer();
    
    const startData = selectedData[0];
    const endData = selectedData[selectedData.length - 1];
    const popChange = endData.population - startData.population;
    const changePercent = (popChange / startData.population * 100).toFixed(2);
    
    container.innerHTML = `
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
            <h4 class="font-bold text-sm mb-2 text-blue-900">📊 선택 기간 통계</h4>
            <div class="grid grid-cols-2 gap-3 text-sm">
                <div>
                    <div class="text-gray-600">기간</div>
                    <div class="font-semibold">${startData.date} ~ ${endData.date}</div>
                </div>
                <div>
                    <div class="text-gray-600">인구 변화</div>
                    <div class="font-semibold ${popChange >= 0 ? 'text-green-600' : 'text-red-600'}">
                        ${popChange >= 0 ? '+' : ''}${popChange.toLocaleString()}명 (${changePercent >= 0 ? '+' : ''}${changePercent}%)
                    </div>
                </div>
                <div>
                    <div class="text-gray-600">시작 인구</div>
                    <div class="font-semibold">${startData.population.toLocaleString()}명</div>
                </div>
                <div>
                    <div class="text-gray-600">종료 인구</div>
                    <div class="font-semibold">${endData.population.toLocaleString()}명</div>
                </div>
            </div>
        </div>
    `;
}

function createPeriodStatsContainer() {
    const container = document.createElement('div');
    container.id = 'periodStats';
    const chartContainer = document.getElementById('timeseriesChart');
    if (chartContainer) {
        chartContainer.appendChild(container);
    }
    return container;
}

// 시군구용 시계열 로드 (정치인 데이터 포함 가능)
async function loadSigunguTimeseries(sigunguCode, politicians) {
    try {
        const response = await fetch(`${API_BASE}/api/sigungu/${sigunguCode}/timeseries`);
        const data = await response.json();
        
        if (!data.timeseries || data.timeseries.length === 0) {
            console.log('시군구 시계열 데이터 없음');
            return;
        }
        
        renderTimeseriesChart(data.timeseries, politicians, data.yearly_business);
        
    } catch (error) {
        console.error('시군구 시계열 데이터 로드 실패:', error);
    }
}

// 지표 전환 함수
function switchMetric(metric) {
    // 버튼 스타일 업데이트
    ['population', 'business', 'housing'].forEach(m => {
        const btn = document.getElementById(`btn-${m}`);
        if (btn) {
            if (m === metric) {
                btn.className = 'px-3 py-1 text-xs rounded bg-blue-600 text-white';
            } else {
                btn.className = 'px-3 py-1 text-xs rounded bg-gray-200 text-gray-700';
            }
        }
    });
    
    // 해당 지표 그래프 그리기
    if (metric === 'population') {
        drawPopulationChart();
    } else if (metric === 'business') {
        drawBusinessChart();
    } else if (metric === 'housing') {
        drawHousingChart();
    }
}
window.switchMetric = switchMetric;

// 사업체 그래프
function drawBusinessChart() {
    const {width, height, margin} = window.currentChartSize;
    const yearlyBusiness = window.currentYearlyBusiness || [];
    const politicianTerms = window.currentPoliticianTerms || [];
    
    if (yearlyBusiness.length === 0) {
        d3.select('#chartContainer').html('<div class="text-center py-8 text-gray-500">사업체 데이터 없음</div>');
        return;
    }
    
    d3.select('#chartContainer').html('');
    
    const svg = d3.select('#chartContainer')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // X축: 연도
    const x = d3.scaleBand()
        .domain(yearlyBusiness.map(d => d.year))
        .range([0, width])
        .padding(0.3);
    
    // Y축: 사업체수
    const y = d3.scaleLinear()
        .domain([0, d3.max(yearlyBusiness, d => d.company_cnt) * 1.1])
        .range([height, 0]);
    
    // 정치인 임기 배경 (연도 기반)
    politicianTerms.forEach((term, idx) => {
        const termStartYear = term.startDate.getFullYear();
        const termEndYear = term.endDate.getFullYear();
        
        // 해당하는 연도들 찾기
        const years = yearlyBusiness.map(d => d.year).filter(y => y >= termStartYear && y <= termEndYear);
        
        if (years.length > 0) {
            const startX = x(years[0]);
            const endX = x(years[years.length - 1]) + x.bandwidth();
            const barHeight = height / Math.max(politicianTerms.length, 1);
            const yPos = idx * barHeight;
            
            svg.append('rect')
                .attr('x', startX)
                .attr('y', yPos)
                .attr('width', endX - startX)
                .attr('height', barHeight)
                .attr('fill', term.color)
                .attr('opacity', 0.15)
                .attr('stroke', term.color)
                .attr('stroke-width', 1)
                .attr('stroke-dasharray', '3,3');
            
            const uniqueParties = [...new Set(term.politicians.map(p => p.party))];
            const partyText = uniqueParties.slice(0, 2).join(', ') + (uniqueParties.length > 2 ? ' 외' : '');
            
            svg.append('text')
                .attr('x', startX + 5)
                .attr('y', yPos + 15)
                .style('font-size', '9px')
                .style('font-weight', 'bold')
                .attr('fill', term.color)
                .text(`${term.label}: ${partyText}`);
        }
    });
    
    // X축 그리기
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll('text')
        .style('font-size', '12px')
        .style('font-weight', 'bold');
    
    // Y축 그리기
    svg.append('g')
        .call(d3.axisLeft(y).ticks(5))
        .selectAll('text')
        .style('font-size', '11px');
    
    // 막대 그래프
    svg.selectAll('.bar')
        .data(yearlyBusiness)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', d => x(d.year))
        .attr('y', d => y(d.company_cnt))
        .attr('width', x.bandwidth())
        .attr('height', d => height - y(d.company_cnt))
        .attr('fill', '#10b981')
        .on('mouseover', function(event, d) {
            d3.select('body')
                .append('div')
                .attr('class', 'tooltip')
                .style('position', 'absolute')
                .style('background', 'white')
                .style('padding', '8px 12px')
                .style('border', '1px solid #ccc')
                .style('border-radius', '4px')
                .style('box-shadow', '0 2px 4px rgba(0,0,0,0.1)')
                .style('pointer-events', 'none')
                .style('font-size', '12px')
                .html(`
                    <div><strong>${d.year}년</strong></div>
                    <div>사업체: ${d.company_cnt.toLocaleString()}개</div>
                    <div>종사자: ${d.worker_cnt.toLocaleString()}명</div>
                `)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 10) + 'px');
        })
        .on('mouseout', function() {
            d3.selectAll('.tooltip').remove();
        });
    
    // 제목
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', -15)
        .attr('text-anchor', 'middle')
        .style('font-size', '14px')
        .style('font-weight', 'bold')
        .text('연도별 사업체 변화');
}

// 주택 그래프
function drawHousingChart() {
    const {width, height, margin} = window.currentChartSize;
    const yearlyBusiness = window.currentYearlyBusiness || [];
    const politicianTerms = window.currentPoliticianTerms || [];
    
    if (yearlyBusiness.length === 0) {
        d3.select('#chartContainer').html('<div class="text-center py-8 text-gray-500">주택 데이터 없음</div>');
        return;
    }
    
    d3.select('#chartContainer').html('');
    
    const svg = d3.select('#chartContainer')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // X축: 연도
    const x = d3.scaleBand()
        .domain(yearlyBusiness.map(d => d.year))
        .range([0, width])
        .padding(0.3);
    
    // Y축: 주택수
    const y = d3.scaleLinear()
        .domain([0, d3.max(yearlyBusiness, d => d.house_cnt) * 1.1])
        .range([height, 0]);
    
    // 정치인 임기 배경 (연도 기반)
    politicianTerms.forEach((term, idx) => {
        const termStartYear = term.startDate.getFullYear();
        const termEndYear = term.endDate.getFullYear();
        
        const years = yearlyBusiness.map(d => d.year).filter(y => y >= termStartYear && y <= termEndYear);
        
        if (years.length > 0) {
            const startX = x(years[0]);
            const endX = x(years[years.length - 1]) + x.bandwidth();
            const barHeight = height / Math.max(politicianTerms.length, 1);
            const yPos = idx * barHeight;
            
            svg.append('rect')
                .attr('x', startX)
                .attr('y', yPos)
                .attr('width', endX - startX)
                .attr('height', barHeight)
                .attr('fill', term.color)
                .attr('opacity', 0.15)
                .attr('stroke', term.color)
                .attr('stroke-width', 1)
                .attr('stroke-dasharray', '3,3');
            
            const uniqueParties = [...new Set(term.politicians.map(p => p.party))];
            const partyText = uniqueParties.slice(0, 2).join(', ') + (uniqueParties.length > 2 ? ' 외' : '');
            
            svg.append('text')
                .attr('x', startX + 5)
                .attr('y', yPos + 15)
                .style('font-size', '9px')
                .style('font-weight', 'bold')
                .attr('fill', term.color)
                .text(`${term.label}: ${partyText}`);
        }
    });
    
    // X축 그리기
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x))
        .selectAll('text')
        .style('font-size', '12px')
        .style('font-weight', 'bold');
    
    // Y축 그리기
    svg.append('g')
        .call(d3.axisLeft(y).ticks(5))
        .selectAll('text')
        .style('font-size', '11px');
    
    // 막대 그래프
    svg.selectAll('.bar')
        .data(yearlyBusiness)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('x', d => x(d.year))
        .attr('y', d => y(d.house_cnt))
        .attr('width', x.bandwidth())
        .attr('height', d => height - y(d.house_cnt))
        .attr('fill', '#8b5cf6')
        .on('mouseover', function(event, d) {
            d3.select('body')
                .append('div')
                .attr('class', 'tooltip')
                .style('position', 'absolute')
                .style('background', 'white')
                .style('padding', '8px 12px')
                .style('border', '1px solid #ccc')
                .style('border-radius', '4px')
                .style('box-shadow', '0 2px 4px rgba(0,0,0,0.1)')
                .style('pointer-events', 'none')
                .style('font-size', '12px')
                .html(`
                    <div><strong>${d.year}년</strong></div>
                    <div>주택수: ${d.house_cnt.toLocaleString()}호</div>
                `)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 10) + 'px');
        })
        .on('mouseout', function() {
            d3.selectAll('.tooltip').remove();
        });
    
    // 제목
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', -15)
        .attr('text-anchor', 'middle')
        .style('font-size', '14px')
        .style('font-weight', 'bold')
        .text('연도별 주택 변화');
}

// 함수 별칭
const loadEmdongTimeseries = loadAndRenderTimeseries;

// 전역 함수로 등록
window.loadAndRenderTimeseries = loadAndRenderTimeseries;
window.loadEmdongTimeseries = loadEmdongTimeseries;
window.loadSigunguTimeseries = loadSigunguTimeseries;

