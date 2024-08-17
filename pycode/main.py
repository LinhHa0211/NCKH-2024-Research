from object_detection import ObjectDetectionWithYOLO
from preprocessing import PreprocessingForSentences
from api_chatgpt import APIChatGPT
from phobert_and_faiss import PhoBERTClassification, PhoBERTWithFAISS
from postprocessing import PostprocessingForSentences
from typing import Literal, List
from io import BytesIO



import extract_frames as ef
import os



def predict(uploaded_video: BytesIO, temp_folder_path: str, min_duration: int, max_duration: int, 
            segment_duration: int, num_frames_per_seg: int, 
            yolo_model_path: str, 
            threshold_for_yolo_labels: float, threshold_for_choose_one_keyword: float, 
            n_sentences_for_prediction: List[int], vncorenlp_dir: str,
            OPENAI_API_KEY: str, gpt_model: str, 
            phobert_model_path: str, faiss_db_vectors_path: str, 
            database_path: str, faiss_dis_type: Literal['L2', 'Cosine']='L2', faiss_k: int=1,
            n_sentences_per_class: int=5,
            n_sentences_padding: int=3) -> str:
    
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    
    # Read video to file
    parent_folder_path = temp_folder_path
    video_path = os.path.join(ef.mkdir(parent_folder_path, tail='video'), uploaded_video.name)
    with open(video_path, "wb") as f:
        f.write(uploaded_video.getbuffer())


    video_duration = ef.VideoFileClip(video_path).duration
    
    if video_duration < min_duration:
        return f"Xin lỗi! Video của bạn quá ngắn, bạn cần đưa cho tôi video có độ dài từ {min_duration} giây đến {max_duration} giây."
    
    elif video_duration > max_duration:
        return f"Xin lỗi! Video của bạn quá dài, bạn cần đưa cho tôi video có độ dài từ {min_duration} giây đến {max_duration} giây."
    
    else:

        # Extract frames from each video segment:
        cut_videos_save_path = ef.mkdir(parent_folder_path, tail='cut_videos')
        cut_frames_save_path = ef.mkdir(parent_folder_path, tail='frames')
        ef.split_video(video_path, cut_videos_save_path, segment_duration)
        
        for cut_video_path in os.listdir(cut_videos_save_path):
            ef.extract_frames_from_video(
                video_path=os.path.join(cut_videos_save_path, cut_video_path), 
                cut_frames_save_path=cut_frames_save_path, 
                num_frames_per_seg=num_frames_per_seg, 
            )
        
        
        # Object Detection
        od = ObjectDetectionWithYOLO(yolo_model_path)
        
        objects_frequencies_list = []
        for cut_frames_fol_path in os.listdir(cut_frames_save_path):
            inputfol_path = os.path.join(cut_frames_save_path, cut_frames_fol_path)
            objects_frequencies_list.append(od.predict_for_frames_list(inputfol_path))
        
        # Check Object Fequencies List
        empty_check = all(len(objects_frequency) == 0 for objects_frequency in objects_frequencies_list)
        if empty_check == True:
            return "Xin lỗi! Video của bạn có vẻ có chất lượng khá thấp. Tôi không thể dự đoán được, bạn có thể cung cấp video khác không?"
        
        print(vncorenlp_dir)
        
        # Preprocess Sentences
        preprocessing = PreprocessingForSentences(vncorenlp_dir)
        
        top_labels_list = []
        for object_frequencies in objects_frequencies_list:
            top_labels_list.append(preprocessing.get_top_labels(object_frequencies, threshold=threshold_for_yolo_labels)) 
                                
        
        list_of_sentences_lists = []
        for top_labels in top_labels_list:
            list_of_sentences_lists.append(preprocessing.combine_words_for_sentences_list(
                                                            top_labels, 
                                                            threshold=threshold_for_choose_one_keyword,
                                                            n_sentences=n_sentences_for_prediction
                                                        ))
                                        
        
       

        # Call API From ChatGPT
        api_chatgpt = APIChatGPT(OPENAI_API_KEY, model_name=gpt_model)
        
        for i in range(len(list_of_sentences_lists)):
            api_chatgpt.generate_sentences(sentences_list=list_of_sentences_lists[i])
        

        # Preprocess API Texts
        for i in range(len(list_of_sentences_lists)):
            for j in range(len(list_of_sentences_lists[i])):
                list_of_sentences_lists[i][j].preprocessed_api_text = preprocessing.preprocess_text(list_of_sentences_lists[i][j].api_text)
        
        
        # Classify
        phobert_classification = PhoBERTClassification(phobert_model_path)
          
        phobert_with_faiss = PhoBERTWithFAISS(phobert_model_path, faiss_db_vectors_path, database_path, dis_type=faiss_dis_type)
        
        for i in range(len(list_of_sentences_lists)):
            phobert_classification.predict_for_sentences_list(list_of_sentences_lists[i])
            phobert_with_faiss.predict_for_sentences_list(list_of_sentences_lists[i], k=faiss_k)
            
    
        # Postprocess
        postprocessing = PostprocessingForSentences()
        
        response = postprocessing.summarize(list_of_sentences_lists, segment_duration, int(video_duration), 
                                            n_sentences_per_class, n_sentences_padding, 
                                            api_func=api_chatgpt.generate_paragraph)
        
        postprocessing.clear_directory(path=parent_folder_path) 
        
        # Return
        return response