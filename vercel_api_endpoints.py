#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vercel 배포용 API 엔드포인트 생성
행정동 단위 선거 데이터 및 영향력 분석 API
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class VercelAPIEndpoints:
    def __init__(self):
        self.api_dir = "api"
        self.data_dir = "vercel_optimized_data"
        os.makedirs(self.api_dir, exist_ok=True)
        
        # API 엔드포인트 매핑
        self.endpoints = {
            "dong_list": "/api/dong-list",
            "dong_elections": "/api/dong-elections",
            "timeline_analysis": "/api/timeline-analysis",
            "lda_correlation": "/api/lda-correlation",
            "influence_analysis": "/api/influence-analysis",
            "regional_issues": "/api/regional-issues",
            "statistical_changes": "/api/statistical-changes",
            "district_changes": "/api/district-changes",
            "election_results": "/api/election-results"
        }

    def create_dong_list_api(self, dong_data: Dict[str, Any]) -> str:
        """행정동 목록 API 생성"""
        api_content = f'''import {{ NextRequest, NextResponse }} from 'next/server';

// 행정동 목록 데이터
const dongData = {json.dumps(dong_data, ensure_ascii=False, indent=2)};

export async function GET(request: NextRequest) {{
    try {{
        const {{ searchParams }} = new URL(request.url);
        const sido = searchParams.get('sido');
        const gu = searchParams.get('gu');
        
        let filteredDongs = Object.values(dongData.dong_data || {{}});
        
        if (sido) {{
            filteredDongs = filteredDongs.filter((dong: any) => dong.sido_name === sido);
        }}
        
        if (gu) {{
            filteredDongs = filteredDongs.filter((dong: any) => dong.gu_name === gu);
        }}
        
        const dongList = filteredDongs.map((dong: any) => ({{
            dong_code: dong.dong_code,
            dong_name: dong.dong_name,
            gu_name: dong.gu_name,
            sido_name: dong.sido_name,
            election_count: dong.elections?.length || 0,
            candidate_count: dong.elections?.reduce((sum: number, e: any) => sum + (e.candidate_count || 0), 0) || 0
        }}));
        
        return NextResponse.json({{
            success: true,
            data: dongList,
            total: dongList.length,
            filters: {{ sido, gu }}
        }});
    }} catch (error) {{
        return NextResponse.json({{
            success: false,
            error: '행정동 목록 조회 실패',
            message: error instanceof Error ? error.message : 'Unknown error'
        }}, {{ status: 500 }});
    }}
}}'''
        
        api_file = f"{self.api_dir}/dong-list/route.ts"
        os.makedirs(os.path.dirname(api_file), exist_ok=True)
        
        with open(api_file, "w", encoding="utf-8") as f:
            f.write(api_content)
        
        logger.info(f"행정동 목록 API 생성 완료: {api_file}")
        return api_file

    def create_dong_elections_api(self, dong_data: Dict[str, Any]) -> str:
        """행정동 선거 데이터 API 생성"""
        api_content = f'''import {{ NextRequest, NextResponse }} from 'next/server';

// 행정동 선거 데이터
const dongData = {json.dumps(dong_data, ensure_ascii=False, indent=2)};

export async function GET(request: NextRequest) {{
    try {{
        const {{ searchParams }} = new URL(request.url);
        const dongCode = searchParams.get('dong_code');
        const electionId = searchParams.get('election_id');
        
        if (!dongCode) {{
            return NextResponse.json({{
                success: false,
                error: 'dong_code 파라미터가 필요합니다'
            }}, {{ status: 400 }});
        }}
        
        // 행정동 데이터 찾기
        const dongInfo = Object.values(dongData.dong_data || {{}}).find((dong: any) => dong.dong_code === dongCode);
        
        if (!dongInfo) {{
            return NextResponse.json({{
                success: false,
                error: '해당 행정동을 찾을 수 없습니다'
            }}, {{ status: 404 }});
        }}
        
        let elections = dongInfo.elections || [];
        
        if (electionId) {{
            elections = elections.filter((e: any) => e.election_id === electionId);
        }}
        
        return NextResponse.json({{
            success: true,
            data: {{
                dong_info: {{
                    dong_code: dongInfo.dong_code,
                    dong_name: dongInfo.dong_name,
                    gu_name: dongInfo.gu_name,
                    sido_name: dongInfo.sido_name
                }},
                elections: elections,
                total_elections: elections.length
            }}
        }});
    }} catch (error) {{
        return NextResponse.json({{
            success: false,
            error: '행정동 선거 데이터 조회 실패',
            message: error instanceof Error ? error.message : 'Unknown error'
        }}, {{ status: 500 }});
    }}
}}'''
        
        api_file = f"{self.api_dir}/dong-elections/route.ts"
        os.makedirs(os.path.dirname(api_file), exist_ok=True)
        
        with open(api_file, "w", encoding="utf-8") as f:
            f.write(api_content)
        
        logger.info(f"행정동 선거 데이터 API 생성 완료: {api_file}")
        return api_file

    def create_timeline_analysis_api(self, dong_data: Dict[str, Any]) -> str:
        """시계열 분석 API 생성"""
        api_content = f'''import {{ NextRequest, NextResponse }} from 'next/server';

// 시계열 분석 데이터
const timelineData = {json.dumps(dong_data.get('timeline_analysis', {}), ensure_ascii=False, indent=2)};

export async function GET(request: NextRequest) {{
    try {{
        const {{ searchParams }} = new URL(request.url);
        const dongCode = searchParams.get('dong_code');
        const analysisType = searchParams.get('type') || 'all';
        
        let analysisData = timelineData;
        
        if (dongCode) {{
            analysisData = {{
                election_frequency: timelineData.election_frequency?.[dongCode] || {{}},
                party_evolution: timelineData.party_evolution?.[dongCode] || {{}},
                demographic_trends: timelineData.demographic_trends?.[dongCode] || {{}}
            }};
        }}
        
        if (analysisType !== 'all') {{
            analysisData = {{ [analysisType]: analysisData[analysisType] || {{}} }};
        }}
        
        return NextResponse.json({{
            success: true,
            data: analysisData,
            analysis_type: analysisType,
            dong_code: dongCode
        }});
    }} catch (error) {{
        return NextResponse.json({{
            success: false,
            error: '시계열 분석 조회 실패',
            message: error instanceof Error ? error.message : 'Unknown error'
        }}, {{ status: 500 }});
    }}
}}'''
        
        api_file = f"{self.api_dir}/timeline-analysis/route.ts"
        os.makedirs(os.path.dirname(api_file), exist_ok=True)
        
        with open(api_file, "w", encoding="utf-8") as f:
            f.write(api_content)
        
        logger.info(f"시계열 분석 API 생성 완료: {api_file}")
        return api_file

    def create_lda_correlation_api(self, dong_data: Dict[str, Any]) -> str:
        """LDA 상관관계 API 생성"""
        api_content = f'''import {{ NextRequest, NextResponse }} from 'next/server';

// LDA 상관관계 데이터
const ldaData = {json.dumps(dong_data.get('lda_correlation', {}), ensure_ascii=False, indent=2)};

export async function GET(request: NextRequest) {{
    try {{
        const {{ searchParams }} = new URL(request.url);
        const year = searchParams.get('year');
        const dongCode = searchParams.get('dong_code');
        
        let correlationData = ldaData;
        
        if (year) {{
            correlationData = ldaData.timeline_matching?.[year] || {{}};
        }}
        
        if (dongCode) {{
            // 특정 행정동의 LDA 상관관계 필터링
            const filteredData = {{}};
            for (const [year, data] of Object.entries(ldaData.timeline_matching || {{}})) {{
                const matchingElections = data.matching_elections?.filter((item: any) => 
                    item.dong === dongCode
                ) || [];
                if (matchingElections.length > 0) {{
                    filteredData[year] = {{
                        ...data,
                        matching_elections: matchingElections
                    }};
                }}
            }}
            correlationData = filteredData;
        }}
        
        return NextResponse.json({{
            success: true,
            data: correlationData,
            year: year,
            dong_code: dongCode
        }});
    }} catch (error) {{
        return NextResponse.json({{
            success: false,
            error: 'LDA 상관관계 조회 실패',
            message: error instanceof Error ? error.message : 'Unknown error'
        }}, {{ status: 500 }});
    }}
}}'''
        
        api_file = f"{self.api_dir}/lda-correlation/route.ts"
        os.makedirs(os.path.dirname(api_file), exist_ok=True)
        
        with open(api_file, "w", encoding="utf-8") as f:
            f.write(api_content)
        
        logger.info(f"LDA 상관관계 API 생성 완료: {api_file}")
        return api_file

    def create_influence_analysis_api(self, influence_data: Dict[str, Any]) -> str:
        """영향력 분석 API 생성"""
        api_content = f'''import {{ NextRequest, NextResponse }} from 'next/server';

// 영향력 분석 데이터
const influenceData = {json.dumps(influence_data, ensure_ascii=False, indent=2)};

export async function GET(request: NextRequest) {{
    try {{
        const {{ searchParams }} = new URL(request.url);
        const analysisType = searchParams.get('type') || 'all';
        const dongCode = searchParams.get('dong_code');
        
        let analysisData = influenceData;
        
        if (analysisType !== 'all') {{
            analysisData = {{ [analysisType]: influenceData[analysisType] || {{}} }};
        }}
        
        if (dongCode) {{
            // 특정 행정동의 영향력 분석 필터링
            const filteredData = {{}};
            for (const [type, data] of Object.entries(analysisData)) {{
                if (typeof data === 'object' && data !== null) {{
                    filteredData[type] = data[dongCode] || {{}};
                }}
            }}
            analysisData = filteredData;
        }}
        
        return NextResponse.json({{
            success: true,
            data: analysisData,
            analysis_type: analysisType,
            dong_code: dongCode
        }});
    }} catch (error) {{
        return NextResponse.json({{
            success: false,
            error: '영향력 분석 조회 실패',
            message: error instanceof Error ? error.message : 'Unknown error'
        }}, {{ status: 500 }});
    }}
}}'''
        
        api_file = f"{self.api_dir}/influence-analysis/route.ts"
        os.makedirs(os.path.dirname(api_file), exist_ok=True)
        
        with open(api_file, "w", encoding="utf-8") as f:
            f.write(api_content)
        
        logger.info(f"영향력 분석 API 생성 완료: {api_file}")
        return api_file

    def create_vercel_config(self) -> str:
        """Vercel 설정 파일 생성"""
        vercel_config = {
            "version": 2,
            "builds": [
                {
                    "src": "api/**/*.ts",
                    "use": "@vercel/node"
                }
            ],
            "routes": [
                {
                    "src": "/api/(.*)",
                    "dest": "/api/$1"
                }
            ],
            "functions": {
                "api/dong-list/route.ts": {
                    "maxDuration": 10
                },
                "api/dong-elections/route.ts": {
                    "maxDuration": 10
                },
                "api/timeline-analysis/route.ts": {
                    "maxDuration": 15
                },
                "api/lda-correlation/route.ts": {
                    "maxDuration": 15
                },
                "api/influence-analysis/route.ts": {
                    "maxDuration": 20
                }
            }
        }
        
        config_file = "vercel.json"
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(vercel_config, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Vercel 설정 파일 생성 완료: {config_file}")
        return config_file

    def create_package_json(self) -> str:
        """package.json 생성"""
        package_json = {
            "name": "election-analysis-api",
            "version": "1.0.0",
            "description": "행정동 단위 선거 데이터 및 영향력 분석 API",
            "main": "index.js",
            "scripts": {
                "dev": "vercel dev",
                "build": "next build",
                "start": "next start",
                "deploy": "vercel --prod"
            },
            "dependencies": {
                "next": "^14.0.0",
                "@vercel/node": "^3.0.0",
                "typescript": "^5.0.0",
                "@types/node": "^20.0.0"
            },
            "devDependencies": {
                "@types/react": "^18.0.0",
                "@types/react-dom": "^18.0.0"
            }
        }
        
        package_file = "package.json"
        with open(package_file, "w", encoding="utf-8") as f:
            json.dump(package_json, f, ensure_ascii=False, indent=2)
        
        logger.info(f"package.json 생성 완료: {package_file}")
        return package_file

    def create_readme(self) -> str:
        """README.md 생성"""
        readme_content = """# 선거 데이터 분석 API

## 개요
행정동 단위 선거 데이터 및 영향력 분석을 위한 Vercel 배포 API

## API 엔드포인트

### 1. 행정동 목록 조회
```
GET /api/dong-list
```
- **파라미터**: 
  - `sido`: 시도명 (선택)
  - `gu`: 구명 (선택)
- **응답**: 행정동 목록 및 기본 정보

### 2. 행정동 선거 데이터 조회
```
GET /api/dong-elections
```
- **파라미터**:
  - `dong_code`: 행정동 코드 (필수)
  - `election_id`: 선거 ID (선택)
- **응답**: 특정 행정동의 선거 데이터

### 3. 시계열 분석
```
GET /api/timeline-analysis
```
- **파라미터**:
  - `dong_code`: 행정동 코드 (선택)
  - `type`: 분석 유형 (선택)
- **응답**: 시계열 분석 결과

### 4. LDA 상관관계 분석
```
GET /api/lda-correlation
```
- **파라미터**:
  - `year`: 연도 (선택)
  - `dong_code`: 행정동 코드 (선택)
- **응답**: LDA 토픽과 선거 데이터 상관관계

### 5. 영향력 분석
```
GET /api/influence-analysis
```
- **파라미터**:
  - `type`: 분석 유형 (선택)
  - `dong_code`: 행정동 코드 (선택)
- **응답**: 종합 영향력 분석 결과

## 배포 방법

1. **의존성 설치**
```bash
npm install
```

2. **개발 서버 실행**
```bash
npm run dev
```

3. **Vercel 배포**
```bash
npm run deploy
```

## 데이터 구조

### 행정동 데이터
- `dong_code`: 행정동 코드
- `dong_name`: 행정동명
- `gu_name`: 구명
- `sido_name`: 시도명
- `elections`: 선거 데이터 배열

### 선거 데이터
- `election_id`: 선거 ID
- `election_name`: 선거명
- `election_type`: 선거 종류
- `candidates`: 후보자 정보
- `parties`: 정당 목록
- `demographic_analysis`: 인구통계학적 분석

## 분석 유형

1. **지역 이슈 분석**: 지역별 주요 이슈 및 변화 추이
2. **통계 변화 분석**: 인구, 경제, 사회, 환경 지표 변화
3. **선거구도 변화**: 선거구 경계 및 정치적 지리 변화
4. **선거 결과 영향**: 투표 패턴 및 정치적 변화 분석
5. **LDA 상관관계**: 토픽 모델링과 선거 데이터 상관관계

## 기술 스택

- **Backend**: Next.js API Routes
- **Deployment**: Vercel
- **Language**: TypeScript
- **Data**: JSON

## 라이선스

MIT License
"""
        
        readme_file = "README.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        logger.info(f"README.md 생성 완료: {readme_file}")
        return readme_file

    def create_all_apis(self, dong_data: Dict[str, Any], influence_data: Dict[str, Any]) -> List[str]:
        """모든 API 엔드포인트 생성"""
        created_files = []
        
        # API 엔드포인트 생성
        created_files.append(self.create_dong_list_api(dong_data))
        created_files.append(self.create_dong_elections_api(dong_data))
        created_files.append(self.create_timeline_analysis_api(dong_data))
        created_files.append(self.create_lda_correlation_api(dong_data))
        created_files.append(self.create_influence_analysis_api(influence_data))
        
        # 설정 파일 생성
        created_files.append(self.create_vercel_config())
        created_files.append(self.create_package_json())
        created_files.append(self.create_readme())
        
        logger.info(f"모든 API 엔드포인트 생성 완료: {len(created_files)}개 파일")
        return created_files

def main():
    """메인 실행 함수"""
    api_creator = VercelAPIEndpoints()
    
    # 데이터 파일 로드
    dong_data_file = "vercel_optimized_data/dong_election_analysis.json"
    influence_data_file = "influence_analysis/comprehensive_influence_analysis.json"
    
    if not os.path.exists(dong_data_file):
        logger.error(f"행정동 데이터 파일을 찾을 수 없습니다: {dong_data_file}")
        return
    
    if not os.path.exists(influence_data_file):
        logger.error(f"영향력 분석 데이터 파일을 찾을 수 없습니다: {influence_data_file}")
        return
    
    # 데이터 로드
    with open(dong_data_file, "r", encoding="utf-8") as f:
        dong_data = json.load(f)
    
    with open(influence_data_file, "r", encoding="utf-8") as f:
        influence_data = json.load(f)
    
    # 모든 API 생성
    created_files = api_creator.create_all_apis(dong_data, influence_data)
    
    logger.info("=== Vercel API 엔드포인트 생성 완료 ===")
    for file in created_files:
        logger.info(f"생성된 파일: {file}")

if __name__ == "__main__":
    main()
