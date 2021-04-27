import { FormControl, InputLabel, MenuItem, Select } from '@material-ui/core';
import React from 'react';


const SelectBox = ({ model, setModel }) => {
    const inputLabel = React.useRef(null);
    const [labelWidth, setLabelWidth] = React.useState(0);
    React.useEffect(() => {
        setLabelWidth(inputLabel.current.offsetWidth);
    }, []);

    return (
        <FormControl
            margin='normal'
            style={{ width: '200px' }}
            variant='outlined'>
            <InputLabel ref={inputLabel} htmlFor="model-select">Model</InputLabel>
            <Select
                value={model}
                labelWidth={labelWidth}
                onChange={e => setModel(e.target.value)}
                inputProps={{
                    name: 'model',
                    id: 'model-select',
                }}
            >
                <MenuItem value={'gpt2'}>GPT2 (not fine-tuned on NLP data)</MenuItem>
                {/* <MenuItem value={'gpt2-medium'}>Medium (345M)</MenuItem>
                <MenuItem value={'gpt2-large'}>Large (774M)</MenuItem> */}
                <MenuItem value={'lysandre/arxiv-nlp'}>Fine-tuned NLP</MenuItem>
                <MenuItem value={'gpt3'}>GPT 3</MenuItem>
            </Select>
        </FormControl>
    )
};

export default SelectBox;