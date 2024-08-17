from ultralytics import YOLO
from typing import Dict, Set

import os
import cv2


class ObjectDetectionWithYOLO:
    def __init__(self, yolo_model_path) -> None:
        """
            Initializes the ODWithYOLO class.
            :param yolo_model_path: Path to the YOLO model configuration or weights.
        """
        self.yolo_model = YOLO(yolo_model_path)

    
    def predict_frame(self, input_frame_path: str, verbose: bool=False) -> Set[str]:
        """
            Detects objects in a given frame using the YOLO model.
            :param <input_frame_path>: Path to the input frame
            :param <verbose>: Decides whether to print to stdout
            :return: Set of detected object labels in the frame
        """
        
        detected_objects = set()
        
        if input_frame_path.endswith('.jpg') or input_frame_path.endswith('.png'):
            # Read the image
            img = cv2.resize(cv2.imread(input_frame_path), (480, 480))
            # Detection
            results = self.yolo_model(img, verbose=verbose)[0]
            # Iterate over detections
            for r in results.boxes.data: # Access the bounding boxes from the Results object
                _, _, _, _, _, cls = r # Unpack 6 values: coordinates, confidence, and class
                label = self.yolo_model.names[int(cls)]
                detected_objects.add(label)
                
            cv2.destroyAllWindows()
             
        return detected_objects


    def predict_for_frames_list(self, inputfol_path: str, verbose: bool=False) -> Dict[str, int]:
        """
            Detects objects in all frames in a given folder using the YOLO model.
            :param <inputfol_path>: Path to the input folder containing frames
            :param <verbose>: Decides whether to print to stdout
            :return: Dictionary of detected object labels and their frequencies in the folder
        """
        
        dic = {}
        
        for iframe_path in os.listdir(inputfol_path):
            
            input_frame_path = os.path.join(inputfol_path, iframe_path)
            detected_objects = self.predict_frame(input_frame_path, verbose=verbose)
            
            if len(detected_objects) == 0:
                continue
            
            for obj in detected_objects:
                if obj in dic:
                    dic[obj] += 1
                else:
                    dic[obj] = 1
            
        return dict(sorted(dic.items(), key=lambda item: item[1], reverse=True)) if len(dic) > 0 else dic
            
    

        