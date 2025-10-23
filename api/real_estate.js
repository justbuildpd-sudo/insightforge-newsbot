// Real estate data API endpoint
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
    
    const { region_code, property_type } = req.query;
    
    // 샘플 부동산 데이터
    const realEstateData = {
        region_code: region_code || '11',
        region_name: '서울특별시',
        property_type: property_type || 'apartment',
        prices: {
            average: 850000000, // 8억 5천만원
            median: 750000000, // 7억 5천만원
            min: 450000000, // 4억 5천만원
            max: 1500000000 // 15억원
        },
        trends: {
            monthly_change: 1.2,
            yearly_change: 8.5,
            volatility: 12.3
        },
        market_indicators: {
            supply: 1250,
            demand: 1890,
            vacancy_rate: 3.2,
            transaction_volume: 456
        },
        districts: [
            {
                name: '강남구',
                average_price: 1200000000,
                change_rate: 5.2,
                transaction_count: 89
            },
            {
                name: '서초구',
                average_price: 1100000000,
                change_rate: 4.8,
                transaction_count: 67
            },
            {
                name: '송파구',
                average_price: 950000000,
                change_rate: 6.1,
                transaction_count: 123
            },
            {
                name: '종로구',
                average_price: 780000000,
                change_rate: 2.3,
                transaction_count: 45
            }
        ]
    };
    
    res.status(200).json(realEstateData);
}
