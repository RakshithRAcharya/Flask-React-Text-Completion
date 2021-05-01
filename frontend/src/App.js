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
  // const tmp = [{
  //   value: 0.0,
  //   label: "0.0",
  // },{
  //   value: 0.1,
  //   label: "0.10",
  // },{
  //   value: 0.2,
  //   label: "0.20",
  // },{
  //   value: 0.3,
  //   label: "0.30",
  // },{
  //   value: 0.4,
  //   label: "0.40",
  // },{
  //   value: 0.50,
  //   label: "0.50",
  // },{
  //   value: 0.60,
  //   label: "0.60",
  // },{
  //   value: 0.70,
  //   label: "0.70",
  // },{
  //   value: 0.80,
  //   label: "0.80",
  // },{
  //   value: 0.90,
  //   label: "0.90",
  // },{
  //   value: 1.00,
  //   label: "1",
  // },];
  // const [tempval, settempVal] = useState(0.3);
  // const updateTemp = (e, newtemp) => { 
  //   settempVal(newtemp);};
  const [lenval, setlenVal] = useState(20);
  const updateLen = (e, data) => {
    setlenVal(data);};
  const generateText = () => {
    postGenerateText({ text, lenval, model, userId: 1 });
  }

  return (
    <div className='app-container'>
      <form noValidate autoComplete='off'>
        <h1>Topics in Deep Learning Final Project - Team15</h1>
        <h2 class="subtitle">Context Sensitive Text Completion</h2>
        <SelectBox model={model} setModel={setModel} />
        <InputLabel htmlFor="token-select" >Length</InputLabel>
        <Slider value={lenval} onChange={updateLen} marks={gfg} valueLabelDisplay="auto"/>
        {/* <InputLabel htmlFor="temp-select">Temperature</InputLabel>
        <Slider value={tempval} min={0} max={1} onChange={updateTemp} marks={tmp} valueLabelDisplay="auto"/> */}
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
