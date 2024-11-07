// frontend/src/App.js
import React, { useState } from 'react';
const axios = require('axios/dist/browser/axios.cjs');

function App() {
  const [text, setText] = useState('');
  const [authorBackground, setAuthorBackground] = useState('');
  const [beliefs, setBeliefs] = useState([]);
  const [selectedBelief, setSelectedBelief] = useState('');
  const [action, setAction] = useState('change');
  const [parable, setParable] = useState('');

  const extractBeliefs = async () => {
    const response = await axios.post('http://localhost:8000/extract_beliefs/', {
      text,
      author_background: authorBackground,
    });
    setBeliefs(response.data.beliefs);
  };

  const generateParable = async () => {
    const response = await axios.post('http://localhost:8000/generate_parable/', {
      belief: selectedBelief,
      action,
      text,
      author_background: authorBackground,
    });
    setParable(response.data.parable);
  };

  return (
    <div>
      <h1>Belief Parable Generator</h1>
      <textarea placeholder="Enter text" value={text} onChange={(e) => setText(e.target.value)} />
      <input
        type="text"
        placeholder="Author background"
        value={authorBackground}
        onChange={(e) => setAuthorBackground(e.target.value)}
      />
      <button onClick={extractBeliefs}>Extract Beliefs</button>

      {beliefs.length > 0 && (
        <div>
          <h2>Select a Belief</h2>
          {beliefs.map((belief, index) => (
            <div key={index}>
              <input
                type="radio"
                name="belief"
                value={belief}
                onChange={(e) => setSelectedBelief(e.target.value)}
              />
              {belief}
            </div>
          ))}
          <select value={action} onChange={(e) => setAction(e.target.value)}>
            <option value="changed">Changed</option>
            <option value="reinforced">Reinforced</option>
            <option value="meaningless">Meaningless</option>
          </select>
          <button onClick={generateParable}>Generate Parable</button>
        </div>
      )}

      {parable && (
        <div>
          <h2>Generated Parable</h2>
          <p>{parable}</p>
        </div>
      )}
    </div>
  );
}

export default App;
