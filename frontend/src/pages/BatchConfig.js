import { Helmet } from 'react-helmet-async';
import React, { useState } from "react";
import axios from "axios";
import TextField from "@mui/material/TextField";
import Autocomplete from "@mui/material/Autocomplete";
import Button from "@mui/material/Button";
import {
  Box,
  Container,
  CssBaseline,
  Typography,
  Grid,
  Chip
} from "@mui/material";
import {
  deepOrange,
  deepPurple,
  green,
  blue,
  red,
  yellow,
  teal
} from "@mui/material/colors";

export default function BatchConfig() {
  const [tag, setTag] = useState(""); // Single tag

  const colorMap = {
    irish: deepOrange[500],
    immigration: deepPurple[500],
    protest: green[500],
    rightwing: blue[500],
    leftwing: red[500],
    irelandisfull: yellow[600],
    ireland: teal[500]
  };

  const handleSubmit = async () => {
    try {
      console.log("Sending keyword:", tag); // Log the keyword being sent

      const apiUrl = `${process.env.REACT_APP_API_BASE_URL}/api/batch`;
      const response = await axios.post(apiUrl, { tags: [tag] }); // Send tag as an array

      console.log("Response from server:", response.data);
    } catch (error) {
      console.error("Error sending data:", error);
    }
  };

  return (
    <Container component="main" maxWidth="md">
      <CssBaseline />
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        marginTop={4}
      >
        <Typography component="h1" variant="h5" marginBottom={2}>
          Batch Configuration
        </Typography>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={9}>
            <Autocomplete
              id="tags-input"
              options={Object.keys(colorMap)}
              freeSolo
              value={tag}
              onChange={(event, newValue) => {
                setTag(newValue);
              }}
              renderTags={(value, getTagProps) =>
                value ? (
                  <Chip
                    variant="filled"
                    label={value}
                    {...getTagProps({ index: 0 })}
                    style={{ backgroundColor: colorMap[value] || blue[200] }}
                  />
                ) : null
              }
              renderInput={(params) => (
                <TextField
                  {...params}
                  fullWidth
                  variant="outlined"
                  label="Keyword"
                  placeholder="Add keyword"
                />
              )}
            />
          </Grid>
          <Grid item xs={3}>
            <Button
              variant="contained"
              color="primary"
              fullWidth
              onClick={handleSubmit}
            >
              Submit
            </Button>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
}
