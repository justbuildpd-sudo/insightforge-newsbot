// Emdong data API endpoint
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
    
    const { sigungu_code } = req.query;
    
    if (!sigungu_code) {
        res.status(400).json({ error: 'sigungu_code parameter is required' });
        return;
    }
    
    // 샘플 읍면동 데이터 (종로구 기준)
    const emdongData = {
        emdong_list: [
            {
                code: '11010101',
                emdong_name: '청운동',
                population: 12000,
                area: 1.2
            },
            {
                code: '11010102',
                emdong_name: '신교동',
                population: 8000,
                area: 0.8
            },
            {
                code: '11010103',
                emdong_name: '궁정동',
                population: 6000,
                area: 0.6
            },
            {
                code: '11010104',
                emdong_name: '효자동',
                population: 15000,
                area: 1.5
            },
            {
                code: '11010105',
                emdong_name: '창신동',
                population: 18000,
                area: 1.8
            },
            {
                code: '11010106',
                emdong_name: '숭인동',
                population: 22000,
                area: 2.2
            },
            {
                code: '11010107',
                emdong_name: '이화동',
                population: 16000,
                area: 1.6
            },
            {
                code: '11010108',
                emdong_name: '혜화동',
                population: 14000,
                area: 1.4
            },
            {
                code: '11010109',
                emdong_name: '명륜동',
                population: 12000,
                area: 1.2
            },
            {
                code: '11010110',
                emdong_name: '와룡동',
                population: 10000,
                area: 1.0
            },
            {
                code: '11010111',
                emdong_name: '무악동',
                population: 13000,
                area: 1.3
            },
            {
                code: '11010112',
                emdong_name: '교남동',
                population: 11000,
                area: 1.1
            },
            {
                code: '11010113',
                emdong_name: '평창동',
                population: 17000,
                area: 1.7
            },
            {
                code: '11010114',
                emdong_name: '부암동',
                population: 19000,
                area: 1.9
            },
            {
                code: '11010115',
                emdong_name: '삼청동',
                population: 7000,
                area: 0.7
            },
            {
                code: '11010116',
                emdong_name: '가회동',
                population: 5000,
                area: 0.5
            },
            {
                code: '11010117',
                emdong_name: '종로동',
                population: 9000,
                area: 0.9
            }
        ]
    };
    
    res.status(200).json(emdongData);
}
