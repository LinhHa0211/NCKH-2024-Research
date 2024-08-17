from typing import List

class Sentence:
    def __init__(self, key_words: List[List[str | int]], padding_words: List[str]) -> None:
        self.key_words = key_words
        self.padding_words = padding_words
        
        self.api_text = None
        self.preprocessed_api_text = None
        
        self.phobert_voted_label = None # [0, 1.5]
        
        self.faiss_pred_texts = []
        self.faiss_pred_labels = []
        self.faiss_voted_label = None # [0, 1.5]
 
    
    def get_key_words_for_create_text(self) -> List[str]:
        return [word for word, _ in self.key_words]
    
    def get_padding_words_for_create_text(self) -> List[str]:
        return self.padding_words
    
    
       
    