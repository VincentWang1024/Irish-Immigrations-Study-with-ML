/* eslint-disable */

import React, { useEffect, useRef } from "react";
import * as d3 from "d3";
// import data from "./data";

function BarChartRace ({data}) {
  const ref = useRef();

  const duration = 750;
  const background = "#f4f4f4"; // Background color of the SVG

  const names = new Set(data.map((d) => d.name));
  const dates = Array.from(new Set(data.map((d) => d.date))).sort(d3.ascending);

  const n = Math.min(12, names.size);

  let x = d3.scaleLinear();

  // Define a new color scale
  let color = d3.scaleOrdinal().range(d3.schemeTableau10);

  const k = 10;

  const datevalues = Array.from(
    d3.rollup(
      data,
      ([d]) => d.value,
      (d) => +new Date(d.date),
      (d) => d.name
    )
  )
    .map(([date, data]) => [new Date(date), data])
    .sort(([a], [b]) => d3.ascending(a, b));

  const keyframes = (() => {
    const keyframes = [];
    let ka, a, kb, b;
    for ([[ka, a], [kb, b]] of d3.pairs(datevalues)) {
      for (let i = 0; i < k; ++i) {
        const t = i / k;
        keyframes.push([
          new Date(ka * (1 - t) + kb * t),
          rank((name) => (a.get(name) || 0) * (1 - t) + (b.get(name) || 0) * t)
        ]);
      }
    }
    keyframes.push([new Date(kb), rank((name) => b.get(name) || 0)]);
    return keyframes;
  })();

  function rank(value) {
    const data = Array.from(names, (name) => ({ name, value: value(name) }));
    data.sort((a, b) => d3.descending(a.value, b.value));
    for (let i = 0; i < data.length; ++i) data[i].rank = Math.min(n, i);
    return data;
  }

  useEffect(() => {
    if (ref.current) {
      const svg = d3.select(ref.current);
      const node = svg.node();
      if (node) {
        const width = node.getBoundingClientRect().width;

        x = d3
          .scaleLinear()
          .domain([0, d3.max(data, (d) => d.value)])
          .range([0, width]);

        let i = 0;
        d3.interval(() => {
          update(keyframes[i]);
          i = (i + 1) % keyframes.length;
        }, duration);
      }
    }
  }, []);

  const update = (keyframe) => {
    if (ref && ref.current) {
      const svg = d3.select(ref.current);
      const node = svg.node();
      if (node) {
        const width = node.getBoundingClientRect().width;
        const height = node.getBoundingClientRect().height;

        svg.style("background-color", background); // Apply background color

        const dateData = keyframe[1].sort((a, b) =>
          d3.descending(a.value, b.value)
        );

        const y = d3
          .scaleBand()
          .domain(dateData.map((d) => d.name))
          .range([0, height])
          .padding(0.1);

        const bars = svg.selectAll("rect").data(dateData, (d) => d.name);

        const barsEnter = bars
          .enter()
          .append("rect")
          .attr("x", 0)
          .attr("y", (d) => y(d.name))
          .attr("width", (d) => x(d.value))
          .attr("height", y.bandwidth())
          .attr("fill", (d) => color(d.rank / n));

        const barsUpdate = barsEnter.merge(bars);

        barsUpdate
          .transition()
          .duration(duration)
          .attr("y", (d) => y(d.name))
          .attr("width", (d) => x(d.value))
          .attr("fill", (d) => color(d.rank / n));

        bars.exit().remove();

        // Add labels
        const labels = svg.selectAll(".label").data(dateData, (d) => d.name);

        const labelsEnter = labels
          .enter()
          .append("text")
          .attr("class", "label")
          .attr("x", (d) => x(d.value) + 5) // Adjust this for label positioning
          .attr("y", (d) => y(d.name) + y.bandwidth() / 2)
          .attr("dy", ".35em") // Vertically center text
          .text((d) => d.name);

        const labelsUpdate = labelsEnter.merge(labels);

        labelsUpdate
          .transition()
          .duration(duration)
          .attr("x", (d) => x(d.value) + 5) // Adjust this for label positioning
          .attr("y", (d) => y(d.name) + y.bandwidth() / 2);

        labels.exit().remove();

        // Add values
        const values = svg.selectAll(".value").data(dateData, (d) => d.name);

        const valuesEnter = values
          .enter()
          .append("text")
          .attr("class", "value")
          .attr("x", (d) => x(d.value) - 5) // Adjust this for value positioning
          .attr("y", (d) => y(d.name) + y.bandwidth() / 2)
          .attr("dy", ".35em") // Vertically center text
          .attr("text-anchor", "end") // Align text to end (right)
          .text((d) => d3.format(",d")(d.value));

        const valuesUpdate = valuesEnter.merge(values);

        valuesUpdate
          .transition()
          .duration(duration)
          .attr("x", (d) => x(d.value) - 5) // Adjust this for value positioning
          .attr("y", (d) => y(d.name) + y.bandwidth() / 2)
          .tween("text", function (d) {
            let i = d3.interpolate(this.textContent.replace(/,/g, ""), d.value);
            return function (t) {
              this.textContent = d3.format(",d")(i(t));
            };
          });

        values.exit().remove();
      }
    }
  };

  return <svg ref={ref} />;
};

export default BarChartRace;
