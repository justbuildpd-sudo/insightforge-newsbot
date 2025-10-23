// GDP data API endpoint
export default function handler(req, res) {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    if (req.method !== 'GET') {
        res.status(405).json({ error: 'Method not allowed' });
        return;
    }
    
    const { region_code, year } = req.query;
    
    // 샘플 GDP 데이터
    const gdpData = {
        region_code: region_code || '11',
        region_name: '서울특별시',
        year: year || '2023',
        gdp: {
            total: 456789000000000, // 456조 7890억원
            per_capita: 45678900, // 4567만원
            growth_rate: 2.8,
            sectors: {
                primary: { value: 12345600000000, percentage: 2.7 },
                secondary: { value: 123456000000000, percentage: 27.0 },
                tertiary: { value: 309877000000000, percentage: 67.8 }
            }
        },
        comparison: {
            national_average: 3.2,
            rank: 1,
            percentile: 95.5
        },
        trends: [
            { year: '2019', value: 420000000000000, growth_rate: 2.1 },
            { year: '2020', value: 410000000000000, growth_rate: -2.4 },
            { year: '2021', value: 425000000000000, growth_rate: 3.7 },
            { year: '2022', value: 440000000000000, growth_rate: 3.5 },
            { year: '2023', value: 456789000000000, growth_rate: 2.8 }
        ]
    };
    
    res.status(200).json(gdpData);
}
