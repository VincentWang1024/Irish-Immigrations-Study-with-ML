import React, { Component } from 'react';
import CanvasJSReact from '@canvasjs/react-charts';
import bar_data from '../fake_data';
//var CanvasJSReact = require('@canvasjs/react-charts');
 
var CanvasJS = CanvasJSReact.CanvasJS;
var CanvasJSChart = CanvasJSReact.CanvasJSChart;
export default class BarChart extends Component {
	constructor(props) {
		super(props);
		this.state = {
			title:'',
			dataPoints: '',
		};
	}
	onChange = (e) => this.setState({ [e.target.name]: e.target.value });

	render() {
		const options = {
			title: {
				text: this.state.title
			},
			data: [
			{
				// Change type to "doughnut", "line", "splineArea", etc.
				type: "column",
				// dataPoints: this.state.dataPoints
				dataPoints: bar_data
			}
			]
		}
		return (
		<div>
			<CanvasJSChart options = {options}
				/* onRef={ref => this.chart = ref} */
			/>
			{/*You can get reference to the chart instance as shown above using onRef. This allows you to access all chart properties and methods*/}
		</div>
		);
	}
}



