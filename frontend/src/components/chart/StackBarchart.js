import React, { useState, useEffect } from 'react';
import ReactApexChart from 'react-apexcharts';
import { Card, CardHeader } from '@mui/material';
import { useTheme, styled } from '@mui/material/styles';
import Tooltip from '@mui/material/Tooltip';
import IconButton from '@mui/material/IconButton';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import Zoom from '@mui/material/Zoom';

const CHART_HEIGHT = 372;
const LEGEND_HEIGHT = 120;

const StyledChartWrapper = styled('div')(({ theme }) => ({
  height: CHART_HEIGHT,
  marginTop: theme.spacing(5),
  '& .apexcharts-canvas svg': { height: CHART_HEIGHT },
  '& .apexcharts-canvas svg,.apexcharts-canvas foreignObject': {
    overflow: 'visible',
  },
  '& .apexcharts-legend': {
    height: LEGEND_HEIGHT,
    alignContent: 'center',
    position: 'relative !important',
    borderTop: `solid 1px ${theme.palette.divider}`,
    top: `calc(${CHART_HEIGHT - LEGEND_HEIGHT}px) !important`,
  },
}));

// ----------------------------------------------------------------------

const ApexChart = ({inputseries, inputcategories}) => {
  console.log(inputseries);
  console.log(inputcategories);

  const [series, setSeries] = useState([]);

  const [options] = useState({
    chart: {
      type: 'bar',
      height: 350,
      stacked: true,
      toolbar: {
        show: true,
      },
      zoom: {
        enabled: true,
      },
    },
    responsive: [
      {
        breakpoint: 480,
        options: {
          legend: {
            position: 'bottom',
            offsetX: -10,
            offsetY: 0,
          },
        },
      },
    ],
    plotOptions: {
      bar: {
        horizontal: false,
        borderRadius: 10,
        dataLabels: {
          total: {
            enabled: true,
            style: {
              fontSize: '13px',
              fontWeight: 900,
            },
          },
        },
      },
    },
    xaxis: {
      type: 'datetime',
      categories: inputcategories
      // categories: ['01/01/2011 GMT', '01/02/2011 GMT', '01/03/2011 GMT', '01/04/2011 GMT',
      // '01/05/2011 GMT', '01/06/2011 GMT'],
    },
    legend: {
      position: 'right',
      offsetY: 40,
    },
    fill: {
      opacity: 1,
    },
  });

  useEffect(() =>{
      console.log(inputseries);
      setSeries(inputseries);
    }
  )

  return (
    <Card>
      <Tooltip 
        title="Information about the word cloud" 
        placement="top-end" 
        TransitionComponent={Zoom}
        sx={{ position: 'absolute', bottom : 0, right : 0 }}
      >
        <IconButton color="primary">
          <HelpOutlineIcon />
        </IconButton>
      </Tooltip>
      <CardHeader title=''/>
          <ReactApexChart options={options} 
          series={series} 
          type="area" height={450} />
    </Card>
  );
};

export default ApexChart;
