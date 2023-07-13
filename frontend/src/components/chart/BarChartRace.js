import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';


export default function BarChartRace({ data }) {  // Accept data as a prop
    const ref = useRef();

    useEffect(() => {
        const svg = d3.select(ref.current)
            .attr('width', 500)
            .attr('height', 500);

        const x = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.value)])
            .range([0, 500]);

        const y = d3.scaleBand()
            .domain(d3.range(data.length))
            .range([0, 500])
            .padding(0.1);

        svg.selectAll('rect')
            .data(data)
            .join('rect')
            .attr('y', (d, i) => y(i))
            .attr('width', d => x(d.value))
            .attr('height', y.bandwidth())
            .attr('fill', 'steelblue');

        const shuffle = () => {
            data.forEach(d => d.value = Math.random() * 100);
            x.domain([0, d3.max(data, d => d.value)]);
            svg.selectAll('rect')
                .data(data.sort((a, b) => b.value - a.value))
                .sort((a, b) => b.value - a.value)
                .transition()
                .duration(2000)
                .attr('y', (d, i) => y(i))
                .attr('width', d => x(d.value));
        }

        const interval = setInterval(shuffle, 3000);

        // Clean up on unmount
        return () => clearInterval(interval);
    }, [data]);  // Add data as a dependency

    return (
        <svg ref={ref}></svg>
    );
}
