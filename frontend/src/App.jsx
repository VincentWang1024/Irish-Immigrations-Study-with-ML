import React, { useState } from 'react';
import { styled } from '@mui/system';
import URLInput from './URLInput';
import NavBar from './components/Navbar';
import BarChart from './components/BarChart';


const OuterContainer = styled('div')({
    bool:'true',
    display: 'flex',
    flexDirection: 'column',
    marginLeft: '0',
    marginRight: '0', 
    marginTop: '0',
    marginBottom: '0',
    width: '100vw',
    height: '100vh',  
    minHeight: '100vh',
    backgroundColor: 'white'

});

// const AppContainer = styled('div')({
//   display: 'flex',
//   flexDirection: 'column',
//   alignItems: 'center',
//   justifyContent: 'center',
//   flex: '1 0 auto',
// });

const AppTitle = styled('h1')({
  fontSize: '28px',
  fontWeight: 'bold',
  marginBottom: '20px',
  color: '#333',
});

const App = () => {
  const handleURLSubmit = (url) => {
    // Simulate processing the URL
    console.log('Fetching URL:', url);
    // perform any other logic or API calls here
  };

  return (
    <OuterContainer sx={{ px: 0 }}>
      <NavBar />
       <AppTitle>URL Input</AppTitle>
       <URLInput onURLSubmit={handleURLSubmit} />
       <BarChart />
    </OuterContainer>
  );
};

export default App;