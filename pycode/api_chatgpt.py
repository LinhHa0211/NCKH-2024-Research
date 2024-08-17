from openai import OpenAI
from typing import List
from sentence import Sentence

class APIChatGPT:
    def __init__(self, OPENAI_API_KEY: str, model_name: str='gpt-4o-mini') -> None:
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = model_name

    
    def generate_sentences(self, sentences_list: List[Sentence]) -> None:
        
        question_prompt = f'Hãy tạo cho tôi {len(sentences_list)} câu, mỗi câu có tầm 15 đến 25 chữ và làm câu trở nên phong phú hơn. Câu trả lời không thêm kí tự đặc biệt, không in đậm các từ, không cần đánh số thứ tự. Với các gợi ý bên dưới:\n'
        
        for i in range(len(sentences_list)):
            question_prompt += f'Câu thứ {i + 1} có các từ khoá {sentences_list[i].get_key_words_for_create_text()} và các từ đệm {sentences_list[i].get_padding_words_for_create_text()}.\n'
        question_prompt += 'Chú ý: Chỉ tạo đúng với số câu đã yêu cầu, dùng từ khóa để biểu đạt ý chính trong câu. Bạn có thể sử dụng liên từ (hạn chế dùng dấu phẩy) để tăng độ mượt cho câu.\n'

        response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": question_prompt}]
                )

        # Access the content correctly
        content = response.choices[0].message.content
        text = content.split('.')
        
        while len(text) > len(sentences_list):
            text.pop(-1)

        for i in range(len(text)):
            sentences_list[i].api_text = text[i].strip() + '.'
        
        
    def generate_paragraph(self, texts: List[str], n_sentences_padding: int, dance_name: str):
        question_prompt = f'Hãy tạo cho tôi một đoạn văn mô tả về {dance_name}, có khoảng {len(texts) + n_sentences_padding} câu, từ các câu bên dưới:\n'
        
        for text in texts:
            question_prompt += f'\t - {text}\n'
        
        question_prompt += '**Lưu ý quan trọng**: Dùng các câu đã gợi ý để biểu đạt ý chính trong đoạn văn. Bạn có thể sử dụng liên từ, hoặc các câu kết nối để tăng độ mượt đoạn văn.\n'

        response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": question_prompt}]
                )

        # Access the content correctly
        return response.choices[0].message.content
        

