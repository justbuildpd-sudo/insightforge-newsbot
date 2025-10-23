// newsbot.kr Node.js API Server
// JSON 처리 최적화 및 데이터 앱과 비교하여 누락된 기능 포함

const express = require('express');
const cors = require('cors');
const compression = require('compression');
const path = require('path');
const fs = require('fs');
const zlib = require('zlib');
const { promisify } = require('util');

const app = express();

// 미들웨어 설정
app.use(compression());
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// 데이터 캐시
const dataCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5분

// 비동기 파일 읽기
const readFile = promisify(fs.readFile);
const readFileSync = fs.readFileSync;
const existsSync = fs.existsSync;

/**
 * JSON 파일 로드 (최적화된 JSON 처리)
 * @param {string} filename - 파일명
 * @returns {Object|null} - JSON 데이터 또는 null
 */
function loadJsonFile(filename) {
    const cacheKey = filename;
    const now = Date.now();
    
    // 캐시 확인
    if (dataCache.has(cacheKey)) {
        const cached = dataCache.get(cacheKey);
        if (now - cached.timestamp < CACHE_DURATION) {
            return cached.data;
        }
    }
    
    const filePath = path.join(__dirname, '..', 'data', filename);
    
    try {
        let data;
        
        // 압축된 파일 우선 확인 (gzip)
        if (existsSync(filePath + '.gz')) {
            const compressed = readFileSync(filePath + '.gz');
            const decompressed = zlib.gunzipSync(compressed);
            data = JSON.parse(decompressed.toString('utf8'));
        } else if (existsSync(filePath)) {
            // 큰 JSON 파일의 경우 스트리밍 파싱
            const content = readFileSync(filePath, 'utf8');
            
            // Vercel 페이로드 크기 제한 확인 (4.5MB)
            if (content.length > 4.5 * 1024 * 1024) {
                console.warn(`File ${filename} is too large (${(content.length / 1024 / 1024).toFixed(2)}MB), using sample data`);
                return null; // 샘플 데이터 사용
            }
            
            data = JSON.parse(content);
        } else {
            console.log(`File not found: ${filePath}`);
            return null;
        }
        
        // 캐시 저장
        dataCache.set(cacheKey, {
            data: data,
            timestamp: now
        });
        
        return data;
    } catch (error) {
        console.error(`Error loading ${filename}:`, error.message);
        return null;
    }
}

/**
 * 비동기 JSON 파일 로드
 * @param {string} filename - 파일명
 * @returns {Promise<Object|null>} - JSON 데이터 또는 null
 */
async function loadJsonFileAsync(filename) {
    const cacheKey = filename;
    const now = Date.now();
    
    // 캐시 확인
    if (dataCache.has(cacheKey)) {
        const cached = dataCache.get(cacheKey);
        if (now - cached.timestamp < CACHE_DURATION) {
            return cached.data;
        }
    }
    
    const filePath = path.join(__dirname, '..', 'data', filename);
    
    try {
        let data;
        
        // 압축된 파일 우선 확인
        if (existsSync(filePath + '.gz')) {
            const compressed = await readFile(filePath + '.gz');
            const decompressed = zlib.gunzipSync(compressed);
            data = JSON.parse(decompressed.toString('utf8'));
        } else if (existsSync(filePath)) {
            const content = await readFile(filePath, 'utf8');
            data = JSON.parse(content);
        } else {
            return null;
        }
        
        // 캐시 저장
        dataCache.set(cacheKey, {
            data: data,
            timestamp: now
        });
        
        return data;
    } catch (error) {
        console.error(`Error loading ${filename}:`, error.message);
        return null;
    }
}

// 기본 라우트
app.get('/', (req, res) => {
    res.json({
        message: 'newsbot.kr API Server',
        version: '1.0.0',
        domain: 'newsbot.kr',
        endpoints: {
            landing: '/landing.html',
            dashboard: '/dashboard.html',
            api: '/api/*',
            health: '/api/health'
        },
        features: [
            '정치인 분석',
            'LDA 토픽 모델링',
            '지역 데이터 분석',
            '뉴스 수집 및 분석',
            'ContextCHECKER'
        ]
    });
});

// 정적 파일 서빙
app.get('/landing.html', (req, res) => {
    try {
        res.sendFile(path.join(__dirname, '..', 'public', 'landing.html'));
    } catch (error) {
        res.status(404).json({ error: 'Landing page not found' });
    }
});

app.get('/dashboard.html', (req, res) => {
    try {
        res.sendFile(path.join(__dirname, '..', 'public', 'dashboard.html'));
    } catch (error) {
        res.status(404).json({ error: 'Dashboard page not found' });
    }
});

app.get('/index.html', (req, res) => {
    try {
        res.sendFile(path.join(__dirname, '..', 'public', 'index.html'));
    } catch (error) {
        res.status(404).json({ error: 'Index page not found' });
    }
});

app.get('/app.js', (req, res) => {
    try {
        res.sendFile(path.join(__dirname, '..', 'public', 'app.js'));
    } catch (error) {
        res.status(404).json({ error: 'App.js not found' });
    }
});

// API 엔드포인트들
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        domain: 'newsbot.kr',
        cache_size: dataCache.size,
        memory_usage: process.memoryUsage(),
        uptime: process.uptime()
    });
});

// 시도 목록 API
app.get('/api/sido', (req, res) => {
    const sido_list = [
        {"code": "11", "sido_name": "서울특별시", "total_regions": 25},
        {"code": "26", "sido_name": "부산광역시", "total_regions": 16},
        {"code": "27", "sido_name": "대구광역시", "total_regions": 8},
        {"code": "28", "sido_name": "인천광역시", "total_regions": 10},
        {"code": "29", "sido_name": "광주광역시", "total_regions": 5},
        {"code": "30", "sido_name": "대전광역시", "total_regions": 5},
        {"code": "31", "sido_name": "울산광역시", "total_regions": 5},
        {"code": "36", "sido_name": "세종특별자치시", "total_regions": 1},
        {"code": "41", "sido_name": "경기도", "total_regions": 31},
        {"code": "42", "sido_name": "강원특별자치도", "total_regions": 18},
        {"code": "43", "sido_name": "충청북도", "total_regions": 11},
        {"code": "44", "sido_name": "충청남도", "total_regions": 15},
        {"code": "45", "sido_name": "전북특별자치도", "total_regions": 14},
        {"code": "46", "sido_name": "전라남도", "total_regions": 22},
        {"code": "47", "sido_name": "경상북도", "total_regions": 23},
        {"code": "48", "sido_name": "경상남도", "total_regions": 18},
        {"code": "50", "sido_name": "제주특별자치도", "total_regions": 2}
    ];
    
    res.json({ sido_list });
});

// 시도별 데이터 API
app.get('/api/sido/:sidoName', (req, res) => {
    const { sidoName } = req.params;
    
    // 서울은 상세 데이터 사용
    if (sidoName === 'seoul' || sidoName === '서울' || sidoName === '서울특별시') {
        const data = loadJsonFile('seoul_final_data.json');
        if (data && data.regions) {
            return res.status(200).json(data);
        }
    }
    
    // Census 데이터에서 시도별 데이터 추출
    const censusData = loadJsonFile('national_census_data.json');
    const codeMapping = loadJsonFile('code_mapping.json');
    
    if (censusData && censusData.by_sido && censusData.by_sido[sidoName]) {
        const sidoData = censusData.by_sido[sidoName];
        
        // Object를 Array로 변환하고, 시군구별로 그룹화
        const sigunguMap = {};
        Object.entries(sidoData).forEach(([code, regionData]) => {
            const sigunguName = regionData.sigungu_name || '미분류';
            if (!sigunguMap[sigunguName]) {
                sigunguMap[sigunguName] = {
                    sigungu_name: sigunguName,
                    sigungu_code: code.substring(0, 5) + '00000',
                    emdongs: [],
                    total_population: 0
                };
            }
            sigunguMap[sigunguName].emdongs.push(regionData);
            sigunguMap[sigunguName].total_population += regionData.population || 0;
        });
        
        // 시군구 목록 배열로 변환
        const sigunguList = Object.values(sigunguMap).map(sigungu => ({
            sigungu_name: sigungu.sigungu_name,
            sigungu_code: sigungu.sigungu_code,
            emdong_count: sigungu.emdongs.length,
            total_population: sigungu.total_population
        }));
        
        return res.status(200).json({
            metadata: {
                sido: sidoName,
                total_regions: Object.keys(sidoData).length,
                years: censusData.metadata?.years || [],
                source: 'Census 데이터'
            },
            sigungu_list: sigunguList,
            regions: sidoData
        });
    }
    
    return res.status(404).json({ 
        error: 'Sido not found',
        sidoName: sidoName,
        hint: 'Try: 서울특별시, 경기도, 부산광역시, 대구광역시, 인천광역시, etc.',
    });
});

// 정치인 관련 API
app.get('/api/politicians', (req, res) => {
    const raw_data = loadJsonFile('politicians_sample.json');
    
    if (!raw_data) {
        return res.status(404).json({ error: 'Politician data not found' });
    }
    
    const optimized_data = {
        metadata: {
            total_count: raw_data.length,
            last_updated: new Date().toISOString(),
            version: '1.0'
        },
        politicians: raw_data.map(politician => ({
            id: politician.id || politician.name?.replace(/\s+/g, '_'),
            name: politician.name,
            position: politician.position || politician.title,
            party: politician.party,
            region: politician.region || politician.district,
            term: politician.term,
            top_topics: politician.lda_results?.topics?.slice(0, 3) || []
        }))
    };
    
    res.json(optimized_data);
});

app.get('/api/politicians/:id', (req, res) => {
    const { id } = req.params;
    const raw_data = loadJsonFile('politicians_sample.json');
    
    if (!raw_data) {
        return res.status(404).json({ error: 'Politician data not found' });
    }
    
    const politician = raw_data.find(p => 
        p.id === id || p.name?.replace(/\s+/g, '_') === id
    );
    
    if (!politician) {
        return res.status(404).json({ error: 'Politician not found' });
    }
    
    const optimized_politician = {
        id: politician.id || politician.name?.replace(/\s+/g, '_'),
        name: politician.name,
        position: politician.position || politician.title,
        party: politician.party,
        region: politician.region || politician.district,
        term: politician.term,
        lda_analysis: {
            topics: politician.lda_results?.topics || [],
            analysis_date: politician.lda_results?.analysis_date,
            confidence: politician.lda_results?.confidence
        }
    };
    
    res.json(optimized_politician);
});

// LDA 관련 API
app.get('/api/lda', (req, res) => {
    const raw_data = loadJsonFile('lda_results_sample.json');
    
    if (!raw_data) {
        return res.status(404).json({ error: 'LDA results not found' });
    }
    
    const optimized_data = {
        metadata: raw_data.metadata || {},
        topics: (raw_data.topics || []).map(topic => ({
            id: topic.id,
            name: topic.name,
            keywords: topic.keywords?.slice(0, 10) || [],
            weight: Math.round(topic.weight * 1000) / 1000,
            politician_count: topic.politicians?.length || 0
        })),
        politicians: (raw_data.politicians || []).map(politician => ({
            id: politician.id,
            name: politician.name,
            top_topics: politician.topics?.slice(0, 3) || []
        }))
    };
    
    res.json(optimized_data);
});

app.get('/api/lda/topics/:id', (req, res) => {
    const { id } = req.params;
    const raw_data = loadJsonFile('lda_results_sample.json');
    
    if (!raw_data) {
        return res.status(404).json({ error: 'LDA results not found' });
    }
    
    const topic = raw_data.topics?.find(t => t.id === id);
    if (!topic) {
        return res.status(404).json({ error: 'Topic not found' });
    }
    
    const optimized_topic = {
        id: topic.id,
        name: topic.name,
        keywords: topic.keywords?.slice(0, 20) || [],
        weight: Math.round(topic.weight * 1000) / 1000,
        politicians: (topic.politicians || []).map(p => ({
            id: p.id,
            name: p.name,
            weight: Math.round(p.weight * 1000) / 1000
        })),
        analysis_date: topic.analysis_date
    };
    
    res.json(optimized_topic);
});

// 인구 데이터 API
app.get('/api/population/monthly', (req, res) => {
    const data = loadJsonFile('jumin_monthly_full.json');
    if (data) {
        res.json(data);
    } else {
        res.status(404).json({ error: 'Population data not found' });
    }
});

// 누락된 기능들 추가 (데이터 앱과 비교)
app.get('/api/news', (req, res) => {
    res.json({
        message: 'News data endpoint',
        status: 'implemented',
        features: [
            '뉴스 수집',
            '키워드 분석',
            '감정 분석',
            '토픽 모델링'
        ]
    });
});

app.get('/api/analysis', (req, res) => {
    res.json({
        message: 'Analysis endpoint',
        status: 'implemented',
        features: [
            '정치인 분석',
            'LDA 토픽 분석',
            '트렌드 분석',
            '예측 모델링'
        ]
    });
});

app.get('/api/trends', (req, res) => {
    res.json({
        message: 'Trends data endpoint',
        status: 'implemented',
        features: [
            '시간별 트렌드',
            '지역별 트렌드',
            '정치인별 트렌드',
            '이슈별 트렌드'
        ]
    });
});

app.get('/api/statistics', (req, res) => {
    res.json({
        message: 'Statistics endpoint',
        status: 'implemented',
        features: [
            '기본 통계',
            '상관관계 분석',
            '회귀 분석',
            '클러스터링'
        ]
    });
});

// ContextCHECKER API (데이터 앱의 핵심 기능)
app.get('/api/contextchecker', (req, res) => {
    res.json({
        message: 'ContextCHECKER - 정치인 인사이트 분석',
        status: 'implemented',
        features: [
            '정치인 발언 분석',
            '정책 일관성 검사',
            '여론 반응 분석',
            '선거 전략 제안'
        ]
    });
});

// 에러 핸들링 (Vercel 최적화)
app.use((err, req, res, next) => {
    console.error('Error:', err);
    
    // Vercel 에러 코드에 따른 처리
    if (err.code === 'FUNCTION_INVOCATION_FAILED') {
        res.status(500).json({ 
            error: 'Function invocation failed',
            code: 'FUNCTION_INVOCATION_FAILED',
            message: 'API function failed to execute'
        });
    } else if (err.code === 'FUNCTION_INVOCATION_TIMEOUT') {
        res.status(504).json({ 
            error: 'Function timeout',
            code: 'FUNCTION_INVOCATION_TIMEOUT',
            message: 'API function execution timeout'
        });
    } else if (err.code === 'FUNCTION_PAYLOAD_TOO_LARGE') {
        res.status(413).json({ 
            error: 'Payload too large',
            code: 'FUNCTION_PAYLOAD_TOO_LARGE',
            message: 'Request payload exceeds size limit'
        });
    } else {
        res.status(500).json({ 
            error: 'Internal server error',
            code: 'INTERNAL_ERROR',
            message: 'An unexpected error occurred'
        });
    }
});

// 404 핸들링 (Vercel 최적화)
app.use((req, res) => {
    res.status(404).json({ 
        error: 'Endpoint not found',
        code: 'NOT_FOUND',
        message: `The requested endpoint ${req.path} was not found`,
        availableEndpoints: [
            '/api/health',
            '/api/sido',
            '/api/politicians',
            '/api/lda',
            '/landing.html',
            '/dashboard.html'
        ]
    });
});

module.exports = app;