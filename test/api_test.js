// API 테스트 스크립트
const http = require('http');
const fs = require('fs');
const path = require('path');

const API_BASE = 'http://localhost:3000';

// HTTP 요청 헬퍼
function makeRequest(path, method = 'GET') {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'localhost',
            port: 3000,
            path: path,
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        const req = http.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => {
                data += chunk;
            });
            res.on('end', () => {
                try {
                    const jsonData = JSON.parse(data);
                    resolve({
                        status: res.statusCode,
                        data: jsonData,
                        headers: res.headers
                    });
                } catch (error) {
                    resolve({
                        status: res.statusCode,
                        data: data,
                        headers: res.headers
                    });
                }
            });
        });

        req.on('error', (error) => {
            reject(error);
        });

        req.end();
    });
}

// 테스트 실행
async function runTests() {
    console.log('🧪 NewsAnalyzer API 테스트 시작\n');

    const tests = [
        {
            name: '서버 상태 확인',
            test: async () => {
                const result = await makeRequest('/api/health');
                console.log('✅ 서버 상태:', result.status === 200 ? '정상' : '오류');
                return result.status === 200;
            }
        },
        {
            name: '정치인 리스트 API',
            test: async () => {
                const result = await makeRequest('/api/politicians');
                console.log('✅ 정치인 리스트:', result.status === 200 ? '성공' : '실패');
                if (result.status === 200) {
                    console.log(`   - 총 정치인 수: ${result.data.politicians?.length || 0}명`);
                    console.log(`   - 메타데이터: ${JSON.stringify(result.data.metadata)}`);
                }
                return result.status === 200;
            }
        },
        {
            name: '정치인 상세 정보 API',
            test: async () => {
                const result = await makeRequest('/api/politicians/kim_dong_yeon');
                console.log('✅ 정치인 상세:', result.status === 200 ? '성공' : '실패');
                if (result.status === 200) {
                    console.log(`   - 이름: ${result.data.name}`);
                    console.log(`   - 직책: ${result.data.position}`);
                    console.log(`   - 정당: ${result.data.party}`);
                    console.log(`   - LDA 토픽 수: ${result.data.lda_analysis?.topics?.length || 0}개`);
                }
                return result.status === 200;
            }
        },
        {
            name: 'LDA 분석 결과 API',
            test: async () => {
                const result = await makeRequest('/api/lda');
                console.log('✅ LDA 결과:', result.status === 200 ? '성공' : '실패');
                if (result.status === 200) {
                    console.log(`   - 총 토픽 수: ${result.data.topics?.length || 0}개`);
                    console.log(`   - 정치인 수: ${result.data.politicians?.length || 0}명`);
                    console.log(`   - 메타데이터: ${JSON.stringify(result.data.metadata)}`);
                }
                return result.status === 200;
            }
        },
        {
            name: '특정 정치인 LDA 결과',
            test: async () => {
                const result = await makeRequest('/api/lda?politician_id=kim_dong_yeon');
                console.log('✅ 특정 정치인 LDA:', result.status === 200 ? '성공' : '실패');
                if (result.status === 200) {
                    console.log(`   - 정치인: ${result.data.politician?.name}`);
                    console.log(`   - 토픽 수: ${result.data.politician?.top_topics?.length || 0}개`);
                }
                return result.status === 200;
            }
        },
        {
            name: '토픽 상세 정보 API',
            test: async () => {
                const result = await makeRequest('/api/lda/topics/topic_1');
                console.log('✅ 토픽 상세:', result.status === 200 ? '성공' : '실패');
                if (result.status === 200) {
                    console.log(`   - 토픽명: ${result.data.name}`);
                    console.log(`   - 키워드 수: ${result.data.keywords?.length || 0}개`);
                    console.log(`   - 정치인 수: ${result.data.politicians?.length || 0}명`);
                }
                return result.status === 200;
            }
        },
        {
            name: '데이터 압축 확인',
            test: async () => {
                const result = await makeRequest('/api/politicians');
                if (result.status === 200) {
                    const contentLength = result.headers['content-length'];
                    const contentEncoding = result.headers['content-encoding'];
                    console.log('✅ 압축 상태:', contentEncoding === 'gzip' ? '압축됨' : '압축 안됨');
                    console.log(`   - 응답 크기: ${contentLength} bytes`);
                    return true;
                }
                return false;
            }
        }
    ];

    let passed = 0;
    let total = tests.length;

    for (const test of tests) {
        try {
            console.log(`\n🔍 ${test.name} 테스트 중...`);
            const success = await test.test();
            if (success) {
                passed++;
                console.log(`✅ ${test.name}: 통과`);
            } else {
                console.log(`❌ ${test.name}: 실패`);
            }
        } catch (error) {
            console.log(`❌ ${test.name}: 오류 - ${error.message}`);
        }
    }

    console.log(`\n📊 테스트 결과: ${passed}/${total} 통과`);
    
    if (passed === total) {
        console.log('🎉 모든 테스트가 성공적으로 완료되었습니다!');
    } else {
        console.log('⚠️ 일부 테스트가 실패했습니다. 서버 상태를 확인해주세요.');
    }
}

// 서버가 실행 중인지 확인
async function checkServer() {
    try {
        const result = await makeRequest('/api/health');
        return result.status === 200;
    } catch (error) {
        return false;
    }
}

// 메인 실행
async function main() {
    console.log('🚀 NewsAnalyzer API 테스트 시작');
    console.log('📍 테스트 대상: http://localhost:3000');
    
    // 서버 상태 확인
    const serverRunning = await checkServer();
    if (!serverRunning) {
        console.log('❌ 서버가 실행되지 않았습니다.');
        console.log('💡 다음 명령어로 서버를 시작하세요:');
        console.log('   npm start');
        return;
    }
    
    console.log('✅ 서버가 실행 중입니다.');
    
    // 테스트 실행
    await runTests();
}

main().catch(console.error);
