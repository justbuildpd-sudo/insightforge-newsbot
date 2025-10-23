// LDA analysis API endpoint
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
    
    // 샘플 LDA 분석 결과
    const ldaData = {
        topics: [
            {
                id: 1,
                name: '도시 발전',
                keywords: ['도시계획', '개발', '인프라', '교통', '주거'],
                weight: 0.25,
                documents: 45,
                description: '도시 발전과 관련된 정책 및 계획에 대한 토픽'
            },
            {
                id: 2,
                name: '환경 보호',
                keywords: ['환경', '친환경', '대기질', '녹지', '재활용'],
                weight: 0.20,
                documents: 38,
                description: '환경 보호 및 친환경 정책에 대한 토픽'
            },
            {
                id: 3,
                name: '경제 활성화',
                keywords: ['경제', '일자리', '창업', '중소기업', '투자'],
                weight: 0.18,
                documents: 32,
                description: '경제 활성화 및 일자리 창출에 대한 토픽'
            },
            {
                id: 4,
                name: '복지 정책',
                keywords: ['복지', '보육', '노인', '장애인', '의료'],
                weight: 0.15,
                documents: 28,
                description: '사회 복지 및 보육 정책에 대한 토픽'
            },
            {
                id: 5,
                name: '교육 혁신',
                keywords: ['교육', '학교', '학생', '교사', '디지털'],
                weight: 0.12,
                documents: 22,
                description: '교육 혁신 및 디지털 교육에 대한 토픽'
            },
            {
                id: 6,
                name: '문화 예술',
                keywords: ['문화', '예술', '공연', '전시', '문화재'],
                weight: 0.10,
                documents: 18,
                description: '문화 예술 및 문화재 보존에 대한 토픽'
            }
        ],
        analysis_info: {
            total_documents: 183,
            total_topics: 6,
            analysis_date: '2024-10-23',
            model_version: '1.0.0',
            confidence_score: 0.85
        }
    };
    
    res.status(200).json(ldaData);
}
