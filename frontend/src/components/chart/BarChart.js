/* eslint-disable */

import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Spinner } from 'react-bootstrap';
import PieChart from './PieChart'
import { Chart } from "react-google-charts";
import axios from 'axios';
import CircularProgress from '@mui/material/CircularProgress';
import Box from '@mui/material/Box';


const MyBarChart = ({ url, number, model_id , preprocessIDs}) => {
  const [chartData, setChartData] = useState(null);
  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#FF8042', '#0088FE'];
  const fakeData = []
  const [pieData, setPieData] = useState(null);
  const options = {
    title: "GoEmotion",
  };
  useEffect(() => {
      const fetchChartData = async () => {
        try {
            const response = await axios.post(`${process.env.REACT_APP_NLP_PLATFORM_API_URL}/api/comments`, {
                url, 
                number, 
                model_id,
                preprocessIDs
            });
    
            const data = response.data;
    
            const transformedData = data.barchart_data.map(item => ({
                label: item.label,
                value: item.ratio,
            }));
    
            let result = data.piechart_data[0].goemotion_result.result;
    
            let transformedData2 = [["Task", "Hours per Day"]];
    
            for (let i = 0; i < result.length; i++) {
                let emotion = Object.keys(result[i])[0];
                let value = result[i][emotion];
                transformedData2.push([emotion, value]);
            }
    
            console.log(transformedData);
            console.log(transformedData2);
    
            setChartData(transformedData);
            setPieData(transformedData2);
    
        } catch (error) {
            console.error('Error:', error);
        } finally { /* empty */ }
    };

    fetchChartData();
  }, [url, number]);

  console.log(!chartData && !pieData);
  if(!chartData && !pieData) {
    return  <div style={{ display: 'flex'}}>
                <Box sx={{ display: 'flex' }}><CircularProgress /></Box>
                &nbsp;&nbsp;<h3>  Loading......Please wait a few minutes! </h3>
            </div>
  }

  return (
    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
      <br/>
      <BarChart
        width={700}
        height={500}
        data={chartData}
        margin={{
          top: 5, right: 30, left: 20, bottom: 5,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="label" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="value" fill="#8884d8" />
      </BarChart>
      
      <Chart
        chartType="PieChart"
        data={pieData}
        options={options}
        width={"120%"}
        height={"500px"}
    /> 
    </div>
  );
};

export default MyBarChart;
