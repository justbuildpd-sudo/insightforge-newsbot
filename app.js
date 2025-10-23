// InsightForge 웹 애플리케이션 - 개선된 디자인과 데이터 로드
// Version: 2.0.0 - Cache busting update
const API_BASE = 'https://insightforge-newsbot.vercel.app';

// 전역 변수
let allSido = [];
let allSigungu = [];
let allEmdong = [];
let expandedSidos = new Set();
let currentSelectedRegion = null;
let chartData = null;

// DOM 요소
const loadingEl = document.getElementById('loading');
const errorEl = document.getElementById('error');
const contentEl = document.getElementById('content');

// 로딩 상태 표시
function showLoading() {
    if (loadingEl) loadingEl.classList.remove('hidden');
    if (contentEl) contentEl.classList.add('hidden');
    if (errorEl) errorEl.classList.add('hidden');
}

// 에러 상태 표시
function showError(message) {
    if (errorEl) {
        errorEl.classList.remove('hidden');
        errorEl.querySelector('#errorMessage').textContent = message;
    }
    if (contentEl) contentEl.classList.add('hidden');
    if (loadingEl) loadingEl.classList.add('hidden');
}

// 콘텐츠 표시
function showContent() {
    if (contentEl) contentEl.classList.remove('hidden');
    if (loadingEl) loadingEl.classList.add('hidden');
    if (errorEl) errorEl.classList.add('hidden');
}

// API 호출 헬퍼
async function fetchAPI(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API 호출 오류:', error);
        throw error;
    }
}

// 시도 데이터 로드
async function loadSidoData() {
    try {
        console.log('📊 시도 데이터 로드 중... (v2.0.0)');
        console.log('🔗 API URL:', `${API_BASE}/api/sido`);
        const data = await fetchAPI(`${API_BASE}/api/sido`);
        
        if (data && data.sido_list) {
            allSido = data.sido_list;
            console.log(`✅ 시도 데이터 로드 완료: ${allSido.length}개`);
            renderSidoList();
        } else {
            throw new Error('시도 데이터 구조가 올바르지 않습니다.');
        }
    } catch (error) {
        console.error('❌ 시도 데이터 로드 실패:', error);
        showError(`시도 데이터 로드 실패: ${error.message}`);
    }
}

// 시도 목록 렌더링
function renderSidoList() {
    const container = document.getElementById('sido-list');
    if (!container) return;

    container.innerHTML = '';
    
    allSido.forEach(sido => {
        const sidoItem = document.createElement('div');
        sidoItem.className = 'sido-item bg-white border border-gray-200 rounded-lg p-4 mb-3 cursor-pointer hover:shadow-md transition-shadow';
        sidoItem.innerHTML = `
            <div class="flex justify-between items-center">
                <div>
                    <h3 class="text-lg font-semibold text-gray-800">${sido.sido_name}</h3>
                    <p class="text-sm text-gray-600">${sido.total_regions}개 지역</p>
                </div>
                <div class="text-gray-400">
                    <svg class="w-5 h-5 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                    </svg>
                </div>
            </div>
        `;
        
        sidoItem.addEventListener('click', () => toggleSido(sido.code));
        container.appendChild(sidoItem);
    });
}

// 시도 토글
async function toggleSido(sidoCode) {
    const sido = allSido.find(s => s.code === sidoCode);
    if (!sido) return;

    if (expandedSidos.has(sidoCode)) {
        // 접기
        expandedSidos.delete(sidoCode);
        const container = document.getElementById(`sido-${sidoCode}`);
        if (container) {
            container.remove();
        }
    } else {
        // 펼치기
        expandedSidos.add(sidoCode);
        await loadSigunguList(sido.name);
    }
}

// 시군구 데이터 로드
async function loadSigunguList(sidoName) {
    try {
        console.log(`📊 ${sidoName} 시군구 데이터 로드 중...`);
        const data = await fetchAPI(`${API_BASE}/api/sido/${encodeURIComponent(sidoName)}`);
        
        if (data && data.sigungu_list) {
            console.log(`✅ ${sidoName} 시군구 데이터 로드 완료: ${data.sigungu_list.length}개`);
            renderSigunguList(sidoName, data.sigungu_list);
        } else {
            throw new Error(`${sidoName} 시군구 데이터를 찾을 수 없습니다.`);
        }
    } catch (error) {
        console.error(`❌ ${sidoName} 시군구 데이터 로드 실패:`, error);
        showError(`${sidoName} 시군구 데이터 로드 실패: ${error.message}`);
    }
}

// 시군구 목록 렌더링
function renderSigunguList(sidoName, sigunguList) {
    const sidoCode = allSido.find(s => s.name === sidoName)?.code;
    if (!sidoCode) return;

    const container = document.createElement('div');
    container.id = `sido-${sidoCode}`;
    container.className = 'sigungu-container ml-6 mt-2';
    
    let html = '<div class="space-y-2">';
    sigunguList.forEach(sigungu => {
        const pop = sigungu.total_population || 0;
        const popText = pop > 0 ? `${(pop / 1000).toFixed(1)}천` : '-';
        
        html += `
            <div class="sigungu-item bg-gray-50 border border-gray-200 rounded-lg p-3 cursor-pointer hover:bg-gray-100 transition-colors"
                 onclick="toggleSigungu('${sidoCode}', '${sigungu.sigungu_code}')">
                <div class="flex justify-between items-center">
                    <div>
                        <h4 class="font-medium text-gray-800">${sigungu.sigungu_name}</h4>
                        <p class="text-sm text-gray-600">${sigungu.emdong_count}개 동</p>
                    </div>
                    <div class="text-right">
                        <span class="text-sm text-gray-500">${popText}</span>
                        <div class="text-gray-400">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                            </svg>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
    
    // 시도 항목 뒤에 삽입
    const sidoItems = document.querySelectorAll('.sido-item');
    const currentSidoItem = Array.from(sidoItems).find(item => 
        item.textContent.includes(sidoName)
    );
    
    if (currentSidoItem) {
        currentSidoItem.parentNode.insertBefore(container, currentSidoItem.nextSibling);
    }
}

// 시군구 토글
async function toggleSigungu(sidoCode, sigunguCode) {
    const container = document.getElementById(`sigungu-${sigunguCode}`);
    if (container) {
        // 이미 로드된 경우 토글
        if (container.style.display === 'none') {
            container.style.display = 'block';
        } else {
            container.style.display = 'none';
        }
        return;
    }

    // 동 데이터 로드
    await loadEmdongList(sigunguCode);
}

// 동 데이터 로드
async function loadEmdongList(sigunguCode) {
    try {
        // 현재 선택된 시도 찾기
        const currentSido = allSido.find(s => expandedSidos.has(s.code));
        if (!currentSido) return;
        
        console.log(`📊 ${currentSido.name} 동 데이터 로드 중...`);
        
        // 시도 데이터 다시 가져오기
        const data = await fetchAPI(`${API_BASE}/api/sido/${encodeURIComponent(currentSido.name)}`);
        
        if (!data || !data.regions) {
            throw new Error('지역 데이터를 찾을 수 없습니다.');
        }
        
        // regions를 배열로 변환
        const regionsArray = Object.entries(data.regions).map(([code, regionData]) => ({
            code: code,
            ...regionData
        }));
        
        // 해당 시군구의 동 목록 필터링
        const emdongList = regionsArray.filter(region => {
            return region.sigungu_name && region.code.substring(0, 5) === sigunguCode.substring(0, 5);
        }).sort((a, b) => (a.emdong_name || '').localeCompare(b.emdong_name || ''));
        
        console.log(`✅ 동 데이터 로드 완료: ${emdongList.length}개`);
        renderEmdongList(sigunguCode, emdongList);
        
    } catch (error) {
        console.error('❌ 동 데이터 로드 실패:', error);
        showError(`동 데이터 로드 실패: ${error.message}`);
    }
}

// 동 목록 렌더링
function renderEmdongList(sigunguCode, emdongList) {
    const container = document.createElement('div');
    container.id = `sigungu-${sigunguCode}`;
    container.className = 'emdong-container ml-6 mt-2';
    
    let html = '<div class="space-y-1">';
    emdongList.forEach(emdong => {
        const pop = emdong.population || 0;
        const popText = pop > 0 ? `${(pop / 1000).toFixed(1)}천` : '-';
        const displayName = [emdong.sigungu_name, emdong.emdong_name].filter(x => x && x !== '계').join(' ');
        
        html += `
            <div class="emdong-item p-2 hover:bg-blue-50 rounded cursor-pointer border border-gray-100 text-sm transition-colors"
                 onclick='selectRegion("${emdong.code}")'>
                <div class="flex justify-between items-center">
                    <span class="text-gray-700">${displayName}</span>
                    <span class="text-xs text-gray-500">${popText}</span>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
    
    // 시군구 항목 뒤에 삽입
    const sigunguItem = document.querySelector(`[onclick*="${sigunguCode}"]`);
    if (sigunguItem) {
        sigunguItem.parentNode.insertBefore(container, sigunguItem.nextSibling);
    }
}

// 지역 선택
function selectRegion(regionCode) {
    console.log(`📍 지역 선택: ${regionCode}`);
    currentSelectedRegion = regionCode;
    
    // 선택된 지역 하이라이트
    document.querySelectorAll('.region-selected').forEach(el => {
        el.classList.remove('region-selected');
    });
    
    const selectedElement = document.querySelector(`[onclick*="${regionCode}"]`);
    if (selectedElement) {
        selectedElement.classList.add('region-selected', 'bg-blue-100', 'border-blue-300');
    }
    
    // 차트 데이터 로드
    loadChartData(regionCode);
}

// 차트 데이터 로드
async function loadChartData(regionCode) {
    try {
        console.log(`📊 ${regionCode} 차트 데이터 로드 중...`);
        
        // 인구 데이터 로드
        const populationData = await fetchAPI(`${API_BASE}/api/population/monthly`);
        
        if (populationData && populationData.regions && populationData.regions[regionCode]) {
            const regionData = populationData.regions[regionCode];
            console.log(`✅ ${regionCode} 차트 데이터 로드 완료`);
            
            // 차트 렌더링
            renderTimeseriesChart(regionData, regionCode);
        } else {
            throw new Error(`${regionCode} 지역 데이터를 찾을 수 없습니다.`);
        }
    } catch (error) {
        console.error(`❌ ${regionCode} 차트 데이터 로드 실패:`, error);
        showError(`차트 데이터 로드 실패: ${error.message}`);
    }
}

// 시계열 차트 렌더링
function renderTimeseriesChart(regionData, regionCode) {
    const container = document.getElementById('chart-container');
    if (!container) return;

    // 기존 차트 제거
    container.innerHTML = '';
    
    // 차트 데이터 준비
    const years = Object.keys(regionData).sort();
    const data = years.map(year => ({
        year: parseInt(year),
        population: regionData[year] || 0
    }));

    // D3.js 차트 생성
    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const width = 800 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select(container)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // 스케일 설정
    const xScale = d3.scaleLinear()
        .domain(d3.extent(data, d => d.year))
        .range([0, width]);

    const yScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.population)])
        .range([height, 0]);

    // 라인 생성
    const line = d3.line()
        .x(d => xScale(d.year))
        .y(d => yScale(d.population))
        .curve(d3.curveMonotoneX);

    // 축 생성
    g.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(xScale).tickFormat(d3.format('d')));

    g.append('g')
        .call(d3.axisLeft(yScale).tickFormat(d3.format('.0s')));

    // 라인 그리기
    g.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', '#3b82f6')
        .attr('stroke-width', 2)
        .attr('d', line);

    // 점 그리기
    g.selectAll('.dot')
        .data(data)
        .enter().append('circle')
        .attr('class', 'dot')
        .attr('cx', d => xScale(d.year))
        .attr('cy', d => yScale(d.population))
        .attr('r', 4)
        .attr('fill', '#3b82f6')
        .on('mouseover', function(event, d) {
            // 툴팁 표시
            d3.select(this).attr('r', 6);
        })
        .on('mouseout', function(event, d) {
            d3.select(this).attr('r', 4);
        });

    // 제목 추가
    g.append('text')
        .attr('x', width / 2)
        .attr('y', -10)
        .attr('text-anchor', 'middle')
        .style('font-size', '16px')
        .style('font-weight', 'bold')
        .text(`${regionCode} 인구 변화`);

    console.log('✅ 차트 렌더링 완료');
}

// 초기화
async function init() {
    showLoading();
    
    try {
        await loadSidoData();
        showContent();
    } catch (error) {
        showError(`초기화 실패: ${error.message}`);
    }
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', init);
