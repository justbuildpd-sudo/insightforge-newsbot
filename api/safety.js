// Safety data API endpoint
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
    
    const { region_code, safety_type } = req.query;
    
    // 샘플 안전 데이터
    const safetyData = {
        region_code: region_code || '11',
        region_name: '서울특별시',
        safety_type: safety_type || 'all',
        incidents: {
            total: 12345,
            traffic_accidents: 4567,
            crimes: 2345,
            fires: 123,
            disasters: 45,
            others: 5265
        },
        safety_indicators: {
            crime_rate: 2.3, // 인구 10만명당
            accident_rate: 1.8, // 인구 10만명당
            fire_rate: 0.3, // 인구 10만명당
            safety_index: 85.6
        },
        facilities: {
            police_stations: 45,
            fire_stations: 23,
            emergency_centers: 12,
            cctv_cameras: 12345,
            emergency_call_boxes: 234
        },
        response_times: {
            police: 8.5, // 분
            fire: 6.2, // 분
            medical: 7.8, // 분
            average: 7.5 // 분
        },
        prevention_programs: [
            {
                name: '범죄 예방 프로그램',
                participants: 12345,
                effectiveness: 78.9,
                budget: 123456000000
            },
            {
                name: '교통 안전 교육',
                participants: 23456,
                effectiveness: 85.6,
                budget: 234567000000
            },
            {
                name: '화재 예방 교육',
                participants: 12345,
                effectiveness: 92.3,
                budget: 123456000000
            }
        ],
        trends: [
            { year: '2019', incidents: 13567, safety_index: 82.3 },
            { year: '2020', incidents: 12890, safety_index: 83.5 },
            { year: '2021', incidents: 12567, safety_index: 84.2 },
            { year: '2022', incidents: 12345, safety_index: 85.1 },
            { year: '2023', incidents: 12345, safety_index: 85.6 }
        ]
    };
    
    res.status(200).json(safetyData);
}
