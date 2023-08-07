import { Helmet } from 'react-helmet-async';
import { Link as RouterLink } from 'react-router-dom';


// @mui
import { styled } from '@mui/material/styles';
import { Button, Typography, Container, Box } from '@mui/material';
import designImage from '../images/ux.png';
import preprocessingImage from '../images/data-processing.png';
import modelImage from '../images/social.png';
import visualization from '../images/growth.png'
import goEmotions from '../images/emotional.png'
import wordCloud from '../images/server.png'
import realtimebarchart from '../images/bar-graph.png'
import piechart from '../images/pie-chart.png'
import topicModelling from '../images/Topic-Modelling.png'


// ----------------------------------------------------------------------

const StyledContent = styled('div')(({ theme }) => ({
  maxWidth: 480,
  margin: 'auto',
  minHeight: '100vh',
  display: 'flex',
  justifyContent: 'center',
  flexDirection: 'column',
  padding: theme.spacing(12, 0),
}));




const aboutPageCSS = `
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 0;
}

header {
  background-color: #333;
  color: #fff;
  padding: 10px;
}

nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

nav ul li {
  display: inline-block;
  margin-right: 20px;
}

nav ul li a {
  color: #fff;
  text-decoration: none;
}

/* Add animation to h1 elements */
h1 {
  font-size: 36px;
  margin-bottom: 20px;
  animation: fadeInUp 1s ease-in-out, colorChange 2s infinite alternate; /* Apply multiple animations */
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes colorChange {
  from {
    color: #333;
  }
  to {
    color: #ff6600; /* Change text color to a different shade */
  }
}

/* Rest of your existing CSS */
/* ... */



.about {
  background-color: #f5f5f5;
  padding: 50px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.about-content {
  text-align: center;
}

.about-content h1 {
  font-size: 36px;
  margin-bottom: 20px;
}

.about-content p {
  font-size: 18px;
  line-height: 1.6;
  margin-bottom: 20px;
}


.about-content p {
  font-size: 18px;
  line-height: 1.6;
  margin-bottom: 20px;
}

/* CSS for the Features section */
.features-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 30px;
}

.feature-box {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 20px;
}

.features {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.features img {
  flex: 1; /* Expand the image to fill the available space */
  max-width: 30%; /* Ensure the image doesn't exceed its container */
  border-radius: 8px;
}

.features-content {
  flex: 2;
  padding: 0 20px;
}

.features h2 {
  font-size: 24px;
  margin-bottom: 10px;
}

.features p {
  font-size: 18px;
  line-height: 1.6;
}

/* Animation for the Features section on hover */
.features:hover {
  transform: translateY(-5px);
}



.feature-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-top: 30px;
}

.feature-container p {
  margin-bottom: 30px;
  line-height: 1.6;
  background-color: rgba(255, 255, 255, 0.8);
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  flex: 0 0 calc(33.33% - 20px);
  box-sizing: border-box;
  position: relative;
  transition: transform 0.3s ease; /* Adding transition */
}

.feature-container p:hover {
  transform: translateY(-5px); /* Move the box up slightly on hover */
}

.feature-container p img {
  width: 150px;
  height: auto;
  border-radius: 8px;
  display: block;
  margin: 20px auto;
}

/* Add spacing between the boxes */
.feature-container p:nth-child(3n + 1) {
  margin-right: 0;
}

/* Add spacing above and below the boxes */
.feature-container p:not(:nth-last-child(-n + 3)) {
  margin-bottom: 30px;
}


/* Category styles */
.category {
  flex: 0 0 calc(50% - 20px); /* Set width for two boxes in a row with spacing */
  padding: 20px; /* Add padding to the category boxes */
  box-sizing: border-box; /* Include padding and border in the box width calculation */
  text-align: center; /* Center the content inside the category */
}

.category h2 {
  font-size: 24px;
  margin-bottom: 10px;
  text-align: center; /* Center the "Hateful" heading */
}

.category p {
  font-size: 18px;
  line-height: 1.6;
  margin-bottom: 20px;
  background-color: rgba(255, 255, 255, 0.8); /* Transparent background with white color */
  padding: 15px; /* Increase padding to add more space inside the category boxes */
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Image container styles */
.image-container {
  display: flex;
  justify-content: space-around;
  margin-top: 30px;
}

.image-container img {
  width: 250px;
  height: 250px;
  border-radius: 8px;
}

`;


// ----------------------------------------------------------------------

export default function AboutPage() {
  return (
    <>

<div className="about">
      <div className="container">
        <div className="about-content">
          <h1>About Us</h1>
          <p>Our system is a real-time sentiment analysis platform focused on understanding Irish perceptions towards immigrants. You will have access to this platform, which serves as a reliable source for gathering data on relevant social issues.</p>
         
          
          <div className='feature-box'>
  <div className="features">
    <img src={realtimebarchart} alt="Real Time Analysis" />
    <div className="features-content">
      <h2>Real Time Analysis</h2>
      <p>
        The system allows you to add a YouTube link along with the number of comments you want to analyze.
        Real-time analytics is the use of data and related resources for analysis as soon as it enters the system
      </p>
    </div>
  </div>
  <div className="features">
    <div className="features-content">
      <h2>GOEmotions</h2>
      <p>
      Our system includes a BERT Transformer model trained on the GoEmotions dataset, which comprises 58k human-annotated reddit comments in English. The dataset covers a wide range of emotions, and we combining them into five broad categories, forming a superset that includes multiple other emotions.
       This valuable information is presented to users in an easily understandable format through a pie chart
      </p>
    </div>
    <img src={piechart} alt="GOEmotions" />
  </div>
  <div className="features">
    <img src={topicModelling} alt="Topic Modelling" />
    <div className="features-content">
      <h2>Topic Modelling</h2>
      <p>
      Topic Modelling gives the top words used in the comment data and categorises those words in the top five topics.
 Currently we use Bertopic which uses sentence transformers as embedding models and HDBSCAN for clustering words in topics.
 The dashboard uses wordcloud to represent the top words for the live requests sent via comment API.
      </p>
    </div>
  </div>
</div>









          
          <h1>Step-By-Step Guide</h1>
          <div className="feature-container">
            <p>
              The system allows you to add a YouTube link along with the number of comments you want to analyze.
              <img src={designImage} alt="Example_Image" />
            </p>
            <p>
              Before performing sentiment analysis, the system applies necessary preprocessing steps to clean and prepare the comments for analysis.
              <img src={preprocessingImage} alt="Example_Image" />
            </p>
            <p>
              Once the preprocessing is done, the system employs a trained sentiment analysis model to analyze the comments.
              <img src={modelImage} alt="Example_Image" />
            </p>
            <p>
              The results are presented in the form of a bar graph, making it easy for you to grasp the distribution of sentiments in the comments.
              <img src={visualization} alt="Example_Image" />
            </p>
            <p>
              Our system incorporates a powerful transformer model trained on the extensive Goemotions dataset. This dataset contains a corpus of 50k comments, each categorized into 27 distinct emotions.
              <img src={goEmotions} alt="Example_Image" />
            </p>
            <p>
              The system further facilitates topic modeling, allowing you to identify the main themes and subjects discussed in the comments.
              <img src={wordCloud} alt="Example_Image" />
            </p>
          </div>
          <h1>Annotation Guidelines</h1>
<div className="feature-container">
  <div className="category">
    <h2>Neutral</h2>
    <p>Comments that do not clearly indicate support for either the left wing or right wing are classified as neutral. 
    Regardless of the Comments expressing support or not supporting for the protestors, commenter's nationality other than Ireland will be treated as neutral.
     All bot comments will be categorized as neutral.
    </p>
  </div>
<div className="category">
    <h2>Non Hateful</h2>
    <p>
      Comments expressing support to immigration will be considered as non hateful.
      Comments expressing support to immigration, even with some hateful language, will be considered Non Hateful.
    </p>
  </div>

  <div className="category">
    <h2>Hateful</h2>
    <p>
      Comments expressing opposition to immigration, even without the use of hateful language, will be considered hateful.
      Comments expressing opposition to immigration, if they have hateful language, will be considered hateful.
      If the video is about protestors, any expression of support towards them will be regarded as hateful.
    </p>
  </div>
  <div className="category">
  <h2>General</h2>
  <p>
  Comments that are generic and which are not clearly stating any information related to the immigration can be annotated as hateful/not hateful/neutral by referring to the title.
  </p>
</div>
</div>
        </div>
      </div>
    </div>
    <div>
      {/* Use the imported image in the src attribute */}
      <style dangerouslySetInnerHTML={{ __html: aboutPageCSS }} />
    </div>
    </>
  );
}
