const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

// 데이터 디렉토리
const DATA_DIR = path.join(process.cwd(), 'insightforge-web', 'data');

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
            const sidoList = loadJsonFile('sido_sigungu_list.json');
            if (sidoList) {
                // 시도 목록을 배열로 변환
                const result = Object.keys(sidoList).map(sido => ({
                    name: sido,
                    sigungu_count: sidoList[sido].length,
                    sigungu_list: sidoList[sido]
                }));
                return res.status(200).json(result);
            }
            
            // fallback: national_comprehensive_data.json 사용
            const data = loadJsonFile('national_comprehensive_data.json');
            if (data) {
                const sidoMap = {};
                Object.values(data).forEach(item => {
                    if (item.sido && !sidoMap[item.sido]) {
                        sidoMap[item.sido] = {
                            name: item.sido,
                            code: item.sido_code
                        };
                    }
                });
                return res.status(200).json(Object.values(sidoMap));
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
            
            // 시도 코드 매핑 로드
            const sidoCodeMapping = loadJsonFile('sido_code_mapping.json');
            const reverseMapping = {};
            if (sidoCodeMapping) {
                Object.entries(sidoCodeMapping).forEach(([code, name]) => {
                    reverseMapping[name] = 'sido' + code;
                });
            }
            
            // 다른 시도는 national_comprehensive_data에서 필터링
            const nationalData = loadJsonFile('national_comprehensive_data.json');
            if (nationalData) {
                const targetSidoCode = reverseMapping[sidoName] || sidoName;
                const sidoData = {};
                
                Object.entries(nationalData).forEach(([code, item]) => {
                    if (item.sido === sidoName || item.sido === targetSidoCode) {
                        sidoData[code] = item;
                    }
                });
                
                if (Object.keys(sidoData).length > 0) {
                    // 시군구 목록 추가
                    const sidoList = loadJsonFile('sido_sigungu_list.json');
                    const sigunguList = sidoList ? (sidoList[sidoName] || []) : [];
                    
                    return res.status(200).json({
                        sidoName: sidoName,
                        sigungu_count: Object.keys(sidoData).length,
                        sigungu_list: sigunguList,
                        data: sidoData
                    });
                }
            }
            
            return res.status(404).json({ 
                error: 'Sido not found',
                sidoName: sidoName,
                hint: 'Try: 서울특별시, 경기도, 부산광역시, etc.'
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
                '/api/population/*'
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
