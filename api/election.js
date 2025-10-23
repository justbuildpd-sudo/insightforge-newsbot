// Election data API endpoint
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
    
    const { region_code, election_type } = req.query;
    
    // 샘플 선거 데이터
    const electionData = {
        region_code: region_code || '11',
        election_type: election_type || 'local',
        elections: [
            {
                id: 1,
                name: '제8회 전국동시지방선거',
                date: '2022-06-01',
                type: 'local',
                results: {
                    mayor: {
                        name: '김철수',
                        party: '더불어민주당',
                        votes: 2456789,
                        percentage: 56.7
                    },
                    council: {
                        total_seats: 25,
                        parties: [
                            { name: '더불어민주당', seats: 15, percentage: 60.0 },
                            { name: '국민의힘', seats: 8, percentage: 32.0 },
                            { name: '정의당', seats: 2, percentage: 8.0 }
                        ]
                    }
                }
            },
            {
                id: 2,
                name: '제21대 국회의원선거',
                date: '2020-04-15',
                type: 'national',
                results: {
                    assembly_members: [
                        {
                            name: '이영희',
                            party: '더불어민주당',
                            district: '서울 종로구',
                            votes: 45678,
                            percentage: 52.3
                        },
                        {
                            name: '박민수',
                            party: '국민의힘',
                            district: '서울 중구',
                            votes: 38945,
                            percentage: 48.7
                        }
                    ]
                }
            }
        ],
        statistics: {
            total_voters: 4567890,
            turnout_rate: 67.8,
            participation_rate: 72.3
        }
    };
    
    res.status(200).json(electionData);
}
