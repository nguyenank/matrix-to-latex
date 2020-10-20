from model.yolo.detect import detect
import argparse
import os

os.system("python model/yolov5/detect.py --weights webapp/last.pt --source webapp/inference/images --out webapp/inference/output --img 416 --conf 0.4 --save-txt")
#python detect.py --weights last.pt --img 416 --conf 0.4 --save-txt
