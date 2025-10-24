// Emdong (읍면동) data API endpoint
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
    
    // 종로구 읍면동 데이터
    if (sigungu_code === '11010') {
        const emdongData = {
            emdong_list: [
                { code: "11010530", emdong_name: "청운효자동" },
                { code: "11010540", emdong_name: "사직동" },
                { code: "11010550", emdong_name: "삼청동" },
                { code: "11010560", emdong_name: "부암동" },
                { code: "11010570", emdong_name: "평창동" },
                { code: "11010580", emdong_name: "무악동" },
                { code: "11010600", emdong_name: "교남동" },
                { code: "11010610", emdong_name: "가회동" },
                { code: "11010630", emdong_name: "종로1.2.3.4가동" },
                { code: "11010640", emdong_name: "종로5.6가동" },
                { code: "11010650", emdong_name: "이화동" },
                { code: "11010670", emdong_name: "혜화동" },
                { code: "11010680", emdong_name: "창신1동" },
                { code: "11010690", emdong_name: "창신2동" },
                { code: "11010700", emdong_name: "창신3동" },
                { code: "11010710", emdong_name: "숭인1동" },
                { code: "11010720", emdong_name: "숭인2동" }
            ]
        };
        res.status(200).json(emdongData);
    } else {
        res.status(404).json({ error: 'Emdong data not found for the given sigungu_code' });
    }
}
