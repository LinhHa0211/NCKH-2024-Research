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
First, you need to prepare a labeled images dataset. You can use [Roboflow](https://app.roboflow.com/) for this. Then, download the dataset that is suitable for **YOLO-v9**.

Second, you can use [Kaggle](https://www.kaggle.com/) or Colab of Google to train the YOLO-v9s model, as it requires a GPU to run and process. Below is the command for downloading and training model:
```
!yolo task=detect mode=train model=yolov9s.pt epochs=30 batch=32 data=path/to/dataset.yaml imgsz=480
```
Replace ```path/to/dataset.yaml``` with the path to your dataset's .yaml file.
Next, you should download your model to your computer for later use.
### 2. PhoBERT Model:
First, you need to prepare a labeled texts dataset. It has two columns: ***texts*** and ***labels***. The ***texts*** column includes sentences that contain keywords related to their labels. Each row should contain only one sentence.
Second, you can use some preprocessing methods for NLP to preprocess your dataset (VnCoreNLP is one of these steps).
Third, you can download it with the commands below:
```
from transformers import AutoTokenizer, AutoModelForSequenceClassification
model_name = 'vinai/phobert-base-v2'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
```
Finally, the model is ready for training *(using a GPU is recommended)*. After that, you should save the model *(for later use)* with this command:
```
tokenizer.save_pretrained('your_model_path_dir')
model.save_pretrained('your_model_path_dir')
```
Replace ```your_model_path_dir``` with the path to save your model.
# Result:
***Video 1:***
![Results1](./demo/demo1.jpg)

***Video 2:***
![Results2](./demo/demo2.jpg)

***Video 3:***
![Results3](./demo/demo3.1.jpg)





