import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Spinner } from 'react-bootstrap';


const MyBarChart = ({ url, number, model_id }) => {
  const [chartData, setChartData] = useState([]);
  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#FF8042', '#0088FE'];
  const fakeData = []
  useEffect(() => {
    const fetchChartData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/comments', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ url, number, model_id }),
        });

        const data = await response.json();

        const transformedData = data.map(item => ({
          label: item.label,
          value: item.ratio,
        }));

        console.log(transformedData);

        setChartData(transformedData);

      } catch (error) {
        console.error('Error:', error);
      } finally { /* empty */ }
    };

    fetchChartData();
  }, [url, number]);


  return (
    <div>
      <br/>
      {!chartData ? (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Spinner animation="border" />
        </div>
      ) : (
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
      )}
    </div>
  );
};

export default MyBarChart;
