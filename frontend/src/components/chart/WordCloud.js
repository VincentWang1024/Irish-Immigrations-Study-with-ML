/* eslint-disable */

import React, { useEffect,useState } from 'react';
import { TagCloud } from 'react-tagcloud';



function WordCloud({word_cloud_data}) {
  const [selectedTopic, setSelectedTopic] = useState([]);

  const handleTopicChange = (event) => {
    setSelectedTopic(parseInt(event.target.value));
  };

  const selectedWords = word_cloud_data.find((topic) => topic.id === selectedTopic)?.words || [];
  useEffect(() => {
    const fetchWordCloudData = async () => {
      try {
          const response = await axios.post(`${process.env.REACT_APP_NLP_PLATFORM_API_URL}/api/dashboard/wordcloud`, {});
  
          const data = response.data;
  
          const transformedData = data.barchart_data.map(item => ({
              label: item.label,
              value: item.ratio,
          }));
  
          let result = data.piechart_data[0].goemotion_result.result;
  
          let transformedData2 = [["Task", "Hours per Day"]];
  
          for (let i = 0; i < result.length; i++) {
              let emotion = Object.keys(result[i])[0];
              let value = result[i][emotion];
              transformedData2.push([emotion, value]);
          }
  
          console.log(transformedData);
          console.log(transformedData2);

          setSelectedTopic(word_cloud_data);
          
  
      } catch (error) {
          console.error('Error:', error);
      } finally { /* empty */ }
  };

  fetchWordCloudData();
}, []);
  return (  
    <>
    <div>
      <label htmlFor="topicDropdown">Select a topic: </label>
      <select id="topicDropdown" value={selectedTopic} onChange={handleTopicChange}>
        {word_cloud_data.map((topic) => (
          <option key={topic.id} value={topic.id}>
            {topic.name}
          </option>
        ))}
      </select>
    </div>
    <div className="word-cloud-container">
      <TagCloud minSize={12} maxSize={35} tags={selectedWords} className="tag-cloud" />
    </div>
  </>
    
  );
}

export default WordCloud;
