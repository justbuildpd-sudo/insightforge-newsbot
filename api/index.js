// Vercel 서버리스 함수 - 메인 API 엔드포인트
export default function handler(req, res) {
    // CORS 설정
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    
    // 기본 응답
    if (req.method !== 'GET') {
        res.status(405).json({ error: 'Method not allowed' });
        return;
    }
    
    // API 정보
    const apiInfo = {
        status: 'ok',
        message: 'InsightForge API Server',
        version: '3.2.0',
        timestamp: new Date().toISOString(),
        endpoints: {
            health: '/api/health',
            sido: '/api/sido',
            sigungu: '/api/sigungu',
            emdong: '/api/emdong',
            politicians: '/api/politicians',
            lda: '/api/lda',
            population: '/api/population',
            election: '/api/election',
            gdp: '/api/gdp',
            real_estate: '/api/real_estate',
            education: '/api/education',
            welfare: '/api/welfare',
            safety: '/api/safety',
            traffic: '/api/traffic',
            news: '/api/news',
            comprehensive: '/api/comprehensive'
        }
    };
    
    res.status(200).json(apiInfo);
}