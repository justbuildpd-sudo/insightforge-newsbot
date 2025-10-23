// Comprehensive data API endpoint - 모든 데이터를 종합한 대시보드용 API
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
    
    // 종합 데이터 (모든 데이터를 통합한 대시보드용)
    const comprehensiveData = {
        region_code: region_code || '11',
        region_name: '서울특별시',
        last_updated: '2024-10-23T10:00:00Z',
        overview: {
            population: 9720846,
            area: 605.21,
            density: 16060,
            gdp: 456789000000000,
            gdp_per_capita: 45678900
        },
        indicators: {
            population: {
                total: 9720846,
                growth_rate: 0.8,
                age_distribution: {
                    '0-14': 12.3,
                    '15-64': 70.2,
                    '65+': 17.5
                }
            },
            economy: {
                gdp: 456789000000000,
                gdp_growth: 2.8,
                unemployment_rate: 3.2,
                inflation_rate: 2.1
            },
            education: {
                schools: 1250,
                students: 1256789,
                graduation_rate: 98.5,
                college_rate: 78.9
            },
            welfare: {
                facilities: 1234,
                beneficiaries: 456789,
                budget: 12345600000000,
                coverage_rate: 85.6
            },
            safety: {
                crime_rate: 2.3,
                accident_rate: 1.8,
                safety_index: 85.6,
                response_time: 7.5
            },
            environment: {
                air_quality: 3.2,
                green_ratio: 45.6,
                co2_emissions: 1234567,
                energy_efficiency: 78.9
            }
        },
        rankings: {
            population: { rank: 1, percentile: 100 },
            gdp: { rank: 1, percentile: 100 },
            education: { rank: 2, percentile: 95 },
            welfare: { rank: 3, percentile: 90 },
            safety: { rank: 5, percentile: 85 },
            environment: { rank: 8, percentile: 80 }
        },
        trends: {
            population: [
                { year: '2019', value: 9720846, change: 0.5 },
                { year: '2020', value: 9712345, change: -0.1 },
                { year: '2021', value: 9723456, change: 0.1 },
                { year: '2022', value: 9734567, change: 0.1 },
                { year: '2023', value: 9720846, change: -0.1 }
            ],
            gdp: [
                { year: '2019', value: 420000000000000, change: 2.1 },
                { year: '2020', value: 410000000000000, change: -2.4 },
                { year: '2021', value: 425000000000000, change: 3.7 },
                { year: '2022', value: 440000000000000, change: 3.5 },
                { year: '2023', value: 456789000000000, change: 2.8 }
            ]
        },
        alerts: [
            {
                type: 'warning',
                message: '인구 감소 추세가 지속되고 있습니다.',
                severity: 'medium',
                date: '2024-10-20'
            },
            {
                type: 'info',
                message: 'GDP 성장률이 전국 평균을 상회하고 있습니다.',
                severity: 'low',
                date: '2024-10-18'
            },
            {
                type: 'success',
                message: '교육 지표가 전국 상위권을 유지하고 있습니다.',
                severity: 'low',
                date: '2024-10-15'
            }
        ],
        recommendations: [
            {
                category: '인구',
                title: '인구 감소 대응 정책 강화',
                description: '청년 정착 지원 및 출산 장려 정책 확대 필요',
                priority: 'high',
                expected_impact: 'medium'
            },
            {
                category: '경제',
                title: '디지털 경제 전환 가속화',
                description: '스마트시티 구축 및 디지털 인프라 확충',
                priority: 'medium',
                expected_impact: 'high'
            },
            {
                category: '환경',
                title: '친환경 도시 조성',
                description: '녹지 확대 및 대기질 개선 정책 추진',
                priority: 'medium',
                expected_impact: 'medium'
            }
        ]
    };
    
    res.status(200).json(comprehensiveData);
}
