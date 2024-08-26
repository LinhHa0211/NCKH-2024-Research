from typing import List, Dict
from category import Category
from sentence import Sentence
from py_vncorenlp import VnCoreNLP

import random
import unicodedata



class PreprocessingForSentences:
    
    # The dictionary is used to store keywords with the key as the class
    __dictionary = {
        'CoTu-Chieng': ['cồng chiêng', 'tiếng chiêng', 'cái chiêng'],
        'CoTu-Trang_phuc_nam': ['trang phục thổ cẩm Cơ Tu nam', 'trang phục truyền thống của người Cơ Tu nam'],
        'CoTu-Trang_phuc_nu': ['trang phục thổ cẩm Cơ Tu nữ', 'trang phục truyền thống của người Cơ Tu nữ'],
        'CoTu-Trong': ['tiếng trống của người Cơ Tu', 'cái trống của người Cơ Tu'],
        'Dao-Chuong': ['cái chuông của người Dao', 'nhạc cụ chuông của người Dao'],
        'Dao-Mu': ['mũ đội đầu của người Dao Đỏ',],
        'Dao-Trang_phuc': ['trang phục của người Dao Đỏ', 'trang phục truyền thống của người Dao Đỏ'],
        'Dao_quan_chet-Mu': ['mũ đội đầu của người Dao Quần Chẹt'],
        'Dao_quan_chet-Trang_phuc': ['trang phục truyền thống của người Dao Quần Chẹt', 'trang phục của người Dao Quần Chẹt'],
        'Hmong-Khen': ['cái khèn của người H\'Mông', 'nhạc cụ khèn của dân tộc H\'Mông'],
        'Hmong-O': ['cái dù của người H\'Mông', 'cái ô của người H\'Mông'],
        'Hmong-Trang_phuc_nam': ['trang phục thổ cẩm của người H\'Mông nam', 'trang phục truyền thống của người H\'Mông nam'],
        'Hmong-Trang_phuc_nu': ['trang phục thổ cẩm của người H\'Mông nữ', 'trang phục truyền thống của người H\'Mông nữ'],
        'Khmer-Ao': ['áo Khmer', 'trang phục Sbai', 'áo Tầm Vông'],
        'Khmer-Coc': ['cốc chứa hoa của người Khmer', 'cốc Phka Slat', 'cốc Phka Chan'],
        'Khmer-Day_nit': ['dây nịt Khmer', 'thắt lưng Khmer'],
        'Khmer-Non': ['nón của người Khmer', 'nón Chada'],
        'Kinh-Ao_dai': ['áo dài'],
        'Kinh-Bong_sen': ['hoa sen'],
        'Kinh-Canh_sen': ['cánh sen'],
        'Kinh-La_sen': ['lá sen'],
        'Kinh-Non_la': ['nón lá'],
        'Kinh-Trang_phuc_ba_ba': ['áo bà ba'],
        'Kinh-Vay_mua_sen': ['váy có hoạ tiết hoa sen'],
        'Sap': ['cây sạp', 'sạp tre', 'múa sạp'],
        'Thai-Khan_choang': ['khăn choàng cổ của người Thái', 'khăn Piêu'],
        'Thai-Quan_den': ['quần xòe của người Thái', 'quần Thái'],
    }
    
    
    """
        Padding words are used to generate a sentence with keywords in the dictionary
            :type_1 : nouns related to dance
            :type_2 : verbs that go along with them
            :type_3 : words related to props
            :type_4 : words related to clothes
            :type_5 : words related to hats
            :type_6 : words related to accessories
            
            >>> From type_1 --> type_2: fixed
            >>> From type_3 --> type_6: Consists of 3 arrays (nouns, verbs, adjectives)
    """
    __padding_words = {
        
        'type_1': ['múa', 'điệu múa', 'nghệ thuật múa', 'các vũ công trong loại hình múa', 'văn hoá về múa'],
        'type_2': ['đi kèm', 'gắn liền', 'kết hợp', 'kết nối', 'tạo nên'],


        'type_3': [
            ['đạo cụ', 'dụng cụ', 'vật dụng'],
            ['dùng', 'sử dụng'],
            ['đặc biệt', 'tinh tế', 'mang đặc trưng của dân tộc'],
        ],

        'type_4': [
            [],
            ['mặc'],
            ['đẹp', 'trang trọng', 'mang đặc trưng của dân tộc'],
        ],

        'type_5': [
            [],
            ['được dùng để đội'],
            ['đẹp', 'tinh tế', 'mang đặc trưng của dân tộc']
        ],

        'type_6': [
            [],
            ['được đeo'],
            ['tinh xảo', 'tinh mĩ', 'mang đặc trưng của dân tộc']
        ]
    }
    
    
    # Includes all the rules for matching the keywords together.
    __category_dict = {
        # Prop
        'CoTu-Chieng': Category('CoTu-Chieng', 'type_3'),
        'CoTu-Trong': Category('CoTu-Trong', 'type_3'),
        'Dao-Chuong': Category('Dao-Chuong', 'type_3'),
        'Hmong-Khen': Category('Hmong-Khen', 'type_3'),
        'Hmong-O': Category('Hmong-O', 'type_3'),
        'Khmer-Coc': Category('Khmer-Coc', 'type_3'),
        'Kinh-Bong_sen': Category('Kinh-Bong_sen', 'type_3'),
        'Kinh-Canh_sen': Category('Kinh-Canh_sen', 'type_3'),
        'Kinh-La_sen': Category('Kinh-La_sen', 'type_3'),
        'Sap': Category('Sap', 'type_3'),

        # Clothes
        'CoTu-Trang_phuc_nam': Category('CoTu-Trang_phuc_nam', 'type_4'),
        'CoTu-Trang_phuc_nu': Category('CoTu-Trang_phuc_nu', 'type_4'),
        'Dao-Trang_phuc': Category('Dao-Trang_phuc', 'type_4'),
        'Dao_quan_chet-Trang_phuc': Category('Dao_quan_chet-Trang_phuc', 'type_4'),
        'Hmong-Trang_phuc_nam': Category('Hmong-Trang_phuc_nam', 'type_4'),
        'Hmong-Trang_phuc_nu': Category('Hmong-Trang_phuc_nu', 'type_4'),
        'Khmer-Ao': Category('Khmer-Ao', 'type_4'),
        'Kinh-Ao_dai': Category('Kinh-Ao_dai', 'type_4'),
        'Kinh-Trang_phuc_ba_ba': Category('Kinh-Trang_phuc_ba_ba', 'type_4'),
        'Kinh-Vay_mua_sen': Category('Kinh-Vay_mua_sen', 'type_4'),
        'Thai-Quan_den': Category('Thai-Quan_den', 'type_4'),

        # Hat
        'Dao-Mu': Category('Dao-Mu', 'type_5'),
        'Dao_quan_chet-Mu': Category('Dao_quan_chet-Mu', 'type_5'),
        'Khmer-Non': Category('Khmer-Non', 'type_5'),
        'Kinh-Non_la': Category('Kinh-Non_la', 'type_5'),

        # Accessory
        'Khmer-Day_nit': Category('Khmer-Day_nit', 'type_6'),
        'Thai-Khan_choang': Category('Thai-Khan_choang', 'type_6'),
    }
 
    __stopwords = ['bị', 'bởi ', 'cả ', 'các', 'cái', 'cần', 'càng', 'chỉ', 'chiếc', 'cho', 'chứ', 'chưa', 'chuyện', 
                   'có', 'có_thể', 'cứ', 'của', 'cùng', 'cũng', 'đã', 'đang', 'đây', 'để', 'đến_nỗi', 'đều', 'điều', 
                   'do', 'đó', 'được', 'dưới', 'gì', 'hơn', 'ít', 'khi', 'không', 'là', 'lại', 'lên', 'lúc', 
                   'mà', 'mỗi', 'một', 'một_cách', 'này', 'nên', 'nếu', 'ngay', 'nhất', 'nhiều', 'như', 'nhưng', 
                   'những', 'nơi', 'nữa', 'ở', 'phải', 'qua', 'ra', 'rằng', 'rằng', 'rất', 'rất', 'rồi', 'sau', 
                   'sẽ', 'so', 'sự', 'tại', 'theo', 'thì', 'trên', 'trong', 'trước', 'từ', 'từng', 'và', 'vẫn', 'vào', 
                   'vậy', 'về', 'vì', 'việc', 'với', 'vừa', 'và', 'của', 'các', 'là', 'ở', 'cho', 'về', 'cùng', 'theo', 
                   'lại', 'được', 'đến', 'trong', 'với', 'từ', 'khi', 'có', 'này', 'đó', 'rằng', 'mà', 'bởi', 'thì', 
                   'một', 'như', 'nhưng', 'vẫn', 'lên', 'để', 'cả', 'nên', 'hoặc', 'cũng', 'rất', 'nào', 'qua', 'ra', 
                   'đã', 'bằng', 'thế', 'nhiều', 'lúc', 'chỉ', 'tại', 'cách', 'đâu', 'này', 'còn', 'rồi', 'trong', 'giữa', 
                   'điều', 'vậy', 'vì', 'do']
    
    
    
    __rdrsegmenter = None  # Biến tĩnh với hai gạch dưới để bảo vệ kỹ hơn

    def __init__(self, vncorenlp_dir: str):
        if PreprocessingForSentences.__rdrsegmenter is None:
            PreprocessingForSentences.__rdrsegmenter = VnCoreNLP(annotators=["wseg"], save_dir=vncorenlp_dir)

    
    
    def get_top_labels(self, objects_frequencies: Dict[str, int], threshold: float=0.4) -> List[List[str | int]]:
        '''
            :param <objects_frequencies> = {
                'key is label': 'value is count',
                ...
            }
            
            :param <threshold> = 0.4, proportion of max count to consider as a top label

            :return <top_labels> = [
                [label, proportion],
                ...
            ] get k elements that sum of their proportion >= threshold
        '''
        
        top_labels = {}
        
        max_count = max(objects_frequencies.values())
        
        for key, value in objects_frequencies.items():
            proportion = value / max_count
            if proportion < threshold:
                break
            top_labels[key] = proportion
        
        return [list(val) for val in list(top_labels.items())]


    def get_key_words_from_labels(self, labels: List[List[str | int]]) -> List[List]:
        '''
            :param <labels> = [
                [label, proportion],
                ...
            ]

            :return [
                [key word, proportion],
                ...
            ]

        '''
        
        key_words = []
        
        for label, proportion in labels:
            random_key_word = random.choice(self.__dictionary[label])
            key_words.append([random_key_word, proportion])
                    
        return key_words


    def get_padding_words_from_labels(self, labels: List[List[str | int]]) -> List[str]:
        '''
            :param <labels> = [
                [label, proportion],
                ...
            ]

            :return [
                padding word 1, padding word 2, ...
            ]

        '''
        # Force to select one word from type_1 and type_2
        selected_padd_words = []
        selected_padd_words.append(random.choice(self.__padding_words['type_1']))
        selected_padd_words.append(random.choice(self.__padding_words['type_2']))

        # Get type list from the class of label
        type_list = [self.__category_dict[label].type_name for label, _ in labels]

        #  Randomly select one words by the type list
        for type_k in type_list:
            for words_list in self.__padding_words[type_k]:
                if len(words_list) > 0:
                    selected_padd_words.append(random.choice(words_list))

        return list(set(selected_padd_words))
    
    
    def are_matched_labels(self, labels: List[List[str | int]]) -> bool:
        '''
            :param <labels> = [
                [label, proportion],
                ...
            ]
            
        '''
        for i in range(len(labels) - 1):
            for j in range(i + 1, len(labels)):
                if not self.__category_dict[labels[i][0]].is_paired(labels[j][0]):
                    return False
        return True

    
    def create_words_for_sentence(self, labels: List[List[str | int]]) -> Sentence:
        '''
            :param <labels> = [
                [key is label, value is proportion],
                ...
            ]
        '''
        return Sentence(self.get_key_words_from_labels(labels), self.get_padding_words_from_labels(labels))
    
    

    
    def combine_words_for_sentences_list(self, top_labels: List[List[str | int]], threshold: float=0.7, n_sentences: List[int]=[2,5,2]) -> List[Sentence]:
        '''
        
            :param <top_labels> = [
                [label, proportion],
                ...
            ]

            :return <list of combinations of labels>
        '''
        
        if len(top_labels) == 0:
            return []
        
        sentences_list_1 = []
        sentences_list_2 = []
        sentences_list_3 = []
        
        
        # Function is used to check that can all of labels be matched, if sastifying then append all of them to the list 
        append_func = lambda sentences_list, labels: (sentences_list.append(self.create_words_for_sentence(labels)) 
                                                        if self.are_matched_labels(labels) else None)

        
        for i in range(len(top_labels)):
            if top_labels[i][1] >= threshold:
                sentences_list_1.append(self.create_words_for_sentence([top_labels[i]]))

        for i in range(len(top_labels)):
            for j in range(i + 1, len(top_labels)):
                append_func(sentences_list_2, [top_labels[i], top_labels[j]])

        for i in range(len(top_labels)):
            for j in range(i + 1, len(top_labels)):
                for k in range(j + 1, len(top_labels)):
                    append_func(sentences_list_3, [top_labels[i], top_labels[j], top_labels[k]])
        
        sentences_list = []
        sentences_list += random.sample(sentences_list_1, min(len(sentences_list_1), n_sentences[0]))
        sentences_list += random.sample(sentences_list_2, min(len(sentences_list_2), n_sentences[1]))
        sentences_list += random.sample(sentences_list_3, min(len(sentences_list_3), n_sentences[2]))
        return sentences_list
    
        
    def __unicode_normalize(self, text: str) -> str:
        return unicodedata.normalize('NFC', text)

    def __spelling_normalize(self, text: str) -> str:
        text = text.replace('kĩ', 'kỹ').replace('sỹ', 'sĩ').replace('xòe', 'xoè').replace('họa', 'hoạ')
        return text
    
    def __remove_stopwords(self, text: str) -> str:
        words = text.split()
        words = [word for word in words if word not in self.__stopwords]
        return ' '.join(words).replace(' , ',' ').replace(' .','')

    def __words_tokenize(self, text: str) -> str:
        return PreprocessingForSentences.__rdrsegmenter.word_segment(text)[0]
    
    def preprocess_text(self, text: str) -> str:
        temp = self.__unicode_normalize(text)
        temp = self.__spelling_normalize(temp)
        temp = self.__words_tokenize(temp)
        temp = self.__remove_stopwords(temp)
        return temp
