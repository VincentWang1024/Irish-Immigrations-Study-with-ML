/* eslint-disable */

import { Helmet } from 'react-helmet-async';
import { filter } from 'lodash';
import { sentenceCase } from 'change-case';
import { useState, useEffect } from 'react';
import axios from 'axios';
import OutlinedInput from '@mui/material/OutlinedInput';
import ListItemText from '@mui/material/ListItemText';

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
    const [selectedPreprocessName, setSelectedPreprocessName] = useState([]);
    const [selectedPreprocessIDS, setSelectedPreprocessIDS] = useState([]);
    const [preprocessNameList, setPreprocessNameList] = useState([]);

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
          const entries = response.data;
          console.log("entries: ", entries);
          setPreprocessNameList(entries);
        })
        .catch(error => console.error('Error:', error));

        fetchYoutubeData();
    }, []);  // Empty dependency array means this effect runs once on mount

    const ITEM_HEIGHT = 48;
    const ITEM_PADDING_TOP = 8;
    const MenuProps = {
      PaperProps: {
        style: {
          maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
          width: 250,
        },
      },
    };

    const preprocessNames = [
      // 'Oliver Hansen',
      // 'Van Henry',
      // 'April Tucker',
      // 'Ralph Hubbard',
      // 'Omar Alexander',
      // 'Carlos Abbott',
      // 'Miriam Wagner',
      // 'Bradley Wilkerson',
      // 'Virginia Andrews',
      // 'Kelly Snyder',
    ];
    
    const handlePreprocessChange = (event, obj) => {
      const {
        target: { key, value },
      } = event;
      setSelectedPreprocessName(
        // On autofill we get a stringified value.
        typeof value === 'string' ? value.split(',') : value,
      );
      console.log(obj.key);

      setSelectedPreprocessIDS([...selectedPreprocessIDS, parseInt(obj.key.slice(2))])
      console.log(selectedPreprocessName);
      console.log(selectedPreprocessIDS);
    };

    const handleSubmit = (e) => {
      e.preventDefault();
      console.log(apikey)
      // setUrlChange(!urlChange);
      // console.log('Selected preprocessing ID:', preprocessList.id)
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
            <FormControl sx={{ m: 1, width: 300 }}>
              <InputLabel id="demo-multiple-checkbox-label">preprocessing</InputLabel>
              <Select
                labelId="demo-multiple-checkbox-label"
                id="demo-multiple-checkbox"
                multiple
                value={selectedPreprocessName}
                onChange={handlePreprocessChange}
                input={<OutlinedInput label="Tag" />}
                renderValue={(selected) => selected.join(', ')}
                MenuProps={MenuProps}
              >
                {preprocessNameList.map((item) => (
                  <MenuItem key={item.pps_id} value={item.name}>
                    <Checkbox checked={selectedPreprocessName.indexOf(item.name) > -1} />
                    <ListItemText primary={item.name} />
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
            <MyBarChart url={url} number={numComments} model_id={modelID} preprocessIDs={selectedPreprocessIDS}/>
        </>
      )}      
      </Container>
    </>
  );
}
