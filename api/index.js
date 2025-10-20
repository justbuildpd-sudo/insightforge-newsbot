import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import zlib from 'zlib';

// ES modules에서 __dirname 대체
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 데이터 디렉토리
const DATA_DIR = path.join(process.cwd(), 'insightforge-web', 'data');

// 캐시
const dataCache = {};

// JSON 파일 로드 (gzip 지원)
function loadJsonFile(filename) {
    if (dataCache[filename]) {
        return dataCache[filename];
    }
    
    // gzip 파일 먼저 시도
    const gzPath = path.join(DATA_DIR, filename + '.gz');
    if (fs.existsSync(gzPath)) {
        try {
            const compressed = fs.readFileSync(gzPath);
            const decompressed = zlib.gunzipSync(compressed);
            const data = JSON.parse(decompressed.toString('utf-8'));
            dataCache[filename] = data;
            return data;
        } catch (error) {
            console.error(`Error loading ${filename}.gz:`, error);
        }
    }
    
    // 일반 파일
    const filePath = path.join(DATA_DIR, filename);
    if (!fs.existsSync(filePath)) {
        return null;
    }
    
    try {
        const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
        dataCache[filename] = data;
        return data;
    } catch (error) {
        console.error(`Error loading ${filename}:`, error);
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
export default async (req, res) => {
    // CORS preflight
    if (req.method === 'OPTIONS') {
        return res.status(200).json({});
    }
    
    // Set CORS headers
    Object.entries(corsHeaders).forEach(([key, value]) => {
        res.setHeader(key, value);
    });
    
    const { url } = req;
    console.log('📥 Request:', url);
    console.log('📁 DATA_DIR:', DATA_DIR);
    console.log('📁 DATA_DIR exists:', fs.existsSync(DATA_DIR));
    console.log('📁 cwd:', process.cwd());
    
    // Debug endpoint
    if (url.match(/\/api\/debug/)) {
        return res.status(200).json({
            cwd: process.cwd(),
            dataDir: DATA_DIR,
            dataDirExists: fs.existsSync(DATA_DIR),
            files: fs.existsSync(DATA_DIR) ? fs.readdirSync(DATA_DIR).slice(0, 10) : []
        });
    }
    
    try {
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
            const data = loadJsonFile('national_comprehensive_data.json');
            if (data && data.sido_list) {
                return res.status(200).json(data.sido_list);
            }
            return res.status(200).json([]);
        }
        
        // /api/sido/<sido_name>
        const sidoMatch = url.match(/\/api\/sido\/([^/]+)/);
        if (sidoMatch) {
            const sidoName = decodeURIComponent(sidoMatch[1]);
            const filename = sidoName === 'seoul' || sidoName === '서울' 
                ? 'seoul_final_data.json' 
                : `${sidoName}_comprehensive_data.json`;
            const data = loadJsonFile(filename);
            return res.status(200).json(data || {});
        }
        
        // /api/sigungu/<sigungu_name>
        const sigunguMatch = url.match(/\/api\/sigungu\/([^/]+)/);
        if (sigunguMatch) {
            const sigunguName = decodeURIComponent(sigunguMatch[1]);
            const seoulData = loadJsonFile('seoul_final_data.json');
            if (seoulData && seoulData.sigungu_list) {
                const sigungu = seoulData.sigungu_list.find(s => s.sigunguName === sigunguName);
                if (sigungu) {
                    return res.status(200).json(sigungu);
                }
            }
            return res.status(404).json({ error: 'Sigungu not found' });
        }
        
        // /api/emdong/<sigungu>/<emdong>
        const emdongMatch = url.match(/\/api\/emdong\/([^/]+)\/([^/]+)/);
        if (emdongMatch) {
            const sigunguName = decodeURIComponent(emdongMatch[1]);
            const emdongName = decodeURIComponent(emdongMatch[2]);
            const seoulData = loadJsonFile('seoul_final_data.json');
            if (seoulData && seoulData.sigungu_list) {
                const sigungu = seoulData.sigungu_list.find(s => s.sigunguName === sigunguName);
                if (sigungu && sigungu.emdong_list) {
                    const emdong = sigungu.emdong_list.find(e => e.emdongName === emdongName);
                    if (emdong) {
                        return res.status(200).json(emdong);
                    }
                }
            }
            return res.status(404).json({ error: 'Emdong not found' });
        }
        
        // /api/emdong/<sigungu>/<emdong>/timeseries
        const timeseriesMatch = url.match(/\/api\/emdong\/([^/]+)\/([^/]+)\/timeseries/);
        if (timeseriesMatch) {
            const sigunguName = decodeURIComponent(timeseriesMatch[1]);
            const emdongName = decodeURIComponent(timeseriesMatch[2]);
            
            // 월별 데이터 로드
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
                    // Aggregate by month
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
                // Aggregate all
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
            return res.status(200).json({ years: ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'] });
        }
        
        // /api/search
        if (url.match(/\/api\/search/)) {
            return res.status(200).json({ results: [] });
        }
        
        // Default 404
        return res.status(404).json({ error: 'Not found', url });
        
    } catch (error) {
        console.error('❌ Error:', error);
        return res.status(500).json({ error: error.message });
    }
};

