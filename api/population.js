// Population data API endpoint
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
    
    const { region_code } = req.query;
    
    if (!region_code) {
        res.status(400).json({ error: 'region_code parameter is required' });
        return;
    }
    
    // 샘플 인구 데이터
    const populationData = {
        region_code: region_code,
        region_name: '서울특별시 종로구',
        population: {
            total: 154000,
            male: 75000,
            female: 79000,
            age_groups: {
                '0-9': 12000,
                '10-19': 15000,
                '20-29': 18000,
                '30-39': 20000,
                '40-49': 25000,
                '50-59': 22000,
                '60-69': 18000,
                '70-79': 15000,
                '80+': 9000
            }
        },
        trends: {
            growth_rate: 0.8,
            migration_rate: -0.2,
            birth_rate: 0.6,
            death_rate: 0.4
        },
        demographics: {
            density: 12500,
            households: 68000,
            average_age: 42.5,
            elderly_ratio: 18.2
        },
        last_updated: '2024-10-23'
    };
    
    res.status(200).json(populationData);
}
