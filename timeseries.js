// ============================================
// 시계열 그래프 (D3.js)
// ============================================

async function loadAndRenderTimeseries(emdongCode) {
    try {
        const response = await fetch(`${API_BASE}/api/emdong/${emdongCode}/timeseries`);
        const data = await response.json();
        
        if (!data.timeseries || data.timeseries.length === 0) {
            console.log('시계열 데이터 없음');
            return;
        }
        
        renderTimeseriesChart(data.timeseries);
        
    } catch (error) {
        console.error('시계열 데이터 로드 실패:', error);
    }
}

function renderTimeseriesChart(timeseriesData) {
    const container = document.getElementById('timeseriesChart');
    if (!container) return;
    
    // 컨테이너 초기화
    container.innerHTML = '';
    
    // 차트 크기
    const margin = {top: 40, right: 120, bottom: 60, left: 60};
    const width = container.clientWidth - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;
    
    // SVG 생성
    const svg = d3.select('#timeseriesChart')
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .style('background', 'white')
        .style('border-radius', '8px')
        .style('box-shadow', '0 1px 3px rgba(0,0,0,0.1)')
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // 날짜 파싱
    const parseDate = d3.timeParse('%Y-%m');
    timeseriesData.forEach(d => {
        d.parsedDate = parseDate(d.date);
    });
    
    // X축: 시간
    const x = d3.scaleTime()
        .domain(d3.extent(timeseriesData, d => d.parsedDate))
        .range([0, width]);
    
    // Y축: 인구
    const y = d3.scaleLinear()
        .domain([
            d3.min(timeseriesData, d => Math.min(d.population, d.male, d.female)) * 0.95,
            d3.max(timeseriesData, d => d.population) * 1.05
        ])
        .range([height, 0]);
    
    // X축 그리기
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x)
            .ticks(d3.timeMonth.every(1))
            .tickFormat(d3.timeFormat('%Y-%m')))
        .selectAll('text')
        .attr('transform', 'rotate(-45)')
        .style('text-anchor', 'end');
    
    // Y축 그리기
    svg.append('g')
        .call(d3.axisLeft(y)
            .tickFormat(d => d.toLocaleString()));
    
    // 라인 생성 함수
    const line = d3.line()
        .x(d => x(d.parsedDate))
        .y(d => y(d.population))
        .curve(d3.curveMonotoneX);
    
    const maleLine = d3.line()
        .x(d => x(d.parsedDate))
        .y(d => y(d.male))
        .curve(d3.curveMonotoneX);
    
    const femaleLine = d3.line()
        .x(d => x(d.parsedDate))
        .y(d => y(d.female))
        .curve(d3.curveMonotoneX);
    
    // 총 인구 라인
    svg.append('path')
        .datum(timeseriesData)
        .attr('fill', 'none')
        .attr('stroke', '#3b82f6')
        .attr('stroke-width', 3)
        .attr('d', line);
    
    // 남성 인구 라인
    svg.append('path')
        .datum(timeseriesData)
        .attr('fill', 'none')
        .attr('stroke', '#60a5fa')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5')
        .attr('d', maleLine);
    
    // 여성 인구 라인
    svg.append('path')
        .datum(timeseriesData)
        .attr('fill', 'none')
        .attr('stroke', '#f472b6')
        .attr('stroke-width', 2)
        .attr('stroke-dasharray', '5,5')
        .attr('d', femaleLine);
    
    // 데이터 포인트
    svg.selectAll('.dot')
        .data(timeseriesData)
        .enter()
        .append('circle')
        .attr('class', 'dot')
        .attr('cx', d => x(d.parsedDate))
        .attr('cy', d => y(d.population))
        .attr('r', 4)
        .attr('fill', '#3b82f6')
        .attr('stroke', 'white')
        .attr('stroke-width', 2)
        .on('mouseover', function(event, d) {
            // 툴팁 표시
            const tooltip = d3.select('body')
                .append('div')
                .attr('class', 'tooltip')
                .style('position', 'absolute')
                .style('background', 'white')
                .style('padding', '8px 12px')
                .style('border', '1px solid #ccc')
                .style('border-radius', '4px')
                .style('box-shadow', '0 2px 4px rgba(0,0,0,0.1)')
                .style('pointer-events', 'none')
                .style('font-size', '12px')
                .html(`
                    <div><strong>${d.date}</strong></div>
                    <div>총 인구: ${d.population.toLocaleString()}명</div>
                    <div>남성: ${d.male.toLocaleString()}명</div>
                    <div>여성: ${d.female.toLocaleString()}명</div>
                    <div>증감: ${d.change >= 0 ? '+' : ''}${d.change.toLocaleString()}명</div>
                `)
                .style('left', (event.pageX + 10) + 'px')
                .style('top', (event.pageY - 10) + 'px');
            
            d3.select(this)
                .attr('r', 6)
                .attr('fill', '#1e40af');
        })
        .on('mouseout', function() {
            d3.selectAll('.tooltip').remove();
            d3.select(this)
                .attr('r', 4)
                .attr('fill', '#3b82f6');
        });
    
    // 범례
    const legend = svg.append('g')
        .attr('transform', `translate(${width - 100}, 0)`);
    
    const legendData = [
        { label: '총 인구', color: '#3b82f6', dash: false },
        { label: '남성', color: '#60a5fa', dash: true },
        { label: '여성', color: '#f472b6', dash: true }
    ];
    
    legendData.forEach((item, i) => {
        const g = legend.append('g')
            .attr('transform', `translate(0, ${i * 20})`);
        
        g.append('line')
            .attr('x1', 0)
            .attr('x2', 20)
            .attr('y1', 9)
            .attr('y2', 9)
            .attr('stroke', item.color)
            .attr('stroke-width', 2)
            .attr('stroke-dasharray', item.dash ? '3,3' : '0');
        
        g.append('text')
            .attr('x', 25)
            .attr('y', 9)
            .attr('dy', '0.35em')
            .text(item.label)
            .style('font-size', '12px')
            .attr('fill', '#374151');
    });
    
    // 제목
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', -20)
        .attr('text-anchor', 'middle')
        .style('font-size', '16px')
        .style('font-weight', 'bold')
        .text('월별 인구 변화 추이');
    
    // Y축 레이블
    svg.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', -40)
        .attr('x', -height / 2)
        .attr('text-anchor', 'middle')
        .style('font-size', '12px')
        .text('인구 (명)');
}

// 전역 함수로 등록
window.loadAndRenderTimeseries = loadAndRenderTimeseries;

