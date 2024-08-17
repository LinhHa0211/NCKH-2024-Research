import sys
sys.path.append('./pycode')

from pycode import main

import streamlit as st
import json
import time
import threading

# Streamlit UI setup
st.set_page_config(layout="wide", page_title="VIMVA", page_icon="D:/NCKH/ctu_logo.png")

# Định nghĩa biến HTML đóng thẻ </div>
CLOSE_DIV = '</div>'

# Thêm CSS để tùy chỉnh bố cục
st.markdown(
    """
    <style>
    .centered-title, .full-screen, .column {
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .centered-title {
        height: 80px;
    }
    .full-screen {
        height: calc(100vh - 80px);
        width: 100%;
    }
    .column {
        flex-direction: column;
        height: 100%;
    }
    .column > * {
        margin: 10px 0;
        width: 80%;
    }
    .rounded-box {
        border: 2px solid #C0C0C0;
        border-radius: 15px;
        padding: 20px;
        margin: 20px;
        background-color: #f9f9f9;
        box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
        color: black;
    }
    .rounded-box p {
        font-size: 18px;
        text-align: justify;
    }
    
    /* Định nghĩa thanh tiến trình bằng HTML và CSS */
    
    .outer-progress-bar {
        width: 100%; 
        background-color: #f3f3f3;
    }
    .inner-progress-bar {
        width: 100%; 
        height: 20px; 
        background-image: linear-gradient(45deg, #007bff 25%, #0056b3 25%, #0056b3 50%, #007bff 50%, #007bff 75%, #0056b3 75%, #0056b3); 
        background-size: 40px 40px; 
        animation: move 3s linear infinite;"
    }
    
    @keyframes move {
        0% {
            background-position: 0 0;
        }
        100% {
            background-position: 100% 100%;
        }
    }
    
    </style>
    """,
    unsafe_allow_html=True,
)

# Hàng đầu tiên: Tiêu đề ở giữa trang
st.markdown('<div class="centered-title"><h1>VIMVA SYSTEM</h1>' +
            CLOSE_DIV, unsafe_allow_html=True)

# Hàng thứ hai: Chia thành hai cột
left_column, center_column, right_column = st.columns([2, 1, 4])

# Nội dung của cột bên trái
with left_column:
    st.markdown('<div class="column full-screen">', unsafe_allow_html=True)
    uploaded_video = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])
    submit_button = st.button("Submit")
    st.markdown(CLOSE_DIV, unsafe_allow_html=True)

# Nội dung của cột bên phải
with right_column:
    st.markdown('<div class="column full-screen">', unsafe_allow_html=True)

    # Hiển thị hình ảnh trước khi tải lên video và nhấn Submit
    if not (submit_button and uploaded_video):
        st.image('D:/NCKH/empty_video.png',
                 use_column_width=True)

    # Hiển thị video sau khi nhấn Submit
    if submit_button:
        if uploaded_video:
            st.video(uploaded_video)
        else:
            st.warning("Please upload a video to continue.")

    st.markdown(CLOSE_DIV, unsafe_allow_html=True)


# Hàng thứ ba: Hiển thị câu hỏi giả lập khi nhấn nút submit
def run_prediction(uploaded_video, config, result_container):
    # Giả lập thời gian dự đoán thực tế
    response = main.predict(uploaded_video=uploaded_video, **config)
    result_container['response'] = response


if submit_button and uploaded_video:
    # Đọc file config
    with open("D:/NCKH/config.json", 'r') as file:
        config = json.load(file)

    # Container để lưu kết quả
    result_container = {}

    # Tạo và chạy luồng để thực hiện hàm dự đoán
    prediction_thread = threading.Thread(target=run_prediction, args=(uploaded_video, config, result_container))
    prediction_thread.start()

    # Hiển thị thanh tiến trình
    progress_bar = st.markdown('<div class="outer-progress-bar"><div class="inner-progress-bar"></div></div>', unsafe_allow_html=True)

    # Chờ cho đến khi quá trình dự đoán hoàn tất
    while prediction_thread.is_alive():
        time.sleep(0.1)  # Điều chỉnh tốc độ kiểm tra tiến trình

    # Khi dự đoán hoàn tất, xóa thanh tiến trình và hiển thị kết quả
    progress_bar.empty()
    st.markdown(f'<div class="rounded-box">{result_container["response"]}</div>', unsafe_allow_html=True)