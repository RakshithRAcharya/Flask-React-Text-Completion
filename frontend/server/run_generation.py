from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import logging
from tqdm import trange

import torch
import torch.nn.functional as F
import numpy as np

import os
import openai

from transformers import GPT2LMHeadModel, GPT2Tokenizer

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_LENGTH = int(100)  # Hardcoded max length to avoid infinite loop


MODEL_CLASSES = {
    'gpt2': (GPT2LMHeadModel, GPT2Tokenizer)
}

PADDING_TEXT = """ Natural Language Processing (NLP) models have achieved phenomenal success in linguistic and semantic tasks like text classification, machine translation, cognitive dialogue systems, information retrieval via Natural Language Understanding (NLU), and Natural Language Generation (NLG).. <eod> </s> <eos>"""

def top_k_top_p_filtering(logits, top_k=0, top_p=0.0, filter_value=-float('Inf')):

    assert logits.dim() == 1  # batch size 1 for now - could be updated for more but the code would be less clear
    top_k = min(top_k, logits.size(-1))  # Safety check
    if top_k > 0:
        # Remove all tokens with a probability less than the last token of the top-k
        indices_to_remove = logits < torch.topk(logits, top_k)[
            0][..., -1, None]
        logits[indices_to_remove] = filter_value

    if top_p > 0.0:
        sorted_logits, sorted_indices = torch.sort(logits, descending=True)
        cumulative_probs = torch.cumsum(
            F.softmax(sorted_logits, dim=-1), dim=-1)

        # Remove tokens with cumulative probability above the threshold
        sorted_indices_to_remove = cumulative_probs > top_p
        # Shift the indices to the right to keep also the first token above the threshold
        sorted_indices_to_remove[...,
                                 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = 0

        indices_to_remove = sorted_indices[sorted_indices_to_remove]
        logits[indices_to_remove] = filter_value
    return logits

def sample_sequence(model, length, context, num_samples=1, temperature=1, top_k=0, top_p=0.0, is_xlnet=False, device='cpu'):
    context = torch.tensor(context, dtype=torch.long, device=device)
    context = context.unsqueeze(0).repeat(num_samples, 1)
    generated = context
    with torch.no_grad():
        for _ in trange(length):

            inputs = {'input_ids': generated}
            if is_xlnet:
                input_ids = torch.cat((generated, torch.zeros(
                    (1, 1), dtype=torch.long, device=device)), dim=1)
                perm_mask = torch.zeros(
                    (1, input_ids.shape[1], input_ids.shape[1]), dtype=torch.float, device=device)
                # Previous tokens don't see last token
                perm_mask[:, :, -1] = 1.0
                target_mapping = torch.zeros(
                    (1, 1, input_ids.shape[1]), dtype=torch.float, device=device)
                target_mapping[0, 0, -1] = 1.0  # predict last token
                inputs = {'input_ids': input_ids, 'perm_mask': perm_mask,
                          'target_mapping': target_mapping}
            outputs = model(**inputs)
            next_token_logits = outputs[0][0, -1, :] / temperature
            filtered_logits = top_k_top_p_filtering(
                next_token_logits, top_k=top_k, top_p=top_p)
            next_token = torch.multinomial(
                F.softmax(filtered_logits, dim=-1), num_samples=1)
            generated = torch.cat((generated, next_token.unsqueeze(0)), dim=1)
    return generated

openai.api_key = os.getenv("OPENAI_API_KEY")
def gpt3_gen(prompt, max_tokens=30, temperature=0.3, top_p=0.97):
    response = openai.Completion.create(
      engine="davinci",
      prompt=f"I will be able to generate and complete sentences in the domain of Natural Language Processing or Computation and Linguistics, using different Arxiv papers. \n\nPrompt: Word Embeddings are\nAnswer: a class of techniques where individual words are represented as real-valued vectors in a predefined vector space. \n\nPrompt: Natural Language Processing is a domain where\nAnswer: artificial intelligence, and linguistics concerned with enabling computers to engage in communication using natural language(s) in all forms, including but not limited to speech, print, writing, and signing.\n\nPrompt: This model enables you to\nAnswer: learn word embeddings from a corpus of text.\n\nPrompt: The word embedding model is\nAnswer: a neural network that maps words to vectors of real numbers.\n\nPrompt: The word2vec model is\nAnswer: a neural network that maps words to vectors of real numbers.\n\nPrompt:{prompt}",
      temperature=temperature,
      max_tokens=max_tokens,
      top_p=top_p,
      frequency_penalty=0.13,
      presence_penalty=0,
    stop=["Prompt:"]
    )
    return response["choices"][0]["text"][9:]

def generate_text(padding_text=None,
    model_type='gpt2',
    length=20,
    prompt='',
    model_name_or_path='gpt2',
    temperature=0.3,
    top_k=0,
    top_p=0.9,
    no_cuda=True,
    seed=42,):

    
    device = torch.device(
        "cuda" if torch.cuda.is_available() and not no_cuda else "cpu")
    n_gpu = torch.cuda.device_count()

    np.random.seed(seed)
    torch.manual_seed(seed)
    if n_gpu > 0:
        torch.cuda.manual_seed_all(seed)

    model_type = model_type.lower()
    model_class, tokenizer_class = MODEL_CLASSES[model_type]
    tokenizer = tokenizer_class.from_pretrained(model_name_or_path)
    model = model_class.from_pretrained(model_name_or_path)
    model.to(device)
    model.eval()

    if length < 0 and model.config.max_position_embeddings > 0:
        length = model.config.max_position_embeddings
    elif 0 < model.config.max_position_embeddings < length:
        # No generation bigger than model size
        length = model.config.max_position_embeddings
    elif length < 0:
        length = MAX_LENGTH  # avoid infinite loop

    while True:
        raw_text = prompt if prompt else input("Model prompt >>> ")
        context_tokens = tokenizer.encode(raw_text)
        out = sample_sequence(
            model=model,
            context=context_tokens,
            length=length,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            device=device,
            is_xlnet=bool(model_type == "xlnet"),
        )
        out = out[0, len(context_tokens):].tolist()
        text = tokenizer.decode(out, clean_up_tokenization_spaces=True)
        print(text)
        if prompt:
            break
    return text
