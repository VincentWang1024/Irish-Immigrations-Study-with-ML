/* eslint-disable */

import React, { useEffect,useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { faker } from '@faker-js/faker';
// @mui
import { useTheme } from '@mui/material/styles';
import { Grid, Container, Typography } from '@mui/material';
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
import axios from 'axios';

// ----------------------------------------------------------------------

export default function DashboardAppPage() {
  const theme = useTheme();
  const wordcloudfakedata = [
    { id: 1, name: 'Topic 1', words: [
      { value: 'Lorem', count: 200 }, 
      { value: 'Ipsum', count: 100 },
      { value: 'aaaa', count: 120 },
      { value: 'bbbbb', count: 50 },
      { value: 'cccc', count: 60 },
      { value: 'dddd', count: 160 },
      { value: 'eeeee', count: 90 },
      { value: 'ffff', count: 110 },
  ] },
    { id: 2, name: 'Topic 2', words: [{ value: 'Dolor', count: 15 }, { value: 'Sit', count: 8 }] },
    { id: 3, name: 'Topic 3', words: [{ value: 'Lorem', count: 20 }, { value: 'Ipsum', count: 10 }] },
    { id: 4, name: 'Topic 4', words: [{ value: 'Dolor', count: 15 }, { value: 'Sit', count: 8 }] },
    { id: 5, name: 'Topic 5', words: [{ value: 'Lorem', count: 20 }, { value: 'Ipsum', count: 10 }] },
    { id: 6, name: 'Topic 6', words: [{ value: 'Dolor', count: 15 }, { value: 'Sit', count: 8 }] },
    { id: 7, name: 'Topic 7', words: [{ value: 'Lorem', count: 20 }, { value: 'Ipsum', count: 10 }] },
    { id: 8, name: 'Topic 8', words: [{ value: 'Dolor', count: 15 }, { value: 'Sit', count: 8 }] },
    // Add more topics with their associated words
  ];
  const barRaceData = [
    {
      date: "2000-01-01",
      name: "Joy",
      value: 72537
    },
    {
      date: "2000-01-01",
      name: "Sadness",
      value: 56042
    },
    {
      date: "2000-01-01",
      name: "Surprise",
      value: 48000
    },
    {
      date: "2000-01-01",
      name: "Anger",
      value: 60000
    },
    {
      date: "2002-03-01",
      name: "Joy",
      value: 90003
    },
    {
      date: "2002-03-01",
      name: "Sadness",
      value: 65000
    },
    {
      date: "2002-03-01",
      name: "Surprise",
      value: 70000
    },
    {
      date: "2002-03-01",
      name: "Anger",
      value: 80000
    },
    {
      date: "2004-01-01",
      name: "Joy",
      value: 120000
    },
    {
      date: "2004-01-01",
      name: "Sadness",
      value: 75000
    },
    {
      date: "2004-01-01",
      name: "Surprise",
      value: 85000
    },
    {
      date: "2004-01-01",
      name: "Anger",
      value: 90000
    },
    {
      date: "2005-01-01",
      name: "Joy",
      value: 130000
    },
    {
      date: "2005-01-01",
      name: "Sadness",
      value: 80000
    },
    {
      date: "2005-01-01",
      name: "Surprise",
      value: 95000
    },
    {
      date: "2005-01-01",
      name: "Anger",
      value: 100000
    },
    {
      date: "2006-01-01",
      name: "Joy",
      value: 140000
    },
    {
      date: "2006-01-01",
      name: "Sadness",
      value: 85000
    },
    {
      date: "2006-01-01",
      name: "Surprise",
      value: 100000
    },
    {
      date: "2006-01-01",
      name: "Anger",
      value: 110000
    },
    {
      date: "2006-01-01",
      name: "Something",
      value: 110000
    }
  ];

  const [data, setData] = useState(null);
  const [pieData, setPieData] = useState([]);
  useEffect(() => {
      try {
          const url = `${process.env.REACT_APP_NLP_PLATFORM_API_URL}/api/dashboard`
          fetch(url)
          .then(response => response.json())
          .then(data => setData(data))
          .catch(error => console.error(error));                              
          setData(data);

          console.log('hook print: ', data);

          const pData = data.row2_2.map(item => ({
            label: item.label,
            value: item.ratio,
          }));
          setPieData(pData)
          // let result = data.piechart_data[0].goemotion_result.result;
  
          // let transformedData2 = [["Task", "Hours per Day"]];
  
          // for (let i = 0; i < result.length; i++) {
          //     let emotion = Object.keys(result[i])[0];
          //     let value = result[i][emotion];
          //     transformedData2.push([emotion, value]);
          // }
  
          // console.log(transformedData);
          // console.log(transformedData2);

          // setSelectedTopic(word_cloud_data);
          
  
      } catch (error) {
          console.error('Error:', error);
      } finally { /* empty */ }
  }, []);

  if (!data) return 'Loading......';  // Render some loading text or a spinner here




  console.log('after hook: ',data);
  console.log(data.row1_1[0].numOfVideos);
  console.log(data.row1_2[0].numOfcomments);
  console.log(data.row1_34[1].numOfComments);
  console.log(data.row1_34[2].numOfComments);
  console.log(data.row3_2);

  return (
    <>
      <Helmet>
        <title> Dashboard | Minimal UI </title>
      </Helmet>

      <Container maxWidth="xl">
        <Typography variant="h4" sx={{ mb: 5 }}>
          Hi, Welcome back
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <AppWidgetSummary title="Total Videos" total={data.row1_1[0].numOfVideos} icon={'ant-design:android-filled'} />
            {/* <AppWidgetSummary title="Total Videos" total={200000} icon={'ant-design:android-filled'} /> */}
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <AppWidgetSummary title="Total Comments" total={data.row1_2[0].numOfcomments} color="info" icon={'ant-design:apple-filled'} />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <AppWidgetSummary title="#Non Hateful" total={data.row1_34[1].numOfComments} color="warning" icon={'ant-design:windows-filled'} />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <AppWidgetSummary title="#Hateful" total={data.row1_34[2].numOfComments} color="error" icon={'ant-design:bug-filled'} />
          </Grid>

          <Grid item xs={12} md={6} lg={8}>
            <AppWebsiteVisits
              title="Emotion Barchart"
              subheader="(+43%) than last year"
              chartLabels={[
                '01/01/2003',
                '02/01/2003',
                '03/01/2003',
                '04/01/2003',
                '05/01/2003',
                '06/01/2003',
                '07/01/2003',
                '08/01/2003',
                '09/01/2003',
                '10/01/2003',
                '11/01/2003',
              ]}
              chartData={[
                {
                  name: 'Team A',
                  type: 'column',
                  fill: 'solid',
                  data: [23, 11, 22, 27, 13, 22, 37, 21, 44, 22, 30],
                },
                {
                  name: 'Team B',
                  type: 'area',
                  fill: 'gradient',
                  data: [44, 55, 41, 67, 22, 43, 21, 41, 56, 27, 43],
                },
                {
                  name: 'Team C',
                  type: 'line',
                  fill: 'solid',
                  data: [30, 25, 36, 30, 45, 35, 64, 52, 59, 36, 39],
                },
              ]}
            />
          </Grid>

          <Grid item xs={12} md={6} lg={4}>
            <AppCurrentVisits
              title="Goemotion piechart"
              
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
            <BarChartRace data={barRaceData} />
            {/* <AppConversionRates
              title="Emotion Racing"
              subheader="(+43%) than last year"
              chartData={[
                { label: 'Italy', value: 400 },
                { label: 'Japan', value: 430 },
                { label: 'China', value: 448 },
                { label: 'Canada', value: 470 },
                { label: 'France', value: 540 },
                { label: 'Germany', value: 580 },
                { label: 'South Korea', value: 690 },
                { label: 'Netherlands', value: 1100 },
                { label: 'United States', value: 1200 },
                { label: 'United Kingdom', value: 1380 },
              ]}
            /> */}
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

