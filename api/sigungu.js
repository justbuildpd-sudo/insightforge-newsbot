// Sigungu data API endpoint
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
    
    const { sido_code } = req.query;
    
    if (!sido_code) {
        res.status(400).json({ error: 'sido_code parameter is required' });
        return;
    }
    
    // 샘플 시군구 데이터 (서울특별시 기준)
    const sigunguData = {
        sigungu_list: [
            {
                code: '11010',
                sigungu_name: '종로구',
                total_emdong: 17,
                population: 154000
            },
            {
                code: '11020',
                sigungu_name: '중구',
                total_emdong: 15,
                population: 134000
            },
            {
                code: '11030',
                sigungu_name: '용산구',
                total_emdong: 16,
                population: 243000
            },
            {
                code: '11040',
                sigungu_name: '성동구',
                total_emdong: 20,
                population: 308000
            },
            {
                code: '11050',
                sigungu_name: '광진구',
                total_emdong: 15,
                population: 352000
            },
            {
                code: '11060',
                sigungu_name: '동대문구',
                total_emdong: 14,
                population: 346000
            },
            {
                code: '11070',
                sigungu_name: '중랑구',
                total_emdong: 20,
                population: 414000
            },
            {
                code: '11080',
                sigungu_name: '성북구',
                total_emdong: 20,
                population: 447000
            },
            {
                code: '11090',
                sigungu_name: '강북구',
                total_emdong: 18,
                population: 330000
            },
            {
                code: '11100',
                sigungu_name: '도봉구',
                total_emdong: 14,
                population: 348000
            },
            {
                code: '11110',
                sigungu_name: '노원구',
                total_emdong: 20,
                population: 536000
            },
            {
                code: '11120',
                sigungu_name: '은평구',
                total_emdong: 16,
                population: 484000
            },
            {
                code: '11130',
                sigungu_name: '서대문구',
                total_emdong: 14,
                population: 315000
            },
            {
                code: '11140',
                sigungu_name: '마포구',
                total_emdong: 16,
                population: 371000
            },
            {
                code: '11150',
                sigungu_name: '양천구',
                total_emdong: 18,
                population: 464000
            },
            {
                code: '11160',
                sigungu_name: '강서구',
                total_emdong: 20,
                population: 583000
            },
            {
                code: '11170',
                sigungu_name: '구로구',
                total_emdong: 15,
                population: 417000
            },
            {
                code: '11180',
                sigungu_name: '금천구',
                total_emdong: 10,
                population: 244000
            },
            {
                code: '11190',
                sigungu_name: '영등포구',
                total_emdong: 20,
                population: 401000
            },
            {
                code: '11200',
                sigungu_name: '동작구',
                total_emdong: 20,
                population: 401000
            },
            {
                code: '11210',
                sigungu_name: '관악구',
                total_emdong: 21,
                population: 519000
            },
            {
                code: '11220',
                sigungu_name: '서초구',
                total_emdong: 18,
                population: 431000
            },
            {
                code: '11230',
                sigungu_name: '강남구',
                total_emdong: 22,
                population: 547000
            },
            {
                code: '11240',
                sigungu_name: '송파구',
                total_emdong: 20,
                population: 667000
            },
            {
                code: '11250',
                sigungu_name: '강동구',
                total_emdong: 18,
                population: 442000
            }
        ]
    };
    
    res.status(200).json(sigunguData);
}
