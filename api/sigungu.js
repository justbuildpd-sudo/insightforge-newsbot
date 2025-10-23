// Sigungu (시군구) data API endpoint
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
    
    // 서울특별시 시군구 데이터
    if (sido_code === '11') {
        const sigunguData = {
            sigungu_list: [
                { code: "11010", sigungu_name: "종로구", total_regions: 17 },
                { code: "11020", sigungu_name: "중구", total_regions: 15 },
                { code: "11030", sigungu_name: "용산구", total_regions: 16 },
                { code: "11040", sigungu_name: "성동구", total_regions: 17 },
                { code: "11050", sigungu_name: "광진구", total_regions: 15 },
                { code: "11060", sigungu_name: "동대문구", total_regions: 14 },
                { code: "11070", sigungu_name: "중랑구", total_regions: 16 },
                { code: "11080", sigungu_name: "성북구", total_regions: 20 },
                { code: "11090", sigungu_name: "강북구", total_regions: 13 },
                { code: "11100", sigungu_name: "도봉구", total_regions: 14 },
                { code: "11110", sigungu_name: "노원구", total_regions: 19 },
                { code: "11120", sigungu_name: "은평구", total_regions: 16 },
                { code: "11130", sigungu_name: "서대문구", total_regions: 14 },
                { code: "11140", sigungu_name: "마포구", total_regions: 16 },
                { code: "11150", sigungu_name: "양천구", total_regions: 18 },
                { code: "11160", sigungu_name: "강서구", total_regions: 20 },
                { code: "11170", sigungu_name: "구로구", total_regions: 15 },
                { code: "11180", sigungu_name: "금천구", total_regions: 10 },
                { code: "11190", sigungu_name: "영등포구", total_regions: 18 },
                { code: "11200", sigungu_name: "동작구", total_regions: 15 },
                { code: "11210", sigungu_name: "관악구", total_regions: 21 },
                { code: "11220", sigungu_name: "서초구", total_regions: 18 },
                { code: "11230", sigungu_name: "강남구", total_regions: 22 },
                { code: "11240", sigungu_name: "송파구", total_regions: 27 },
                { code: "11250", sigungu_name: "강동구", total_regions: 18 }
            ]
        };
        res.status(200).json(sigunguData);
    } else {
        res.status(404).json({ error: 'Sigungu data not found for the given sido_code' });
    }
}
