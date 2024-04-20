#!/bin/bash -ex

version=rotation_v2
python scripts/evaluate_mllm.py --model-base "liuhaotian/llava-v1.5-13b" \
	--model-path MoF_Models \
	--question-file /svl/u/sunfanyun/sceneVerse/preprocessed/ProcThor/all_data_$version.json

