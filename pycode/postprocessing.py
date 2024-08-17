from typing import List
from sentence import Sentence


import os
import shutil
import random



class PostprocessingForSentences:
    
    def __init__(self) -> None:
        pass
    
    
    def convert_seconds(self, seconds):
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}:{remaining_seconds:02}"
    
    
    def summarize(self, list_of_sentences_lists: List[List[Sentence]], segment_duration: int, video_duration: int, n_sentences_per_class: int, n_sentences_padding: int, api_func) -> str:
        '''
        
            :local_val <res> = {
                    Label: [[Index_Segment, Index_Segment], [Text, Text]]
                    ...
                }        
        
        '''
        
        dance_name_map = {
            0: "vũ điệu dâng trời của dân tộc Cơ Tu",
            1: "điệu múa chuông của dân tộc Dao",
            2: "điệu múa khèn của dân tộc H'Mông",
            3: "điệu múa Rô băm Chun Por của người Khmer",
            4: "điệu múa nón lá của người Kinh",
            5: "điệu múa sen của người Kinh",
            6: "điệu múa xòe của người Thái",
            7: "điệu múa sạp, bắt nguồn từ dân tộc Thái và Mường"
        }
        
    
        res = {}
       
        for i in range(len(list_of_sentences_lists)):

            count_dic = {}
            for sentence in list_of_sentences_lists[i]:
                if sentence.phobert_voted_label[0] == sentence.faiss_voted_label[0]:
                    if sentence.faiss_voted_label[0] not in count_dic:
                        count_dic[sentence.faiss_voted_label[0]] = sentence.faiss_voted_label[1]
                    else:
                        count_dic[sentence.faiss_voted_label[0]] += sentence.faiss_voted_label[1]
            
            if len(count_dic) == 0:
                continue
            
            voted_label = max(count_dic, key=count_dic.get)
            list_texts = []
            for sentence in list_of_sentences_lists[i]:
                if sentence.phobert_voted_label[0] == sentence.faiss_voted_label[0] == voted_label:
                    for j in range(len(sentence.faiss_pred_labels)):
                        if sentence.faiss_pred_labels[j] == voted_label:
                            list_texts.append(sentence.faiss_pred_texts[j])
                        
            if voted_label not in res:
                res[voted_label] = [[i], [list_texts]]
            else:
                res[voted_label][0].append(i)
                res[voted_label][1].append(list_texts)
                
        
        
        if len(res) == 0:
            return "Xin lỗi! Có vẻ video của bạn không rõ ràng về điệu múa. Xin vui lòng upload video khác."
        
        
        sorted_res = dict(sorted(res.items(), key=lambda item: len(item[1][0]), reverse=True))
        
        i = 1
        response = f"<p>Tôi dự đoán được có <strong>{len(res)} điệu múa</strong> trong video bạn gửi lên:</p>"
        response += f"<ul>"
        end_segment_duration = video_duration - segment_duration * (len(list_of_sentences_lists) - 1)
        end_segment_index = len(list_of_sentences_lists) - 1
        for key, value in sorted_res.items():
            random_index_segment = random.choice(value[0])
            from_time = random_index_segment * segment_duration
            converted_from_time = self.convert_seconds(from_time)
            to_time = (random_index_segment + 1) * segment_duration 
            converted_to_time = self.convert_seconds(min(to_time, video_duration))
            
            random_texts = random.sample(value[1], min(len(value[1]), n_sentences_per_class))
            paragraph = api_func(random_texts, n_sentences_padding, dance_name_map[key])
            
            total_time = len(value[0]) * segment_duration
            
            if end_segment_index in value[0]:
                total_time = end_segment_duration + (len(value[0]) - 1) * segment_duration
                if total_time - (len(value[0]) * segment_duration) < 10:
                    total_time = len(value[0]) * segment_duration
            
            if len(sorted_res) == 1:
                response += f"<p><strong>Đây là {dance_name_map[key]}</strong>, sau đây là mô tả chi tiết về điệu múa này: {paragraph}<p>"
                break
            
            response += f"<li><p><strong>Điệu múa thứ {i} là {dance_name_map[key]}</strong>, có xuất hiện khoảng <strong>{total_time} giây</strong> trong video (bạn có thể xem từ phút <strong>{converted_from_time}</strong> đến phút <strong>{converted_to_time}</strong>). Sau đây là mô tả chi tiết về điệu múa này: {paragraph}</p></li>"
            i += 1
        
        response += f"</ul>"

        return response

    
    def clear_directory(self, path: str) -> None:
    
        for item in os.listdir(path):
            
            item_path = os.path.join(path, item)
            
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)  # Delete file or link
            
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Delete directory and its contents




