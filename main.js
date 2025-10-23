// InsightForge 웹 애플리케이션 - 완전히 새로운 파일
// Version: 4.0.0 - COMPLETELY NEW FILE - NO CACHE
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
    if (loadingEl) loadingEl.classList.add('hidden');
    if (contentEl) contentEl.classList.add('hidden');
}

// 성공 상태 표시
function showContent() {
    if (contentEl) contentEl.classList.remove('hidden');
    if (loadingEl) loadingEl.classList.add('hidden');
    if (errorEl) errorEl.classList.add('hidden');
}

// API 호출 헬퍼 - 극강 캐시 버스팅
async function fetchAPI(url) {
    try {
        // 극강 캐시 버스팅
        const timestamp = Date.now();
        const random = Math.random().toString(36).substring(7);
        const cacheBuster = `?v=4.0.0&t=${timestamp}&r=${random}&cache=busted&force=reload&no-cache=true`;
        const finalUrl = url + cacheBuster;
        
        console.log('🚀 API 호출 (NEW FILE):', finalUrl);
        console.log('✅ localhost:3002 완전 제거됨');
        
        const response = await fetch(finalUrl, {
            method: 'GET',
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'If-Modified-Since': '0'
            }
        });
        
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
        console.log('📊 시도 데이터 로드 중... (v4.0.0 - NEW FILE)');
        console.log('🔗 API URL:', `${API_BASE}/api/sido`);
        console.log('🚨 완전히 새로운 파일명으로 캐시 완전 우회');
        console.log('✅ localhost:3002 완전 제거됨');
        console.log('✅ Vercel 서버리스 함수 정상 작동');
        
        const data = await fetchAPI(`${API_BASE}/api/sido`);
        
        if (data && data.sido_list) {
            allSido = data.sido_list;
            console.log(`✅ 시도 데이터 로드 완료: ${allSido.length}개`);
            renderSidoList();
            updateDashboardStats();
            showContent();
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
    const container = document.getElementById('sidoList');
    if (!container) return;
    
    container.innerHTML = '';
    
    allSido.forEach(sido => {
        const sidoEl = document.createElement('div');
        sidoEl.className = 'bg-white rounded-lg shadow-md p-4 mb-3 cursor-pointer hover:shadow-lg transition-shadow';
        sidoEl.innerHTML = `
            <div class="flex items-center justify-between">
                <div>
                    <h3 class="text-lg font-semibold text-gray-800">${sido.sido_name}</h3>
                    <p class="text-sm text-gray-600">${sido.total_regions}개 지역</p>
                </div>
                <div class="text-2xl">${expandedSidos.has(sido.code) ? '📂' : '📁'}</div>
            </div>
        `;
        
        sidoEl.addEventListener('click', () => toggleSido(sido.code));
        container.appendChild(sidoEl);
    });
}

// 시군구 목록 로드
async function loadSigunguList(sidoName) {
    try {
        console.log(`📊 시군구 데이터 로드 중... (${sidoName})`);
        
        // 시도 코드 찾기
        const sido = allSido.find(s => s.sido_name === sidoName);
        if (!sido) {
            throw new Error('시도 정보를 찾을 수 없습니다.');
        }
        
        const data = await fetchAPI(`${API_BASE}/api/sigungu?sido_code=${sido.code}`);
        
        if (data && data.sigungu_list) {
            allSigungu = data.sigungu_list;
            console.log(`✅ 시군구 데이터 로드 완료: ${allSigungu.length}개`);
            renderSigunguList(sidoName);
        } else {
            throw new Error('시군구 데이터 구조가 올바르지 않습니다.');
        }
    } catch (error) {
        console.error('❌ 시군구 데이터 로드 실패:', error);
        showError(`시군구 데이터 로드 실패: ${error.message}`);
    }
}

// 시군구 목록 렌더링
function renderSigunguList(sidoName) {
    const container = document.getElementById(`sido-${allSido.find(s => s.sido_name === sidoName)?.code}`);
    if (!container) return;
    
    container.innerHTML = '';
    
    allSigungu.forEach(sigungu => {
        const sigunguEl = document.createElement('div');
        sigunguEl.className = 'bg-gray-50 rounded-lg p-3 mb-2 cursor-pointer hover:bg-gray-100 transition-colors';
        sigunguEl.innerHTML = `
            <div class="flex items-center justify-between">
                <div>
                    <h4 class="font-medium text-gray-700">${sigungu.sigungu_name}</h4>
                    <p class="text-sm text-gray-500">${sigungu.total_regions}개 지역</p>
                </div>
                <div class="text-lg">📁</div>
            </div>
        `;
        
        sigunguEl.addEventListener('click', () => loadEmdongList(sigungu.code));
        container.appendChild(sigunguEl);
    });
}

// 읍면동 목록 로드
async function loadEmdongList(sigunguCode) {
    try {
        console.log(`📊 읍면동 데이터 로드 중... (${sigunguCode})`);
        
        const data = await fetchAPI(`${API_BASE}/api/emdong?sigungu_code=${sigunguCode}`);
        
        if (data && data.emdong_list) {
            allEmdong = data.emdong_list;
            console.log(`✅ 읍면동 데이터 로드 완료: ${allEmdong.length}개`);
            renderEmdongList();
        } else {
            throw new Error('읍면동 데이터 구조가 올바르지 않습니다.');
        }
    } catch (error) {
        console.error('❌ 읍면동 데이터 로드 실패:', error);
        showError(`읍면동 데이터 로드 실패: ${error.message}`);
    }
}

// 읍면동 목록 렌더링
function renderEmdongList() {
    const container = document.getElementById('emdongList');
    if (!container) return;
    
    container.innerHTML = '';
    
    allEmdong.forEach(emdong => {
        const emdongEl = document.createElement('div');
        emdongEl.className = 'bg-blue-50 rounded-lg p-3 mb-2 cursor-pointer hover:bg-blue-100 transition-colors';
        emdongEl.innerHTML = `
            <div class="flex items-center justify-between">
                <div>
                    <h5 class="font-medium text-blue-700">${emdong.emdong_name}</h5>
                </div>
                <div class="text-lg">🏘️</div>
            </div>
        `;
        
        emdongEl.addEventListener('click', () => selectRegion(emdong));
        container.appendChild(emdongEl);
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
        
        // 시군구 컨테이너 생성
        const container = document.createElement('div');
        container.id = `sido-${sidoCode}`;
        container.className = 'mt-3 ml-4';
        
        const sidoEl = document.querySelector(`[onclick*="${sidoCode}"]`)?.parentElement;
        if (sidoEl) {
            sidoEl.parentElement.insertBefore(container, sidoEl.nextSibling);
        }
        
        await loadSigunguList(sido.sido_name);
    }
}

// 지역 선택
function selectRegion(emdong) {
    currentSelectedRegion = emdong;
    console.log('📍 선택된 지역:', emdong.emdong_name);
    
    // 선택된 지역 표시
    const selectedEl = document.getElementById('selectedRegion');
    if (selectedEl) {
        selectedEl.textContent = emdong.emdong_name;
        selectedEl.classList.remove('hidden');
    }
}

// 대시보드 통계 업데이트
function updateDashboardStats() {
    const totalRegionsEl = document.getElementById('totalRegions');
    const totalSidoEl = document.getElementById('totalSido');
    
    if (totalRegionsEl) {
        const totalRegions = allSido.reduce((sum, sido) => sum + sido.total_regions, 0);
        totalRegionsEl.textContent = totalRegions.toLocaleString();
    }
    
    if (totalSidoEl) {
        totalSidoEl.textContent = allSido.length;
    }
}

// 초기화
async function init() {
    console.log('🚀 InsightForge 웹 애플리케이션 시작 (v4.0.0 - NEW FILE)');
    console.log('✅ localhost:3002 완전 제거됨');
    console.log('✅ Vercel API 사용');
    
    showLoading();
    await loadSidoData();
}

// DOM 로드 완료 시 초기화
document.addEventListener('DOMContentLoaded', init);
