import joblib
import unicodedata
import re
from underthesea import text_normalize, word_tokenize

vectorizer = joblib.load('models/tfidf.joblib')
clf = joblib.load('models/clf3.joblib')  # We choose SVM here for quick result

with open('stopwords.txt', 'r', encoding='utf-8') as file:
    stopwords = file.readlines()
stopwords = [word.replace('\n', '') for word in stopwords]

label_mapping = {
    0: 'Politics',
    1: 'Business',
    2: 'Sports',
    3: 'Education',
    4: 'Wellness',
    5: 'Entertainment'
}


def clean_text(text):
    pattern = r'[^a-zA-Z\sÀ-ỹ]'
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text


def remove_stopwords(text):
    words = text.split()
    words = [word for word in words if word not in stopwords]

    return ' '.join(words)


def pre_process(sentence):
    sentence = unicodedata.normalize('NFC', sentence)
    sentence = clean_text(sentence)
    sentence = sentence.replace('kĩ', 'kỹ').replace(
        'mỳ', 'mì').replace('sỹ', 'sĩ').replace('lí ', ' lý ')
    sentence = text_normalize(sentence)
    sentence = word_tokenize(sentence, format='text')
    sentence = sentence.lower()
    sentence = remove_stopwords(sentence)

    return [sentence]


def predict_category(processed_sentence, clf):
    sentence_vector = vectorizer.transform(processed_sentence)
    predicted_category = clf.predict(sentence_vector)

    return predicted_category[0]


sentence = input('Enter the headline: ')

processed_sentence = pre_process(sentence)
predicted_label = predict_category(processed_sentence, clf)

predicted_category = label_mapping[predicted_label]
print('"' + sentence + '"')
print(f"Predicted Category: {predicted_category}")
