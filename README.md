VIMVA: Innovative Multimodal Recognition in
Vietnamese Folk Dance Video Analysis

Attached Into The paper For The Camera Version

# Introduction:

# Requirement:
## Library
#### 1. To cut video and extract frame
```
     pip install moviepy
```
#### 2. To download, train and use YOLO model
```
     pip install ultralytics
```
#### 3. To download, use VnCoreNLP
```
    pip install py_vncorenlp
```
To use VnCoreNLP, your computer must have JVM (Java Virtual Machine) installed. You can check if it is installed with this command in your **Command Prompt**:
```
     java -version
```
If it is installed, the result should look like this:
![JVM](jvm.png)
Otherwise, you can download JVM at link: https://www.oracle.com/java/technologies/downloads/#java8
#### 4. To download, train and use PhoBERT model
```
     pip install transformers torch
```


# Train Model
### 1. YOLO Model:
First, you need to prepare a labeled image dataset. You can use [Roboflow](https://app.roboflow.com/) for this. Then, download the dataset that is suitable for **YOLO-v9**.

Second, you can use [Kaggle](https://www.kaggle.com/) or Colab of Google to train the YOLO-v9s model, as it requires a GPU to run and process. Below is the command for downloading and training:
```
!yolo task=detect mode=train model=yolov9s.pt epochs=30 batch=32 data=path/to/dataset.yaml imgsz=480
```
Replace 'path/to/dataset.yaml' with the path to your dataset's .yaml file.
# Result:
***Video 1:***
![Results1](./demo/demo1.jpg)

***Video 2:***
![Results2](./demo/demo2.jpg)

***Video 3:***
![Results3](./demo/demo3.1.jpg)





