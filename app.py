import streamlit as st
from pypinyin import pinyin, Style
from gtts import gTTS
from io import BytesIO
import random

# ==================== 初始化設定 ====================
st.set_page_config(page_title="中文注音查詢平板版", layout="centered")

# ==================== 功能函式區 ====================

def get_random_color():
    """ 產生隨機且較深、清晰的顏色 """
    r = random.randint(0, 180)
    g = random.randint(0, 180)
    b = random.randint(0, 180)
    return f'#{r:02x}{g:02x}{b:02x}'

def generate_zhuyin_html(text):
    """ 將文字與注音轉換為直式對照卡片 HTML/CSS """
    result = pinyin(text, style=Style.BOPOMOFO)
    tone_marks = ['ˊ', 'ˇ', 'ˋ', '˙']
    
    # 依字數動態調整字體大小
    hanzi_size = "24px" if len(text) <= 5 else "28px"
    zhuyin_size = "16px" if len(text) <= 5 else "16px"
    
    html = '<div style="display: flex; flex-direction: row; flex-wrap: wrap; gap: 16px; justify-content: center; align-items: flex-end; margin-top: 30px;">'
    
    for char, item in zip(text, result):
        zhuyin = item[0]
        
        # 分離聲調與注音主體 (聲調放最上方)
        tone = [c for c in zhuyin if c in tone_marks]
        body = [c for c in zhuyin if c not in tone_marks]
        ordered_chars = tone + body
        
        color = get_random_color()
        
        # 單字卡片容器：包含上方的直排注音與下方的漢字
        html += f'''
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: flex-end; background-color: #ffffff; padding: 16px 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
            <!-- 注音直排區 -->
            <div style="display: flex; flex-direction: column; align-items: center; color: {color}; font-size: {zhuyin_size}; font-family: \'Microsoft JhengHei\', sans-serif; font-weight: bold; margin-bottom: 8px;">
        '''
        for z_char in ordered_chars:
            html += f'<div style="line-height: 1.1;">{z_char}</div>'
            
        html += f'''
            </div>
            <!-- 漢字區 -->
            <div style="font-size: {hanzi_size}; font-family: \'Microsoft JhengHei\', sans-serif; font-weight: bold; color: #2c3e50;">
                {char}
            </div>
        </div>
        '''
        
    html += '</div>'
    return html

def clear_all():
    """ 清除狀態與輸入框 """
    st.session_state.input_text = ""
    st.session_state.result_text = None

# ==================== Session State 初始化 ====================
if 'input_text' not in st.session_state:
    st.session_state.input_text = ""
if 'result_text' not in st.session_state:
    st.session_state.result_text = None
if 'play_audio' not in st.session_state:
    st.session_state.play_audio = False

# ==================== 主視窗介面佈局 ====================

# 14px 標題設定
st.markdown("<p style='font-size: 14px; font-weight: bold; font-family: \"Microsoft JhengHei\", sans-serif; margin: 0;'>📚 中文注音查詢</p>", unsafe_allow_html=True)
st.markdown("<hr style='margin-top: 8px; margin-bottom: 20px;'>", unsafe_allow_html=True)

# 輸入區與選項
text = st.text_input("請輸入文字：", key="input_text", placeholder="例如：你好嗎")
speak_chinese = st.checkbox("朗讀中文", value=True)

# 按鈕區 (欄位並排)
col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 查詢注音與朗讀", use_container_width=True):
        if not text.strip():
            st.warning("請輸入文字！")
        else:
            st.session_state.result_text = text.strip()
            st.session_state.play_audio = speak_chinese

with col2:
    st.button("🗑️ 清除重填", on_click=clear_all, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==================== 結果顯示區 ====================
if st.session_state.result_text:
    # 顯示注音與漢字 HTML 排版
    zhuyin_html = generate_zhuyin_html(st.session_state.result_text)
    st.markdown(zhuyin_html, unsafe_allow_html=True)
    
    # 處理語音朗讀 (使用 BytesIO 避開硬碟暫存)
    if st.session_state.play_audio:
        try:
            mp3_fp = BytesIO()
            tts = gTTS(text=st.session_state.result_text, lang='zh-TW')
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            st.audio(mp3_fp, format='audio/mp3', autoplay=True)
        except Exception as e:
            st.error(f"語音播放失敗: {e}")
            
        st.session_state.play_audio = False
