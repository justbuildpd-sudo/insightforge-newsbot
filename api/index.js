const fs = require('fs');
const path = require('path');
const zlib = require('zlib');
const https = require('https');

// 데이터 디렉토리
const DATA_DIR = path.join(process.cwd(), 'insightforge-web', 'data');

// 네이버 API 키 (Vercel 환경변수 사용)
const NAVER_CLIENT_ID = process.env.NAVER_CLIENT_ID || 'ULDLTGiPvrrPBgbuydSm';
const NAVER_CLIENT_SECRET = process.env.NAVER_CLIENT_SECRET || 'uO5mu7UQBg';

// 캐시
const dataCache = {};

// 에러 저장용
const loadErrors = {};

// JSON 파일 로드 (gzip 지원)
function loadJsonFile(filename) {
    if (dataCache[filename]) {
        return dataCache[filename];
    }
    
    try {
        // 일반 파일 먼저 시도
        const filePath = path.join(DATA_DIR, filename);
        
        if (fs.existsSync(filePath)) {
            const fileContent = fs.readFileSync(filePath, 'utf-8');
            const data = JSON.parse(fileContent);
            dataCache[filename] = data;
            delete loadErrors[filename]; // 성공 시 에러 제거
            return data;
        }
        
        // gzip 파일 시도
        const gzPath = path.join(DATA_DIR, filename + '.gz');
        if (fs.existsSync(gzPath)) {
            const compressed = fs.readFileSync(gzPath);
            const decompressed = zlib.gunzipSync(compressed);
            const data = JSON.parse(decompressed.toString('utf-8'));
            dataCache[filename] = data;
            delete loadErrors[filename];
            return data;
        }
        
        loadErrors[filename] = 'File not found';
        return null;
    } catch (error) {
        loadErrors[filename] = `${error.name}: ${error.message}`;
        return null;
    }
}

// CORS 헤더
const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
};

// 메인 핸들러
module.exports = (req, res) => {
    // CORS preflight
    if (req.method === 'OPTIONS') {
        return res.status(200).json({});
    }
    
    // Set CORS headers
    Object.entries(corsHeaders).forEach(([key, value]) => {
        res.setHeader(key, value);
    });
    
    const url = req.url || '/';
    
    try {
        // Debug endpoint
        if (url.match(/\/api\/debug/)) {
            const allFiles = fs.existsSync(DATA_DIR) ? fs.readdirSync(DATA_DIR) : [];
            return res.status(200).json({
                cwd: process.cwd(),
                dataDir: DATA_DIR,
                dataDirExists: fs.existsSync(DATA_DIR),
                totalFiles: allFiles.length,
                files: allFiles,
                seoulExists: fs.existsSync(path.join(DATA_DIR, 'seoul_final_data.json'))
            });
        }
        
        // /api/politicians/si_uiwon
        if (url.match(/\/api\/politicians\/si_uiwon/)) {
            const data = loadJsonFile('seoul_si_uiwon_8th.json');
            return res.status(200).json(data || {});
        }
        
        // /api/politicians/gu_uiwon
        if (url.match(/\/api\/politicians\/gu_uiwon/)) {
            const data = loadJsonFile('seoul_gu_uiwon_8th.json');
            return res.status(200).json(data || {});
        }
        
        // /api/politicians/national_assembly
        if (url.match(/\/api\/politicians\/national_assembly/)) {
            const data = loadJsonFile('national_assembly_22nd.json');
            if (data && typeof data === 'object' && !Array.isArray(data)) {
                const politicians = [];
                for (const [region, pols] of Object.entries(data)) {
                    if (Array.isArray(pols)) {
                        politicians.push(...pols);
                    }
                }
                return res.status(200).json(politicians);
            }
            return res.status(200).json(data || []);
        }
        
        // /api/politicians/gu_mayor - 구청장 정보
        if (url.match(/\/api\/politicians\/gu_mayor/)) {
            const data = loadJsonFile('seoul_gu_mayor_8th.json');
            return res.status(200).json(data || {});
        }
        
        // /api/politicians/mayor - 시장 정보
        if (url.match(/\/api\/politicians\/mayor/)) {
            const data = loadJsonFile('seoul_mayor_8th.json');
            return res.status(200).json(data || {});
        }
        
        // /api/politicians/assembly_by_region - 지역구/비례대표 구분
        if (url.match(/\/api\/politicians\/assembly_by_region/)) {
            const data = loadJsonFile('assembly_by_region.json');
            return res.status(200).json(data || {});
        }
        
        // /api/election/previous - 역사적 선거 데이터
        if (url.match(/\/api\/election\/previous$/)) {
            const data = loadJsonFile('previous_election_data_complete.json');
            return res.status(200).json(data || {});
        }
        
        // /api/election/previous/<region> - 지역별 역사적 선거
        const prevElectionMatch = url.match(/\/api\/election\/previous\/([^/]+)/);
        if (prevElectionMatch) {
            const region = decodeURIComponent(prevElectionMatch[1]);
            const data = loadJsonFile('previous_election_data_complete.json');
            
            if (data && data[region]) {
                return res.status(200).json({
                    region: region,
                    elections: data[region]
                });
            }
            
            return res.status(404).json({ error: 'Previous election data not found', region: region });
        }
        
        // /api/population/yearly
        if (url.match(/\/api\/population\/yearly$/)) {
            const data = loadJsonFile('population_yearly_data.json');
            return res.status(200).json(data || {});
        }
        
        // /api/population/yearly/<year>
        const yearMatch = url.match(/\/api\/population\/yearly\/(\d+)/);
        if (yearMatch) {
            const year = yearMatch[1];
            const data = loadJsonFile('population_yearly_data.json');
            if (data && data[year]) {
                return res.status(200).json(data[year]);
            }
            return res.status(404).json({ error: 'Year not found' });
        }
        
        // /api/population/region/<region_name>
        const regionMatch = url.match(/\/api\/population\/region\/([^/]+)/);
        if (regionMatch) {
            const regionName = decodeURIComponent(regionMatch[1]);
            const data = loadJsonFile('population_yearly_data.json');
            if (data) {
                const regionData = {};
                for (const [year, yearData] of Object.entries(data)) {
                    if (yearData && yearData[regionName]) {
                        regionData[year] = yearData[regionName];
                    }
                }
                return res.status(200).json(regionData);
            }
            return res.status(404).json({ error: 'Region not found' });
        }
        
        // /api/national/sido
        if (url.match(/\/api\/national\/sido/)) {
            const censusData = loadJsonFile('national_census_data.json');
            
            if (censusData && censusData.by_sido) {
                // Census 데이터의 시도 목록 반환
                const result = Object.keys(censusData.by_sido).map(sido => {
                    const regions = censusData.by_sido[sido];
                    return {
                        name: sido,
                        region_count: Object.keys(regions).length,
                        hasData: true
                    };
                }).sort((a, b) => a.name.localeCompare(b.name));
                
                return res.status(200).json(result);
            }
            
            // fallback: 기존 데이터
            const sidoList = loadJsonFile('sido_sigungu_list.json');
            if (sidoList) {
                const result = Object.keys(sidoList).map(sido => ({
                    name: sido,
                    sigungu_count: sidoList[sido].length,
                    hasData: false
                }));
                return res.status(200).json(result);
            }
            
            return res.status(200).json([]);
        }
        
        // /api/sido/<sido_name>
        const sidoMatch = url.match(/\/api\/sido\/([^/]+)$/);
        if (sidoMatch) {
            const sidoName = decodeURIComponent(sidoMatch[1]);
            
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
                
                // 명칭은 Census 데이터에 이미 포함되어 있음
                // 추가 처리 없이 그대로 반환
                
                return res.status(200).json({
                    metadata: {
                        sido: sidoName,
                        total_regions: Object.keys(sidoData).length,
                        years: censusData.metadata.years,
                        source: 'Census 데이터'
                    },
                    regions: sidoData
                });
            }
            
            return res.status(404).json({ 
                error: 'Sido not found',
                sidoName: sidoName,
                hint: 'Try: 서울특별시, 경기도, 부산광역시, 대구광역시, 인천광역시, etc.',
                availableSido: censusData && censusData.by_sido ? Object.keys(censusData.by_sido) : []
            });
        }
        
        // /api/sigungu/<sigungu_name>
        const sigunguMatch = url.match(/\/api\/sigungu\/([^/]+)$/);
        if (sigunguMatch) {
            const sigunguName = decodeURIComponent(sigunguMatch[1]);
            const seoulData = loadJsonFile('seoul_final_data.json');
            if (seoulData && seoulData.regions) {
                // regions에서 구 단위 데이터 추출
                const sigunguData = {};
                Object.entries(seoulData.regions).forEach(([key, value]) => {
                    if (key.startsWith(sigunguName + '_')) {
                        sigunguData[key] = value;
                    }
                });
                if (Object.keys(sigunguData).length > 0) {
                    return res.status(200).json({
                        sigunguName: sigunguName,
                        regions: sigunguData
                    });
                }
            }
            return res.status(404).json({ error: 'Sigungu not found' });
        }
        
        // /api/emdong/<sigungu>/<emdong>
        const emdongMatch = url.match(/\/api\/emdong\/([^/]+)\/([^/]+)$/);
        if (emdongMatch) {
            const sigunguName = decodeURIComponent(emdongMatch[1]);
            const emdongName = decodeURIComponent(emdongMatch[2]);
            const seoulData = loadJsonFile('seoul_final_data.json');
            if (seoulData && seoulData.regions) {
                const key = `${sigunguName}_${emdongName}`;
                if (seoulData.regions[key]) {
                    return res.status(200).json(seoulData.regions[key]);
                }
            }
            return res.status(404).json({ error: 'Emdong not found' });
        }
        
        // /api/emdong/<sigungu>/<emdong>/timeseries
        const timeseriesMatch = url.match(/\/api\/emdong\/([^/]+)\/([^/]+)\/timeseries/);
        if (timeseriesMatch) {
            const sigunguName = decodeURIComponent(timeseriesMatch[1]);
            const emdongName = decodeURIComponent(timeseriesMatch[2]);
            
            const monthlyData = loadJsonFile('jumin_monthly_full.json');
            if (monthlyData && monthlyData.emdongs) {
                const emdongData = monthlyData.emdongs.find(e => 
                    e.sigungu === sigunguName && e.emdong === emdongName
                );
                if (emdongData) {
                    return res.status(200).json(emdongData);
                }
            }
            return res.status(404).json({ error: 'Timeseries data not found' });
        }
        
        // /api/sigungu/<sigungu>/timeseries
        const sigunguTimeseriesMatch = url.match(/\/api\/sigungu\/([^/]+)\/timeseries/);
        if (sigunguTimeseriesMatch) {
            const sigunguName = decodeURIComponent(sigunguTimeseriesMatch[1]);
            const monthlyData = loadJsonFile('jumin_monthly_full.json');
            if (monthlyData && monthlyData.emdongs) {
                const sigunguData = monthlyData.emdongs.filter(e => e.sigungu === sigunguName);
                if (sigunguData.length > 0) {
                    const aggregated = {};
                    sigunguData.forEach(emdong => {
                        emdong.data.forEach(monthData => {
                            const month = monthData.month;
                            if (!aggregated[month]) {
                                aggregated[month] = { month, total: 0, male: 0, female: 0 };
                            }
                            aggregated[month].total += monthData.total;
                            aggregated[month].male += monthData.male;
                            aggregated[month].female += monthData.female;
                        });
                    });
                    return res.status(200).json({
                        sigungu: sigunguName,
                        data: Object.values(aggregated).sort((a, b) => a.month.localeCompare(b.month))
                    });
                }
            }
            return res.status(404).json({ error: 'Sigungu timeseries not found' });
        }
        
        // /api/sido/<sido>/timeseries
        const sidoTimeseriesMatch = url.match(/\/api\/sido\/([^/]+)\/timeseries/);
        if (sidoTimeseriesMatch) {
            const sidoName = decodeURIComponent(sidoTimeseriesMatch[1]);
            const monthlyData = loadJsonFile('jumin_monthly_full.json');
            if (monthlyData && monthlyData.emdongs) {
                const aggregated = {};
                monthlyData.emdongs.forEach(emdong => {
                    emdong.data.forEach(monthData => {
                        const month = monthData.month;
                        if (!aggregated[month]) {
                            aggregated[month] = { month, total: 0, male: 0, female: 0 };
                        }
                        aggregated[month].total += monthData.total;
                        aggregated[month].male += monthData.male;
                        aggregated[month].female += monthData.female;
                    });
                });
                return res.status(200).json({
                    sido: sidoName,
                    data: Object.values(aggregated).sort((a, b) => a.month.localeCompare(b.month))
                });
            }
            return res.status(404).json({ error: 'Sido timeseries not found' });
        }
        
        // /api/years
        if (url.match(/\/api\/years/)) {
            return res.status(200).json({ 
                years: ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'] 
            });
        }
        
        // /api/politician/<name>/lda - 정치인 LDA 분석
        const politicianLDAMatch = url.match(/\/api\/politician\/([^/]+)\/lda/);
        if (politicianLDAMatch) {
            const politicianName = decodeURIComponent(politicianLDAMatch[1]);
            
            // 국회의원 LDA 데이터 확인
            const assemblyLDA = loadJsonFile('assembly_member_lda_analysis.json');
            if (assemblyLDA && assemblyLDA[politicianName]) {
                return res.status(200).json({
                    type: 'assembly',
                    data: assemblyLDA[politicianName]
                });
            }
            
            // 지방정치인 LDA 데이터 확인
            const localLDA = loadJsonFile('local_politicians_lda_analysis.json');
            if (localLDA && localLDA[politicianName]) {
                return res.status(200).json({
                    type: 'local',
                    data: localLDA[politicianName]
                });
            }
            
            return res.status(404).json({ 
                error: 'Politician LDA data not found',
                name: politicianName
            });
        }
        
        // /api/lda/assembly - 모든 국회의원 LDA 목록
        if (url.match(/\/api\/lda\/assembly/)) {
            const assemblyLDA = loadJsonFile('assembly_member_lda_analysis.json');
            if (assemblyLDA) {
                // 요약 정보만 반환 (전체는 너무 큼)
                const summary = Object.keys(assemblyLDA).map(name => ({
                    name: name,
                    party: assemblyLDA[name].member_info?.party,
                    district: assemblyLDA[name].member_info?.district,
                    total_count: assemblyLDA[name].total_count
                }));
                return res.status(200).json({
                    total: summary.length,
                    politicians: summary
                });
            }
            return res.status(200).json({ total: 0, politicians: [] });
        }
        
        // /api/lda/local - 모든 지방정치인 LDA 목록
        if (url.match(/\/api\/lda\/local/)) {
            const localLDA = loadJsonFile('local_politicians_lda_analysis.json');
            if (localLDA) {
                const summary = Object.keys(localLDA).map(name => ({
                    name: name,
                    party: localLDA[name].member_info?.party,
                    district: localLDA[name].member_info?.district,
                    total_count: localLDA[name].total_count
                }));
                return res.status(200).json({
                    total: summary.length,
                    politicians: summary
                });
            }
            return res.status(200).json({ total: 0, politicians: [] });
        }
        
        // /api/network/assembly - 국회의원 네트워크 (상위 10명)
        if (url.match(/\/api\/network\/assembly/)) {
            const networkData = loadJsonFile('assembly_network_graph.json');
            if (networkData) {
                // 상위 10명만 반환
                const top10 = networkData.top_50_members ? 
                    networkData.top_50_members.slice(0, 10) : [];
                
                return res.status(200).json({
                    metadata: networkData.metadata,
                    top_members: top10,
                    total_members: networkData.members ? Object.keys(networkData.members).length : 0,
                    total_connections: networkData.connection_stats?.total_connections || 0,
                    clusters_count: networkData.clusters ? networkData.clusters.length : 0
                });
            }
            return res.status(404).json({ error: 'Network data not found' });
        }
        
        // /api/network/member/<name> - 특정 의원 네트워크
        const networkMemberMatch = url.match(/\/api\/network\/member\/([^/]+)/);
        if (networkMemberMatch) {
            const memberName = decodeURIComponent(networkMemberMatch[1]);
            const networkData = loadJsonFile('assembly_network_graph.json');
            
            if (networkData && networkData.member_connections && networkData.member_connections[memberName]) {
                return res.status(200).json({
                    name: memberName,
                    connections: networkData.member_connections[memberName],
                    cluster: networkData.member_to_cluster?.[memberName],
                    member_info: networkData.members?.[memberName]
                });
            }
            
            return res.status(404).json({ 
                error: 'Member network not found',
                name: memberName
            });
        }
        
        // /api/issues - 전체 이슈 추적
        if (url.match(/\/api\/issues$/)) {
            const issueData = loadJsonFile('issue_articles_tracking.json');
            if (issueData) {
                return res.status(200).json(issueData);
            }
            return res.status(404).json({ error: 'Issue data not found' });
        }
        
        // /api/issues/<region> - 지역별 이슈
        const issueRegionMatch = url.match(/\/api\/issues\/([^/]+)/);
        if (issueRegionMatch) {
            const region = decodeURIComponent(issueRegionMatch[1]);
            const issueData = loadJsonFile('issue_articles_tracking.json');
            
            if (issueData && issueData[region]) {
                return res.status(200).json({
                    region: region,
                    issues: issueData[region]
                });
            }
            
            return res.status(404).json({ 
                error: 'Region issues not found',
                region: region
            });
        }
        
        // /api/news/<region> - 지역별 뉴스
        const newsRegionMatch = url.match(/\/api\/news\/([^/]+)/);
        if (newsRegionMatch) {
            const region = decodeURIComponent(newsRegionMatch[1]);
            const newsData = loadJsonFile('gu_news_articles.json');
            
            if (newsData && newsData[region]) {
                return res.status(200).json({
                    region: region,
                    news: newsData[region]
                });
            }
            
            return res.status(404).json({ 
                error: 'Region news not found',
                region: region
            });
        }
        
        // /api/keywords/<region> - 지역별 키워드
        const keywordRegionMatch = url.match(/\/api\/keywords\/([^/]+)/);
        if (keywordRegionMatch) {
            const region = decodeURIComponent(keywordRegionMatch[1]);
            const keywordData = loadJsonFile('gu_news_keywords.json');
            
            if (keywordData && keywordData[region]) {
                return res.status(200).json({
                    region: region,
                    keywords: keywordData[region]
                });
            }
            
            return res.status(404).json({ 
                error: 'Region keywords not found',
                region: region
            });
        }
        
        // /api/audit/<region> - 감사 키워드
        const auditRegionMatch = url.match(/\/api\/audit\/([^/]+)/);
        if (auditRegionMatch) {
            const region = decodeURIComponent(auditRegionMatch[1]);
            const auditKeywords = loadJsonFile('gu_audit_keywords.json');
            const auditNews = loadJsonFile('gu_audit_news.json');
            
            return res.status(200).json({
                region: region,
                keywords: auditKeywords?.[region] || [],
                news: auditNews?.[region] || []
            });
        }
        
        // /api/gdp/<region> - 상세 GDP 데이터
        const gdpRegionMatch = url.match(/\/api\/gdp\/([^/]+)/);
        if (gdpRegionMatch) {
            const region = decodeURIComponent(gdpRegionMatch[1]);
            const gdpData = loadJsonFile('seoul_detailed_gdp_data.json');
            
            if (gdpData && gdpData[region]) {
                return res.status(200).json({
                    region: region,
                    data: gdpData[region]
                });
            }
            
            return res.status(404).json({ error: 'GDP data not found', region: region });
        }
        
        // /api/education/<region> - 교육 데이터
        const educationMatch = url.match(/\/api\/education\/([^/]+)/);
        if (educationMatch) {
            const region = decodeURIComponent(educationMatch[1]);
            const eduData = loadJsonFile('seoul_education_data.json');
            
            if (eduData && eduData[region]) {
                return res.status(200).json({
                    region: region,
                    data: eduData[region]
                });
            }
            
            return res.status(404).json({ error: 'Education data not found', region: region });
        }
        
        // /api/commercial/<region> - 상업지역 데이터
        const commercialMatch = url.match(/\/api\/commercial\/([^/]+)/);
        if (commercialMatch) {
            const region = decodeURIComponent(commercialMatch[1]);
            const commercialData = loadJsonFile('seoul_commercial_area_data.json');
            
            if (commercialData && commercialData[region]) {
                return res.status(200).json({
                    region: region,
                    data: commercialData[region]
                });
            }
            
            return res.status(404).json({ error: 'Commercial data not found', region: region });
        }
        
        // /api/safety/<region> - 안전 데이터
        const safetyMatch = url.match(/\/api\/safety\/([^/]+)/);
        if (safetyMatch) {
            const region = decodeURIComponent(safetyMatch[1]);
            const safetyData = loadJsonFile('seoul_safety_data.json');
            
            if (safetyData && safetyData[region]) {
                return res.status(200).json({
                    region: region,
                    data: safetyData[region]
                });
            }
            
            return res.status(404).json({ error: 'Safety data not found', region: region });
        }
        
        // /api/traffic/<region> - 교통 데이터
        const trafficMatch = url.match(/\/api\/traffic\/([^/]+)/);
        if (trafficMatch) {
            const region = decodeURIComponent(trafficMatch[1]);
            const trafficData = loadJsonFile('seoul_traffic_data.json');
            
            if (trafficData && trafficData[region]) {
                return res.status(200).json({
                    region: region,
                    data: trafficData[region]
                });
            }
            
            return res.status(404).json({ error: 'Traffic data not found', region: region });
        }
        
        // /api/search/news - 네이버 뉴스 검색
        const newsSearchMatch = url.match(/\/api\/search\/news/);
        if (newsSearchMatch) {
            const query = req.query?.q || '';
            if (!query) {
                return res.status(400).json({ error: 'Query parameter required' });
            }
            
            return new Promise((resolve) => {
                const encodedQuery = encodeURIComponent(query);
                const options = {
                    hostname: 'openapi.naver.com',
                    path: `/v1/search/news.json?query=${encodedQuery}&display=10&sort=date`,
                    method: 'GET',
                    headers: {
                        'X-Naver-Client-Id': NAVER_CLIENT_ID,
                        'X-Naver-Client-Secret': NAVER_CLIENT_SECRET
                    }
                };
                
                const request = https.request(options, (response) => {
                    let data = '';
                    response.on('data', (chunk) => { data += chunk; });
                    response.on('end', () => {
                        try {
                            const result = JSON.parse(data);
                            resolve(res.status(200).json(result));
                        } catch (e) {
                            resolve(res.status(500).json({ error: 'Parse error', details: data }));
                        }
                    });
                });
                
                request.on('error', (error) => {
                    resolve(res.status(500).json({ error: error.message }));
                });
                
                request.end();
            });
        }
        
        // /api/search
        if (url.match(/\/api\/search/)) {
            return res.status(200).json({ results: [] });
        }
        
        // Default 404
        return res.status(404).json({ 
            error: 'Not found', 
            url: url,
            availableEndpoints: [
                '/api/debug',
                '/api/national/sido',
                '/api/sido/<name>',
                '/api/politicians/*',
                '/api/population/*',
                '/api/politician/<name>/lda',
                '/api/lda/assembly',
                '/api/lda/local',
                '/api/network/assembly',
                '/api/network/member/<name>'
            ]
        });
        
    } catch (error) {
        console.error('Error:', error);
        return res.status(500).json({ 
            error: 'Internal server error',
            message: error.message 
        });
    }
};
