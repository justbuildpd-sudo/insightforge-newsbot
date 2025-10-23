// Welfare data API endpoint
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
    
    const { region_code, welfare_type } = req.query;
    
    // 샘플 복지 데이터
    const welfareData = {
        region_code: region_code || '11',
        region_name: '서울특별시',
        welfare_type: welfare_type || 'all',
        facilities: {
            total: 1234,
            senior_centers: 234,
            child_care_centers: 456,
            welfare_centers: 123,
            medical_centers: 89,
            others: 332
        },
        beneficiaries: {
            total: 456789,
            elderly: 123456,
            children: 234567,
            disabled: 45678,
            low_income: 53088
        },
        budget: {
            total: 12345600000000, // 12조 3456억원
            per_capita: 2700000, // 270만원
            elderly_care: 4567890000000, // 4조 5678억 9천만원
            child_care: 3456780000000, // 3조 4567억 8천만원
            medical: 2345670000000, // 2조 3456억 7천만원
            others: 1975260000000 // 1조 9752억 6천만원
        },
        programs: [
            {
                name: '기초생활수급자 지원',
                beneficiaries: 45678,
                budget: 1234560000000,
                coverage_rate: 95.2
            },
            {
                name: '노인 돌봄 서비스',
                beneficiaries: 123456,
                budget: 2345670000000,
                coverage_rate: 78.9
            },
            {
                name: '아동 돌봄 서비스',
                beneficiaries: 234567,
                budget: 3456780000000,
                coverage_rate: 85.6
            },
            {
                name: '장애인 복지 서비스',
                beneficiaries: 45678,
                budget: 1234560000000,
                coverage_rate: 92.3
            }
        ],
        trends: [
            { year: '2019', budget: 10000000000000, beneficiaries: 420000 },
            { year: '2020', budget: 10500000000000, beneficiaries: 430000 },
            { year: '2021', budget: 11000000000000, beneficiaries: 440000 },
            { year: '2022', budget: 11500000000000, beneficiaries: 450000 },
            { year: '2023', budget: 12345600000000, beneficiaries: 456789 }
        ]
    };
    
    res.status(200).json(welfareData);
}
