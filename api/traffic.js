// Traffic data API endpoint
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
    
    const { region_code, transport_type } = req.query;
    
    // 샘플 교통 데이터
    const trafficData = {
        region_code: region_code || '11',
        region_name: '서울특별시',
        transport_type: transport_type || 'all',
        infrastructure: {
            roads: {
                total_length: 12345.6, // km
                highways: 234.5,
                arterial_roads: 1234.5,
                local_roads: 10776.6
            },
            public_transport: {
                subway_lines: 9,
                subway_stations: 234,
                bus_routes: 456,
                bus_stops: 5678
            }
        },
        usage: {
            daily_passengers: 4567890,
            subway: 2345678,
            bus: 1234567,
            taxi: 456789,
            private_cars: 234567,
            others: 234567
        },
        efficiency: {
            average_speed: 25.6, // km/h
            congestion_index: 3.2, // 1-5 scale
            punctuality_rate: 92.3, // %
            satisfaction_rate: 78.9 // %
        },
        environmental_impact: {
            co2_emissions: 1234567, // tons/year
            air_quality_index: 3.2, // 1-5 scale
            noise_level: 65.4, // dB
            green_transport_ratio: 45.6 // %
        },
        trends: [
            { year: '2019', passengers: 4200000, co2_emissions: 1200000 },
            { year: '2020', passengers: 3800000, co2_emissions: 1100000 },
            { year: '2021', passengers: 4100000, co2_emissions: 1150000 },
            { year: '2022', passengers: 4400000, co2_emissions: 1200000 },
            { year: '2023', passengers: 4567890, co2_emissions: 1234567 }
        ],
        projects: [
            {
                name: '지하철 9호선 연장',
                budget: 1234560000000,
                completion_rate: 85.6,
                expected_completion: '2025-12-31'
            },
            {
                name: '스마트 교통 시스템 구축',
                budget: 234567000000,
                completion_rate: 67.8,
                expected_completion: '2024-06-30'
            }
        ]
    };
    
    res.status(200).json(trafficData);
}
