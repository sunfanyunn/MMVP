#!/bin/bash -ex
export HOME=/svl/u/sunfanyun

version=constraint_vlm_v0
#python scripts/evaluate_mllm.py --model-base "liuhaotian/llava-v1.5-13b" \
#	--model-path /svl/u/sunfanyun/GenLayout/third_party/MMVP/llava-v1.5-13b-mof \
#	--question-file /svl/u/sunfanyun/sceneVerse/preprocessed/ProcThor/all_data_$version.json

#python scripts/evaluate_mllm.py --model-base "liuhaotian/llava-v1.5-7b" \
#	--model-path /svl/u/sunfanyun/GenLayout/third_party/MMVP/LLaVA/checkpoints/llava-v1.5-7b-$version-pretrain \
#	--question-file /svl/u/sunfanyun/sceneVerse/preprocessed/ProcThor/all_data_$version.json

#run_id=finetune_task_lora
#python scripts/evaluate_mllm.py --model-base "liuhaotian/llava-v1.5-7b" \
#    --model-path /svl/u/sunfanyun/GenLayout/third_party/MMVP/LLaVA/checkpoints/llava-v1.5-7b-$version-$run_id \
#    --question-file /svl/u/sunfanyun/furniscene/preprocessed/all_data_$version.json

#run_id=finetune_lora
#python scripts/evaluate_mllm.py --model-base "liuhaotian/llava-v1.5-7b" \
#    --model-path /svl/u/sunfanyun/GenLayout/third_party/MMVP/LLaVA/checkpoints/llava-v1.5-7b-$version-$run_id \
#    --question-file /svl/u/sunfanyun/sceneVerse/preprocessed/ProcThor/all_data_$version.json
