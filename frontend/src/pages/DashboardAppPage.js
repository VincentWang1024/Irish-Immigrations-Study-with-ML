/* eslint-disable */

import React, { useEffect,useState} from 'react';
import { Helmet } from 'react-helmet-async';
import { faker } from '@faker-js/faker';
// @mui
import { useTheme } from '@mui/material/styles';
import { Grid, Container, Typography } from '@mui/material';
import YouTube from '@mui/icons-material/YouTube';
// components
import Iconify from '../components/iconify';
// sections
import {
  AppTasks,
  AppNewsUpdate,
  AppOrderTimeline,
  AppCurrentVisits,
  AppWebsiteVisits,
  AppTrafficBySite,
  AppWidgetSummary,
  AppCurrentSubject,
  AppConversionRates,
} from '../sections/@dashboard/app';

import WordCloud from '../components/chart/WordCloud';
import BarChartRace from '../components/chart/BarChartRace'
import StackBarchart from '../components/chart/StackBarchart';
import axios from 'axios';
import PropTypes from 'prop-types';

// ----------------------------------------------------------------------

export default function DashboardAppPage(props) {
  const theme = useTheme();

  const [data, setData] = useState(null);
  // const [pieData, setPieData] = useState([]);
  useEffect(() => {
      try {
          const url = `${process.env.REACT_APP_NLP_PLATFORM_API_URL}/api/dashboard`
          fetch(url)
          .then(response => response.json())
          .then(data => {
            setData(data)
            // handlePieData()
          })
          .catch(error => console.error(error));                              

          console.log('hook print: ', data);
  
      } catch (error) {
          console.error('Error:', error);
      } finally { /* empty */ }
  }, []);

  function handlePieData() {
    if (data && data.row2_2) {
      const emotions = data.row2_2[0]
      let newData = Object.keys(emotions).map(key => {
        return {
            label: key,
            value: emotions[key]
        };
      });
      return newData;
    }
  }

  function transformRaceData(data) {
    // Convert data into {date, name, value} format
    let formattedData = data.result.map(item => {
      let key = Object.keys(item)[0];
      return {
        date: data.median_time.split(' ')[0],  // get only the date part
        name: key,
        value: item[key]
      };
    });
  
    // Group data by date and name, and sum up the value for each group
    let groupedData = formattedData.reduce((acc, cur) => {
      // Generate a unique key representing the combination of date and name
      let key = `${cur.date}_${cur.name}`;
      // If this key doesn't exist in the accumulator, create a new object
      if (!acc[key]) {
        acc[key] = {...cur};
      } else {
        // Otherwise, accumulate the value
        acc[key].value += cur.value;
      }
      return acc;
    }, {});
  
    // Convert the grouped data (which is an object) back into array format
    return Object.values(groupedData);
  }
  

  let realBarRaceData = []
  function handleRaceData() {
    if (data && data.row3_1) {
      data.row3_1.map(item =>{
        realBarRaceData = [...realBarRaceData, ...transformRaceData(item.goemotion_result)];
      })
    }
  }
  handleRaceData();

  if (!data) return 'Loading......';  // Render some loading text or a spinner here

  const pieData = handlePieData()
  
  const stackBarData = data.row2_1.reduce((result, item) => {
    const existingProduct = result.find(product => product.name === item.name);
    if (existingProduct) {
      existingProduct.data.push(item.data);
    } else {
      result.push({
        name: item.name,
        data: [item.data]
      });
    }
    return result;
  }, []);

  // let categories = data.row2_1.filter(e => e.name==='Hateful').map(item => {
    let categories = data.row2_1.map(item => {
      const date = new Date(item.categories);
      return `${(date.getUTCMonth() + 1).toString().padStart(2, '0')}/${date.getUTCDate().toString().padStart(2, '0')}/${date.getUTCFullYear()} GMT`;
    });
    
    const groupedCategories = [];
    for (let i = 0; i < categories.length; i += 3) {
      groupedCategories.push(categories[i]);
    }
    categories = groupedCategories;
        
  console.log('after hook: ',data);
  // console.log(data.row1_1[0].numOfVideos);
  // console.log(data.row1_2[0].numOfcomments);
  // console.log(data.row1_34[1].numOfComments);
  // console.log(data.row1_34[2].numOfComments);
  console.log(realBarRaceData);
  // console.log(data.row3_2);
  // console.log(pieData)


  
  return (
    <>
      <Helmet>
        <title> Dashboard | Minimal UI </title>
      </Helmet>

      <Container maxWidth="xl">
        <Typography variant="h4" sx={{ mb: 5 }}>
          Hi, Welcome to NLP Platform
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <AppWidgetSummary title="Total Videos" total={data.row1_1[0].numOfVideos} color="warning"  icon={'mdi:youtube'} />
            {/* <AppWidgetSummary title="Total Videos" total={200000} icon={'ant-design:android-filled'} /> */}
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <AppWidgetSummary title="Total Comments" total={data.row1_2[0].numOfcomments} color="info" icon={'octicon:number-24'} />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <AppWidgetSummary title="#Non Hateful" total={data.row1_34[1].numOfComments} color="success" icon={'bxs:happy-alt'} />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <AppWidgetSummary title="#Hateful" total={data.row1_34[2].numOfComments} color="error" icon={'mingcute:angry-fill'} />
          </Grid>

          <Grid item xs={12} md={6} lg={8}>
            <StackBarchart inputseries={stackBarData} inputcategories={categories} />
          </Grid>

          <Grid item xs={12} md={6} lg={4}>
            <AppCurrentVisits
              title="Goemotion Piechart"
              chartData={pieData}
              chartColors={[
                theme.palette.primary.main,
                theme.palette.info.main,
                theme.palette.warning.main,
                theme.palette.error.main,
              ]}
            />
          </Grid>
          
          <Grid item xs={12} md={6} lg={8}>
            <BarChartRace title='Emotion Bar Race' data={realBarRaceData} />
          </Grid>

          <Grid item xs={12} md={6} lg={4}>
            <WordCloud title="Word Cloud" word_cloud_data={data.row3_2} />
            {/* <WordCloud title="Word Cloud" word_cloud_data={wordcloudfakedata} /> */}
          </Grid>
{/* 
          <Grid item xs={12} md={6} lg={8}>
            <AppNewsUpdate
              title="News Update"
              list={[...Array(5)].map((_, index) => ({
                id: faker.datatype.uuid(),
                title: faker.name.jobTitle(),
                description: faker.name.jobTitle(),
                image: `/assets/images/covers/cover_${index + 1}.jpg`,
                postedAt: faker.date.recent(),
              }))}
            />
          </Grid>

          <Grid item xs={12} md={6} lg={4}>
            <AppOrderTimeline
              title="Order Timeline"
              list={[...Array(5)].map((_, index) => ({
                id: faker.datatype.uuid(),
                title: [
                  '1983, orders, $4220',
                  '12 Invoices have been paid',
                  'Order #37745 from September',
                  'New order placed #XF-2356',
                  'New order placed #XF-2346',
                ][index],
                type: `order${index + 1}`,
                time: faker.date.past(),
              }))}
            />
          </Grid>

          <Grid item xs={12} md={6} lg={4}>
            <AppTrafficBySite
              title="Traffic by Site"
              list={[
                {
                  name: 'FaceBook',
                  value: 323234,
                  icon: <Iconify icon={'eva:facebook-fill'} color="#1877F2" width={32} />,
                },
                {
                  name: 'Google',
                  value: 341212,
                  icon: <Iconify icon={'eva:google-fill'} color="#DF3E30" width={32} />,
                },
                {
                  name: 'Linkedin',
                  value: 411213,
                  icon: <Iconify icon={'eva:linkedin-fill'} color="#006097" width={32} />,
                },
                {
                  name: 'Twitter',
                  value: 443232,
                  icon: <Iconify icon={'eva:twitter-fill'} color="#1C9CEA" width={32} />,
                },
              ]}
            />
          </Grid>

          <Grid item xs={12} md={6} lg={8}>
            <AppTasks
              title="Tasks"
              list={[
                { id: '1', label: 'Create FireStone Logo' },
                { id: '2', label: 'Add SCSS and JS files if required' },
                { id: '3', label: 'Stakeholder Meeting' },
                { id: '4', label: 'Scoping & Estimations' },
                { id: '5', label: 'Sprint Showcase' },
              ]}
            />
          </Grid> */}
        </Grid>
      </Container>
    </>
  );
}

