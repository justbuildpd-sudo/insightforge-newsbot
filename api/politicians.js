// Politicians data API endpoint
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
    
    // 샘플 정치인 데이터
    const politiciansData = {
        politicians: [
            {
                id: 1,
                name: '김철수',
                position: '서울특별시장',
                party: '더불어민주당',
                term: '2022-2026',
                region: '서울특별시',
                profile_image: '/images/politician1.jpg',
                description: '서울특별시장으로서 도시 발전에 기여하고 있습니다.',
                achievements: [
                    '서울시 디지털 정책 추진',
                    '친환경 도시 조성',
                    '시민 참여 정책 확대'
                ]
            },
            {
                id: 2,
                name: '이영희',
                position: '국회의원',
                party: '국민의힘',
                term: '2020-2024',
                region: '서울 종로구',
                profile_image: '/images/politician2.jpg',
                description: '종로구 국회의원으로서 지역 발전에 힘쓰고 있습니다.',
                achievements: [
                    '지역 경제 활성화',
                    '문화재 보존 정책',
                    '청년 일자리 창출'
                ]
            },
            {
                id: 3,
                name: '박민수',
                position: '구청장',
                party: '더불어민주당',
                term: '2022-2026',
                region: '서울 강남구',
                profile_image: '/images/politician3.jpg',
                description: '강남구청장으로서 혁신적인 구정을 펼치고 있습니다.',
                achievements: [
                    '스마트시티 구축',
                    '주민 복지 향상',
                    '교통 체계 개선'
                ]
            },
            {
                id: 4,
                name: '정수진',
                position: '시의원',
                party: '국민의힘',
                term: '2022-2026',
                region: '서울 중구',
                profile_image: '/images/politician4.jpg',
                description: '중구 시의원으로서 지역 상권 활성화에 기여하고 있습니다.',
                achievements: [
                    '상권 활성화 정책',
                    '관광 산업 발전',
                    '주민 소통 강화'
                ]
            },
            {
                id: 5,
                name: '최동호',
                position: '구의원',
                party: '더불어민주당',
                term: '2022-2026',
                region: '서울 마포구',
                profile_image: '/images/politician5.jpg',
                description: '마포구 구의원으로서 문화 예술 정책을 추진하고 있습니다.',
                achievements: [
                    '문화 예술 지원 확대',
                    '청년 창업 지원',
                    '환경 보호 정책'
                ]
            }
        ],
        total_count: 5
    };
    
    res.status(200).json(politiciansData);
}