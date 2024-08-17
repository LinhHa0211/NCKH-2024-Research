from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModel
from sentence import Sentence
from numpy import ascontiguousarray, load, concatenate, linalg, sum
from typing import List, Literal
from pandas import read_excel
from faiss import IndexFlatL2, IndexFlatIP
from torch import no_grad, argmax


class PhoBERTClassification:
    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)


    def predict_for_sentence(self, sentence: Sentence) -> int:

        # Đặt model ở chế độ đánh giá
        self.model.eval()

        # Vô hiệu hóa gradient
        with no_grad():
            # Mã hóa câu đầu vào và chuyển input sang GPU nếu có
            encoding = self.tokenizer(sentence.preprocessed_api_text, return_tensors='pt', truncation=True,
                                      padding=True, max_length=128)

            # Trích xuất input_ids và attention_mask từ encoding
            input_ids = encoding['input_ids']
            attention_mask = encoding['attention_mask']

            # Chạy dự đoán
            outputs = self.model(input_ids, attention_mask=attention_mask)

            # Lấy logits và tính toán dự đoán
            logits = outputs.logits
            prediction = argmax(logits, dim=-1)

            # Trả về kết quả dự đoán
            return prediction.item()
    
    
    def predict_for_sentences_list(self, sentences_list: List[Sentence]) -> List[int]:
        for i in range(len(sentences_list)):
            sentences_list[i].phobert_voted_label = [self.predict_for_sentence(sentences_list[i]),
                                                        sum([proportion for _, proportion in sentences_list[i].key_words])] 




class PhoBERTWithFAISS:
    def __init__(self, phobert_model_path: str, faiss_db_vectors_path: str, database_path: str, dis_type: Literal['L2', 'Cosine']='L2') -> None:
        """
            Initializes the PhoBERTWithFAISS class.
            :param phobert_model_path: Path to the PhoBERT model.
            :param faiss_db_vectors_path: Path to the FAISS database containing PhoBERT embeddings.
        """
        self.phobert_tokenizer = AutoTokenizer.from_pretrained(phobert_model_path)
        self.phobert_model = AutoModel.from_pretrained(phobert_model_path)
        
        self.database_texts, self.database_labels = self.__load_database(database_path)
        
        self.dis_type = dis_type
        self.faiss_db_vectors = self.__load_faiss_db_vectors(faiss_db_vectors_path)
        self.faiss_index = self.__create_faiss_index()

    
    def __load_database(self, database_path: str):
        df = read_excel(database_path)
        return df['Texts'].astype(str).tolist(), df['Mapped Labels'].astype(int).tolist()
    
    
    def __load_faiss_db_vectors(self, faiss_db_vectors_path: str):
        temp = []
        
        with open(faiss_db_vectors_path, 'rb') as f:
            while True:
                try:
                    temp.append(load(f, allow_pickle=True))
                except Exception as e:
                    break
                
        # Gộp các mảng lại thành một mảng duy nhất
        db_vectors = concatenate(temp, axis=0)
        return ascontiguousarray(db_vectors.astype('float32'))


    def __create_faiss_index(self):
        # Initialize FAISS index based on the type of distance
        if self.dis_type == 'L2':
            index = IndexFlatL2(self.faiss_db_vectors.shape[1])
        elif self.dis_type == 'Cosine':
            # Normalize db_vectors and input_vector to calculate cosine similarity by inner product
            self.faiss_db_vectors = self.faiss_db_vectors / linalg.norm(self.faiss_db_vectors, axis=1, keepdims=True)
            index = IndexFlatIP(self.faiss_db_vectors.shape[1])
        
        # Add vectors to the index
        index.add(self.faiss_db_vectors)
        
        return index
    
        
    def __encode_sentences(self, sentences_list: List[Sentence]) -> List:
        texts = [sentence.preprocessed_api_text for sentence in sentences_list]
        inputs = self.phobert_tokenizer(texts, return_tensors='pt', truncation=True, padding=True, max_length=128)
        outputs = self.phobert_model(**inputs)

        embeddings = outputs.last_hidden_state[:, 0, :].detach().numpy()
        return embeddings


    def find_k_nearest_texts_and_labels(self, input_sentence: Sentence, k: int=1):
        # Encode the input sentence
        input_vector = self.__encode_sentences([input_sentence]).astype('float32')

        if self.dis_type == 'Cosine':
            input_vector = input_vector / linalg.norm(input_vector, axis=1, keepdims=True)

        # Perform the search
        D, I = self.faiss_index.search(ascontiguousarray(input_vector), k)

        # Retrieve the nearest sentence from the database
        k_nearest_texts = [self.database_texts[idx] for idx in I[0]]
        k_nearest_labels = [self.database_labels[idx] for idx in I[0]]
        
        return k_nearest_texts, k_nearest_labels, D

    
    def predict_for_sentences_list(self, sentences_list: List[Sentence], k: int=1) -> None:
        for i in range(len(sentences_list)):
            sentences_list[i].faiss_pred_texts, sentences_list[i].faiss_pred_labels, _ = self.find_k_nearest_texts_and_labels(sentences_list[i], k=k)
            sentences_list[i].faiss_voted_label = [max(set(sentences_list[i].faiss_pred_labels), key=sentences_list[i].faiss_pred_labels.count),
                                                        sum([proportion for _, proportion in sentences_list[i].key_words])]
