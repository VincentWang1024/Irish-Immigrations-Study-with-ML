/* eslint-disable */

import React, { useEffect,useState } from 'react';
import { TagCloud } from 'react-tagcloud';



function WordCloud({word_cloud_data}) {
  // Set initial topic to the first item in the array
  const [selectedTopic, setSelectedTopic] = useState(word_cloud_data[0]?.id || []);
  // const [selectedTopic, setSelectedTopic] = useState([]);

  const [selectedWords, setSelectedWords] = useState([]);
  const handleTopicChange = (event) => {
    setSelectedTopic(parseInt(event.target.value));
  };

  useEffect(() => {
    setSelectedWords(word_cloud_data.find((topic) => topic.id === selectedTopic)?.words || []);
  });
  
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
      <TagCloud minSize={25} maxSize={70} tags={selectedWords} className="tag-cloud" />
    </div>
  </>
    
  );
}

export default WordCloud;
