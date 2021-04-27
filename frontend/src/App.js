import React, { useState } from 'react';
import Button from './components/Button';
import SelectBox from './components/SelectBox';
import TextBox from './components/TextBox';
import { Slider, InputLabel } from "@material-ui/core";
import './styles.scss';
import { postGenerateTextEndpoint } from './utils';

function App() {
  const [text, setText] = useState("");
  const [model, setModel] = useState('lysandre/arxiv-nlp');
  const [generatedText, postGenerateText] = postGenerateTextEndpoint();
  const gfg = [
    {
      value: 0,
      label: "0",
    },
    {
      value: 10,
      label: "10",
    },
    {
      value: 20,
      label: "20",
    },
    {
      value: 30,
      label: "30",
    },
    {
      value: 40,
      label: "40",
    },
    {
      value: 50,
      label: "50",
    },
    {
      value: 60,
      label: "60",
    },
    {
      value: 70,
      label: "70",
    },
    {
      value: 80,
      label: "80",
    },
    {
      value: 90,
      label: "90",
    },
    {
      value: 100,
      label: "100",
    },
  ];
  const [val, setVal] = useState(20);
  const updateRange = (e, data) => {
    setVal(data);};
  const generateText = () => {
    postGenerateText({ text, val, model, userId: 1 });
  }

  return (
    <div className='app-container'>
      <form noValidate autoComplete='off'>
        <h1>Topics in Deep Learning Final Project - Team15</h1>
        <h2 class="subtitle">Context Sensitive Text Completion</h2>
        <SelectBox model={model} setModel={setModel} />
        <InputLabel htmlFor="token-select">Length</InputLabel>
        <Slider value={val} onChange={updateRange} marks={gfg}/>
        <TextBox text={text} setText={setText} />
        <Button onClick={generateText} />
      </form>

      {generatedText.pending &&
        <div className='result pending'>Please wait</div>}

      {generatedText.complete &&
        (generatedText.error ?
          <div className='result error'>Bad Request</div> :
          <div className='result valid'>
            {generatedText.data.result}
          </div>)}
    </div>
  );
}

export default App;
