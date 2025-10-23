// Sido data API endpoint
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
    
    // 샘플 시도 데이터
    const sidoData = {
        sido_list: [
            {
                code: '11',
                sido_name: '서울특별시',
                total_regions: 25
            },
            {
                code: '26',
                sido_name: '부산광역시',
                total_regions: 16
            },
            {
                code: '27',
                sido_name: '대구광역시',
                total_regions: 8
            },
            {
                code: '28',
                sido_name: '인천광역시',
                total_regions: 10
            },
            {
                code: '29',
                sido_name: '광주광역시',
                total_regions: 5
            },
            {
                code: '30',
                sido_name: '대전광역시',
                total_regions: 5
            },
            {
                code: '31',
                sido_name: '울산광역시',
                total_regions: 5
            },
            {
                code: '36',
                sido_name: '세종특별자치시',
                total_regions: 1
            },
            {
                code: '41',
                sido_name: '경기도',
                total_regions: 31
            },
            {
                code: '42',
                sido_name: '강원특별자치도',
                total_regions: 18
            },
            {
                code: '43',
                sido_name: '충청북도',
                total_regions: 11
            },
            {
                code: '44',
                sido_name: '충청남도',
                total_regions: 15
            },
            {
                code: '45',
                sido_name: '전북특별자치도',
                total_regions: 14
            },
            {
                code: '46',
                sido_name: '전라남도',
                total_regions: 22
            },
            {
                code: '47',
                sido_name: '경상북도',
                total_regions: 23
            },
            {
                code: '48',
                sido_name: '경상남도',
                total_regions: 18
            },
            {
                code: '50',
                sido_name: '제주특별자치도',
                total_regions: 2
            }
        ]
    };
    
    res.status(200).json(sidoData);
}
