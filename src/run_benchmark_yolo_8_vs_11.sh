#!/bin/bash

VIDEO_SOURCE="./assets/videos/trieste_800x600.mp4"
VIDEO_LABEL=people
MODEL_IDS=("yolo8" "yolo11")

for CURRENT_ID in "${MODEL_IDS[@]}"
do
  BENCHMARK_RESULTS_FILE_NAME640=./benchmark_${VIDEO_LABEL}_640x640.xlsx

  #python3 ./main.py --benchmark --arg MODEL_ID=$CURRENT_ID --arg MODEL_USE_TENSORT=false  --arg BENCHMARK_RESULTS_FILE_NAME=$BENCHMARK_RESULTS_FILE_NAME640
  python3 ./main.py --benchmark --arg MODEL_ID=$CURRENT_ID --arg MODEL_PRECISION=float16  --arg BENCHMARK_RESULTS_FILE_NAME=$BENCHMARK_RESULTS_FILE_NAME640

done
