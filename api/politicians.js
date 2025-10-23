// 정치인 리스트 API - 용량 최적화 버전
const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

// 데이터 캐시
let politicianCache = null;
let cacheTimestamp = null;
const CACHE_DURATION = 5 * 60 * 1000; // 5분

// 압축된 JSON 파일 로드
function loadCompressedJson(filename) {
    const filePath = path.join(__dirname, '..', 'data', filename);
    
    try {
        if (fs.existsSync(filePath + '.gz')) {
            const compressed = fs.readFileSync(filePath + '.gz');
            const decompressed = zlib.gunzipSync(compressed);
            return JSON.parse(decompressed.toString());
        } else if (fs.existsSync(filePath)) {
            return JSON.parse(fs.readFileSync(filePath, 'utf8'));
        }
    } catch (error) {
        console.error(`Error loading ${filename}:`, error);
    }
    return null;
}

// 정치인 데이터 최적화
function optimizePoliticianData(rawData) {
    if (!rawData) return null;
    
    return {
        metadata: {
            total_count: rawData.length,
            last_updated: new Date().toISOString(),
            version: "1.0"
        },
        politicians: rawData.map(politician => ({
            id: politician.id || politician.name?.replace(/\s+/g, '_'),
            name: politician.name,
            position: politician.position || politician.title,
            party: politician.party,
            region: politician.region || politician.district,
            term: politician.term,
            // LDA 결과 요약 (상위 3개 토픽만)
            top_topics: politician.lda_results?.topics?.slice(0, 3).map(topic => ({
                id: topic.id,
                name: topic.name,
                weight: Math.round(topic.weight * 100) / 100
            })) || []
        }))
    };
}

// LDA 결과 최적화
function optimizeLDAResults(rawData) {
    if (!rawData) return null;
    
    return {
        metadata: {
            total_topics: rawData.topics?.length || 0,
            analysis_date: rawData.analysis_date || new Date().toISOString(),
            version: "1.0"
        },
        topics: rawData.topics?.map(topic => ({
            id: topic.id,
            name: topic.name,
            keywords: topic.keywords?.slice(0, 10), // 상위 10개 키워드만
            weight: Math.round(topic.weight * 100) / 100,
            politician_count: topic.politicians?.length || 0
        })) || [],
        politicians: rawData.politicians?.map(politician => ({
            id: politician.id,
            name: politician.name,
            top_topics: politician.topics?.slice(0, 3).map(topic => ({
                id: topic.id,
                name: topic.name,
                weight: Math.round(topic.weight * 100) / 100
            })) || []
        })) || []
    };
}

// 정치인 리스트 API
function getPoliticiansList(req, res) {
    try {
        // 캐시 확인
        const now = Date.now();
        if (politicianCache && cacheTimestamp && (now - cacheTimestamp) < CACHE_DURATION) {
            return res.json(politicianCache);
        }

        // 데이터 로드
        const rawData = loadCompressedJson('politicians_sample.json');
        const optimizedData = optimizePoliticianData(rawData);
        
        if (!optimizedData) {
            return res.status(404).json({ error: 'Politician data not found' });
        }

        // 캐시 업데이트
        politicianCache = optimizedData;
        cacheTimestamp = now;

        res.json(optimizedData);
    } catch (error) {
        console.error('Error in getPoliticiansList:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
}

// 정치인 상세 정보 API
function getPoliticianDetail(req, res) {
    try {
        const { id } = req.params;
        
        const rawData = loadCompressedJson('politicians_sample.json');
        if (!rawData) {
            return res.status(404).json({ error: 'Politician data not found' });
        }

        const politician = rawData.find(p => 
            p.id === id || p.name?.replace(/\s+/g, '_') === id
        );

        if (!politician) {
            return res.status(404).json({ error: 'Politician not found' });
        }

        // 상세 정보 최적화
        const optimizedPolitician = {
            id: politician.id || politician.name?.replace(/\s+/g, '_'),
            name: politician.name,
            position: politician.position || politician.title,
            party: politician.party,
            region: politician.region || politician.district,
            term: politician.term,
            // 전체 LDA 결과
            lda_analysis: {
                topics: politician.lda_results?.topics?.map(topic => ({
                    id: topic.id,
                    name: topic.name,
                    weight: Math.round(topic.weight * 100) / 100,
                    keywords: topic.keywords?.slice(0, 15) // 상위 15개 키워드
                })) || [],
                analysis_date: politician.lda_results?.analysis_date,
                confidence: politician.lda_results?.confidence
            }
        };

        res.json(optimizedPolitician);
    } catch (error) {
        console.error('Error in getPoliticianDetail:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
}

// LDA 분석 결과 API
function getLDAResults(req, res) {
    try {
        const { politician_id } = req.query;
        
        const rawData = loadCompressedJson('lda_results_sample.json');
        const optimizedData = optimizeLDAResults(rawData);
        
        if (!optimizedData) {
            return res.status(404).json({ error: 'LDA results not found' });
        }

        // 특정 정치인 필터링
        if (politician_id) {
            const politician = optimizedData.politicians.find(p => p.id === politician_id);
            if (politician) {
                return res.json({
                    metadata: optimizedData.metadata,
                    politician: politician
                });
            }
        }

        res.json(optimizedData);
    } catch (error) {
        console.error('Error in getLDAResults:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
}

// 토픽 상세 정보 API
function getTopicDetail(req, res) {
    try {
        const { topic_id } = req.params;
        
        const rawData = loadCompressedJson('lda_results_sample.json');
        if (!rawData) {
            return res.status(404).json({ error: 'LDA results not found' });
        }

        const topic = rawData.topics?.find(t => t.id === topic_id);
        if (!topic) {
            return res.status(404).json({ error: 'Topic not found' });
        }

        // 토픽 상세 정보 최적화
        const optimizedTopic = {
            id: topic.id,
            name: topic.name,
            description: topic.description,
            keywords: topic.keywords?.slice(0, 20), // 상위 20개 키워드
            weight: Math.round(topic.weight * 100) / 100,
            politicians: topic.politicians?.map(p => ({
                id: p.id,
                name: p.name,
                weight: Math.round(p.weight * 100) / 100
            })) || [],
            analysis_date: topic.analysis_date
        };

        res.json(optimizedTopic);
    } catch (error) {
        console.error('Error in getTopicDetail:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
}

module.exports = {
    getPoliticiansList,
    getPoliticianDetail,
    getLDAResults,
    getTopicDetail
};
