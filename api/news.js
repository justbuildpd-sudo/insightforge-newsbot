// News data API endpoint
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
    
    const { region_code, politician_id, date_range } = req.query;
    
    // 샘플 뉴스 데이터
    const newsData = {
        region_code: region_code || '11',
        politician_id: politician_id || null,
        date_range: date_range || '30d',
        articles: [
            {
                id: 1,
                title: '서울시 디지털 정책 추진 현황',
                content: '서울시가 디지털 전환 정책을 통해 시민 서비스를 개선하고 있습니다...',
                source: '서울신문',
                date: '2024-10-20',
                sentiment: 'positive',
                keywords: ['디지털', '정책', '서울시', '시민서비스'],
                politician_mentions: ['김철수'],
                region_mentions: ['서울특별시']
            },
            {
                id: 2,
                title: '종로구 문화재 보존 정책 논의',
                content: '종로구에서 역사적 문화재 보존을 위한 새로운 정책을 논의하고 있습니다...',
                source: '문화일보',
                date: '2024-10-19',
                sentiment: 'neutral',
                keywords: ['문화재', '보존', '종로구', '역사'],
                politician_mentions: ['이영희'],
                region_mentions: ['종로구']
            },
            {
                id: 3,
                title: '강남구 스마트시티 구축 성과',
                content: '강남구의 스마트시티 구축 프로젝트가 성공적으로 진행되고 있습니다...',
                source: 'IT조선',
                date: '2024-10-18',
                sentiment: 'positive',
                keywords: ['스마트시티', '강남구', '디지털', '혁신'],
                politician_mentions: ['박민수'],
                region_mentions: ['강남구']
            }
        ],
        statistics: {
            total_articles: 1234,
            positive_sentiment: 456,
            negative_sentiment: 123,
            neutral_sentiment: 655,
            average_sentiment: 0.2 // -1 to 1 scale
        },
        trends: [
            { date: '2024-10-15', article_count: 45, sentiment: 0.3 },
            { date: '2024-10-16', article_count: 52, sentiment: 0.1 },
            { date: '2024-10-17', article_count: 48, sentiment: 0.4 },
            { date: '2024-10-18', article_count: 56, sentiment: 0.2 },
            { date: '2024-10-19', article_count: 43, sentiment: 0.1 },
            { date: '2024-10-20', article_count: 49, sentiment: 0.3 }
        ],
        top_keywords: [
            { keyword: '디지털', count: 123, trend: 'up' },
            { keyword: '정책', count: 98, trend: 'stable' },
            { keyword: '시민', count: 87, trend: 'up' },
            { keyword: '서울시', count: 76, trend: 'stable' },
            { keyword: '혁신', count: 65, trend: 'up' }
        ]
    };
    
    res.status(200).json(newsData);
}
