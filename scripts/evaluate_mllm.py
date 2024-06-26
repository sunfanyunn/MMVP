import argparse
import numpy as np
import torch
import os
import json
from tqdm import tqdm
import shortuuid

from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN, DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN
from llava.conversation import conv_templates, SeparatorStyle
from llava.model.builder import load_pretrained_model
from llava.utils import disable_torch_init
from llava.mm_utils import tokenizer_image_token, get_model_name_from_path, KeywordsStoppingCriteria

from PIL import Image
import math


import pandas as pd
from PIL import Image
import os
import re

def find_number(text):
    pattern = r"\b-?\d+(\.\d+)?\b"
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    else:
        return "No number found in the text."


def split_list(lst, n):
    """Split a list into n (roughly) equal-sized chunks"""
    chunk_size = math.ceil(len(lst) / n)  # integer division
    return [lst[i:i+chunk_size] for i in range(0, len(lst), chunk_size)]


def get_chunk(lst, n, k):
    chunks = split_list(lst, n)
    return chunks[k]


def eval_model(args):
    # Model
    disable_torch_init()
    model_path = os.path.expanduser(args.model_path)
    model_name = get_model_name_from_path(model_path)

    #model_path = "MMVP/MoF_Models"
    #args.model_base = None
    #model_name = "liuhaotian/llava-v1.5-13b"
    tokenizer, model, image_processor, context_len = load_pretrained_model(model_path, args.model_base, model_name)
    
    if args.directory:
        benchmark_dir = os.path.join(args.directory, 'Questions.csv')
        # Load and read the CSV
        df = pd.read_csv(benchmark_dir)  # Assuming the fields are separated by tabs
        answers_file = os.path.expanduser(args.answers_file)
        # Check if the directory is specified in the path
        if os.path.dirname(answers_file):
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(answers_file), exist_ok=True)

        # Now open the file
        ans_file = open(answers_file, "w")

    # Loop through each row in the DataFrame
    #for index, row in tqdm(df.iterrows()):
    all_data = json.load(open(args.question_file, "r"))
    print('number of total entries in all_data', len(all_data))
    print('evaluating on 100 entries ...')

    correct_cnt = 0
    total_cnt = 0
    for cnt in range(1000):
        index = np.random.randint(0, len(all_data))
        

        # Construct the 'prompts' string
        # image_path = os.path.join(args.directory, 'MMVP Images', f"{photo_id}.jpg")
        #row = {
        #    'Question': "How many degrees did the object rotate for?",
        #    'Options':  "Choose your answer from the following options: 0, 90, 180, 270. Output a single number." ,
        #    'Answer': all_data[index]["conversations"][1]["value"]
        #}
        # cur_prompt = row['Question'] + " " + row['Options']
        # qs = cur_prompt

        ground_truth = all_data[index]["conversations"][1]["value"]
        qs = all_data[index]["conversations"][0]["value"][8:]

        if model.config.mm_use_im_start_end:
            assert False
            qs = DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_TOKEN + DEFAULT_IM_END_TOKEN + '\n' + qs
        else:
            qs = DEFAULT_IMAGE_TOKEN + '\n' + qs

        conv = conv_templates[args.conv_mode].copy()
        conv.append_message(conv.roles[0], qs)
        conv.append_message(conv.roles[1], None)
        prompt = conv.get_prompt()

        # Load the corresponding image
        photo_id = index+1
        image_path = all_data[index]["image"]
        image = Image.open(image_path)

        input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors='pt').unsqueeze(0).cuda()

        image_tensor = image_processor.preprocess(image, return_tensors='pt')['pixel_values'][0]

        stop_str = conv.sep if conv.sep_style != SeparatorStyle.TWO else conv.sep2
        keywords = [stop_str]
        stopping_criteria = KeywordsStoppingCriteria(keywords, tokenizer, input_ids)

        with torch.inference_mode():
            output_ids = model.generate(
                input_ids,
                images=image_tensor.unsqueeze(0).half().cuda(),
                do_sample=True,
                temperature=args.temperature,
                top_p=args.top_p,
                num_beams=args.num_beams,
                # no_repeat_ngram_size=3,
                max_new_tokens=1024,
                use_cache=True)

        input_token_len = input_ids.shape[1]
        n_diff_input_output = (input_ids != output_ids[:, :input_token_len]).sum().item()
        if n_diff_input_output > 0:
            print(f'[Warning] {n_diff_input_output} output_ids are not the same as the input_ids')
        outputs = tokenizer.batch_decode(output_ids[:, input_token_len:], skip_special_tokens=True)[0]
        outputs = outputs.strip()
        if outputs.endswith(stop_str):
            outputs = outputs[:-len(stop_str)]
        outputs = outputs.strip()

        ### 
        outputs = outputs.split("\n")[0]
        print(ground_truth, outputs)
        outputs = str(find_number(outputs))

        correct_cnt += (str(ground_truth) == str(outputs))
        total_cnt += 1
        print(f"total eval {cnt}, accuracy: {correct_cnt/total_cnt}")

        #ans_id = shortuuid.uuid()
        #ans_file.write(json.dumps({"question_id": photo_id,
        #                           "prompt": qs,
        #                           "answer": ground_truth,
        #                           "response": outputs,
        #                           "answer_id": ans_id,
        #                           "model_id": model_name,
        #                           }) + "\n")
        #ans_file.flush()
    #ans_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", type=str, default="facebook/opt-350m")
    parser.add_argument("--model-base", type=str, required=True)
    parser.add_argument("--directory", type=str, default=None)
    parser.add_argument("--question-file", type=str, default=None)
    parser.add_argument("--answers-file", type=str, default="answer.jsonl")
    parser.add_argument("--conv-mode", type=str, default="llava_v1")
    parser.add_argument("--num-chunks", type=int, default=1)
    parser.add_argument("--chunk-idx", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top_p", type=float, default=None)
    parser.add_argument("--num_beams", type=int, default=1)
    args = parser.parse_args()

    eval_model(args)
