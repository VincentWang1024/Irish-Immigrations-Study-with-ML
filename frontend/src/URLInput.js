import React, { useState } from 'react';
import { styled } from '@mui/system';
import { TextField, Button, CircularProgress, Alert, AlertTitle, Stack } from '@mui/material';
import { MenuItem, Select, FormControl, InputLabel } from '@mui/material';

import axios from 'axios';

const RootContainer = styled('div')({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  gap: '16px',
  padding: '300px',
  borderRadius: '8px',
  boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.1)',
  backgroundColor: '#f7f7f7',
  width: '800px',
});

const useStyles = () => ({
  textField: {
    width: '100%',
  },
  button: {
    fontWeight: 'bold',
    fontSize: '18px',
  },
  animationContainer: {
    width: '48px',
    height: '48px',
    borderRadius: '50%',
    border: '4px solid rgba(0, 0, 0, 0.1)',
    borderTopColor: '#3f51b5',
    animation: 'spin 1s linear infinite',
  },
  animation: {
    '@keyframes spin': {
      from: { transform: 'rotate(0deg)' },
      to: { transform: 'rotate(360deg)' },
    },
  },
  alertContainer: {
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
  },
  alert: {
    width: '500px',
  },
});

const URLInput = ({ onURLSubmit }) => {
  const classes = useStyles();
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [numComments, setNumComments] = useState('');
  const [isValid, setIsValid] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [successAlertOpen, setSuccessAlertOpen] = useState(false);
  const [errorAlertOpen, setErrorAlertOpen] = useState(false);

  const handleInputChange = (e) => {
    const inputValue = e.target.value;
    setUrl(inputValue);
    setIsValid(isValidUrl(inputValue));
    setError('');
  };

  const handleSubmit = () => {
    if (url.trim() === '') {
      setError('Please enter a URL');
    } else if (!isValid) {
      setError('Please enter a valid URL');
    } else if (numComments === '') {
      setError('Please enter a number of comments');
    } else {
      setIsLoading(true);
      // Simulate loading delay
      // setTimeout(() => {
      //   setIsLoading(false);
      //   setSuccessAlertOpen(true);
      //   onURLSubmit(url);
      // }, 2000);
      fetch('/api/comments', {
        method: 'POST',
        // mode: "cors", // no-cors, *cors, same-origin
        // credentials: 'include', // Include this line
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url, number: numComments }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error('Request failed');
          }
          return response.json();
        })
        .then((data) => {
          setIsLoading(false);
          setSuccessAlertOpen(true);
          onURLSubmit(url);
        })
        .catch((error) => {
          setIsLoading(false);
          setErrorAlertOpen(true);
          console.error('Error:', error.message);
        });

    }
  };

  const handleCloseAlerts = () => {
    setSuccessAlertOpen(false);
    setErrorAlertOpen(false);
  };

  const isValidUrl = (url) => {
    // Regex pattern for URL validation
    const urlRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+/;
    return urlRegex.test(url);
  };

  return (
    <RootContainer>
      <TextField
        label="Enter a URL"
        variant="outlined"
        size="large"
        fullWidth
        className={`${classes.textField} ${isValid ? classes.validUrl : ''}`}
        value={url}
        onChange={handleInputChange}
        error={!!error}
        helperText={error}
        inputProps={{ style: { textAlign: 'center' } }}
      />
      <FormControl fullWidth>
      <InputLabel id="num-comments-label">Number of Comments</InputLabel>
      <Select
        labelId="num-comments-label"
        value={numComments}
        onChange={(e) => setNumComments(e.target.value)}
        variant="outlined"
        label="Number of Comments"
        required
      >
        <MenuItem value={10}>50</MenuItem>
        <MenuItem value={20}>100</MenuItem>
        <MenuItem value={30}>200</MenuItem>
      </Select>
    </FormControl>
      <Button
        variant="contained"
        color="primary"
        size="large"
        className={classes.button}
        onClick={handleSubmit}
        disabled={isLoading||!isValid || numComments === ''}
      >
        {isLoading ? (
          <div className={classes.animationContainer}>
            <CircularProgress size={24} />
          </div>
        ) : (
          'Submit'
        )}
      </Button>
      <div className={classes.alertContainer}>
        <Stack spacing={6} className={classes.alert}>
          <Alert
            severity="success"
            onClose={handleCloseAlerts}
            sx={{ display: successAlertOpen ? 'block' : 'none' }}
          >
            <AlertTitle>Success</AlertTitle>
            URL Submitted Successfully!
          </Alert>
          <Alert
            severity="error"
            onClose={handleCloseAlerts}
            sx={{ display: errorAlertOpen ? 'block' : 'none' }}
          >
            <AlertTitle>Error</AlertTitle>
            Error Submitting URL!
          </Alert>
        </Stack>
      </div>
    </RootContainer>
  );
};

export default URLInput;