import { Helmet } from 'react-helmet-async';
import { filter } from 'lodash';
import { sentenceCase } from 'change-case';
import { useState, useEffect } from 'react';
import axios from 'axios';

// @mui
import {
    Container,
    Typography,
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
    
    
    const apikey = process.env.REACT_APP_YOUTUBE_API_KEY
    const extractVideoId = url => url.split('v=')[1]?.split('&')[0];
  
    const fetchYoutubeData = async () => {
      const videoId = extractVideoId(url);
      const response = await axios.get(
        `https://www.googleapis.com/youtube/v3/videos?id=${videoId}&key=${process.env.REACT_APP_YOUTUBE_API_KEY}&part=snippet`
      );
  
      setTitle(response.data.items[0].snippet.title);
      setThumbnail(response.data.items[0].snippet.thumbnails.high.url);
    };

    useEffect(() => {
        fetch('http://127.0.0.1:5000/api/model')
        // fetch('https://5d800273-5a71-4616-9066-1ce6d6c6280e.mock.pstmn.io/127.0.0.1/model')
            .then(response => response.json())
            .then(data => setMODELLIST(data))  // Set the state once data is fetched
            .catch(error => console.error('Error:', error));

            if (url !== prevUrl) { // check if current URL is different from previous URL
              setPrevUrl(url); // update previous URL state
              fetchYoutubeData(); // fetch video data
          }
      }, [url, prevUrl]); // updated dependency array

    const handleSubmit = (e) => {
      e.preventDefault();
      console.log(apikey)
      // setUrlChange(!urlChange);
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
          <TextField
            label="Enter a URL"
            value={url}
            style={{ width: '70%' }} // You might need to adjust this to ensure all elements fit
            onChange={(e) => setUrl(e.target.value)}
          />
            <FormControl style={{ width: '15%' }}>
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

          <Button type="submit" variant="c`ontained" color="primary">
            Submit
          </Button>
        </form>

        {submitted && (
        <>
          <Typography variant="h5" sx={{ mt: 3, mb: 2 }}>
            Video Title: {title}
          </Typography>
          <img src={thumbnail} alt={title} style={{ width: '300px' }} />
          <MyBarChart url={url} number={numComments} />
        </>
      )}      
      </Container>
    </>
  );
}
