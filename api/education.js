// Education data API endpoint
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
    
    const { region_code, school_level } = req.query;
    
    // 샘플 교육 데이터
    const educationData = {
        region_code: region_code || '11',
        region_name: '서울특별시',
        school_level: school_level || 'all',
        schools: {
            total: 1250,
            elementary: 456,
            middle: 234,
            high: 189,
            university: 45,
            others: 326
        },
        students: {
            total: 1256789,
            elementary: 456789,
            middle: 234567,
            high: 345678,
            university: 219755
        },
        performance: {
            graduation_rate: 98.5,
            college_entrance_rate: 78.9,
            dropout_rate: 1.2,
            average_score: 85.6
        },
        facilities: {
            libraries: 234,
            computer_labs: 456,
            science_labs: 189,
            gymnasiums: 267,
            cafeterias: 345
        },
        budget: {
            total: 4567890000000, // 4조 5678억 9천만원
            per_student: 3650000, // 365만원
            facilities: 1234560000000, // 1조 2345억 6천만원
            programs: 2345670000000 // 2조 3456억 7천만원
        },
        trends: [
            { year: '2019', students: 1234567, budget: 4200000000000 },
            { year: '2020', students: 1245678, budget: 4300000000000 },
            { year: '2021', students: 1251234, budget: 4400000000000 },
            { year: '2022', students: 1254567, budget: 4500000000000 },
            { year: '2023', students: 1256789, budget: 4567890000000 }
        ]
    };
    
    res.status(200).json(educationData);
}
