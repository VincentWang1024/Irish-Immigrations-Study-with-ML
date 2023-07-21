/* eslint-disable */

import { Helmet } from 'react-helmet-async';
import { filter } from 'lodash';
import { sentenceCase } from 'change-case';
import { useState, useEffect } from 'react';
import axios from 'axios';

// @mui
import {
    Container,
    Typography,
    Tooltip,
  Card,
  Table,
  Paper,
  Avatar,
  Button,
  Popover,
  Checkbox,
  TableRow,
  MenuItem,
  TableBody,
  TableCell,
  IconButton,
  TableContainer,
  TablePagination, TextField, FormControl, InputLabel, Select,
} from '@mui/material';

import MyBarChart from '../components/chart/BarChart';
import PieChart from '../components/chart/PieChart';
import {ProductCartWidget, ProductFilterSidebar, ProductList, ProductSort} from "../sections/@dashboard/products";
import PRODUCTS from "../_mock/products";

export default function CommentPage() {
    const [url, setUrl] = useState('');
    const [numComments, setNumComments] = useState('');
    const [modelID, setModelID] = useState('');
    const [submitted, setSubmitted] = useState(false);
    const [MODELLIST, setMODELLIST] = useState([]);
    const [title, setTitle] = useState('');
    const [thumbnail, setThumbnail] = useState('');
    const [prevUrl, setPrevUrl] = useState('');
    const [isHovered, setIsHovered] = useState(false);

    const [preprocessingList, setPreprocessingList] = useState([]);
    const [selectedPreprocessing, setSelectedPreprocessing] = useState(null);

    const fakedataPie = [
      { label: 'Apples', value: 10 }, 
      { label: 'Oranges', value: 20 },
      { label: 'Banana', value: 50 },
    ];

    const apikey = process.env.REACT_APP_YOUTUBE_API_KEY
    const extractVideoId = url => url.split('v=')[1]?.split('&')[0];
  
    const fetchYoutubeData = async () => {
      const videoId = extractVideoId(url);
      const apikey = process.env.REACT_APP_YOUTUBE_API_KEY;
      const response = await axios.get(
        `https://www.googleapis.com/youtube/v3/videos?id=${videoId}&key=${apikey}&part=snippet`
      );
  
      setTitle(response.data.items[0].snippet.title);
      setThumbnail(response.data.items[0].snippet.thumbnails.high.url);
    };

    useEffect(() => {
      console.log(process.env.REACT_APP_NLP_PLATFORM_API_URL);
      axios.get(`${process.env.REACT_APP_NLP_PLATFORM_API_URL}/api/model/find`)
       .then(response => {
           setMODELLIST(response.data);
       })  // Set the state once data is fetched
       .catch(error => console.error('Error:', error));

      axios.get(`${process.env.REACT_APP_NLP_PLATFORM_API_URL}/api/preprocessing/find`)
        .then(response => {
          setPreprocessingList(response.data);
        })
        .catch(error => console.error('Error:', error));
    }, []);  // Empty dependency array means this effect runs once on mount

    const handlePreprocessingChange = (e) => {
      const selectedOption = e.target.value;
      const matchingOption = preprocessingList.find(option => option.name === selectedOption);
      setSelectedPreprocessing(matchingOption);
    };

    const handleSubmit = (e) => {
      e.preventDefault();
      console.log(apikey)
      // setUrlChange(!urlChange);
      console.log('Selected preprocessing ID:', selectedPreprocessing.id)
      setSubmitted(true);
    };

  return (
         <>
      <Helmet>
        <title> Dashboard: Products | Minimal UI </title>
      </Helmet>

      <Container>
        <Typography variant="h4" sx={{ mb: 5 }}>
          Video Comments Analysis
        </Typography>

        <form
          onSubmit={handleSubmit}
          style={{
            display: 'flex',
            flexDirection: 'row', // Change from column to row
            alignItems: 'center',
            justifyContent: 'center',
            gap: '1rem',
            width: '100%' // You might need to adjust this to ensure all elements fit
          }}
        >
            <Tooltip title={
              <>
              <Typography variant="h5" sx={{ mt: 3, mb: 2 }}>
                  Video Title: {title}
                </Typography>
                <img src={thumbnail} alt={title} style={{ width: '200px' }} />
              </>
            } placement="right">
              <TextField
                label="Enter a URL"
                style={{ width: '50%' }}
                onChange={(e) => setUrl(e.target.value)}
              />
            </Tooltip>
            <FormControl style={{ width: '10%' }}>
            <InputLabel>#Comments</InputLabel>
            <Select
              value={numComments}
              onChange={(e) => setNumComments(e.target.value)}
            >
              <MenuItem value={50}>50</MenuItem>
              <MenuItem value={100}>100</MenuItem>
              <MenuItem value={200}>200</MenuItem>
            </Select>
          </FormControl>
            <FormControl style={{ width: '10%' }}>
                <InputLabel>Model</InputLabel>
                <Select
                    value={modelID}
                    onChange={(e) => setModelID(e.target.value)}
                >
                    {MODELLIST.map((model) => (
                        <MenuItem key={model.id} value={model.id}>
                            {model.name}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>
            <FormControl style={{width:'10%'}}>
            <InputLabel>Preprocessing</InputLabel>
                <Select
                    value={selectedPreprocessing ? selectedPreprocessing.name : ''}
                    onChange={handlePreprocessingChange}
                >
                    {preprocessingList.map((option) => (
                        <MenuItem key={option.id} value={option.name}>
                            {option.name}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>

          <Button type="submit" variant="c`ontained" color="primary">
            Submit
          </Button>
        </form>

        {submitted && (
        <>
          {/* <Typography variant="h5" sx={{ mt: 3, mb: 2 }}>
            Video Title: {title}
          </Typography>
          <img src={thumbnail} alt={title} style={{ width: '300px' }} /> */}
            <br/>
            <br/>
            <MyBarChart url={url} number={numComments} model_id={modelID} />
        </>
      )}      
      </Container>
    </>
  );
}
