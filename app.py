import streamlit as st
from pypinyin import pinyin, Style
from gtts import gTTS
import tempfile
import random

# ==================== 初始化設定 ====================
st.set_page_config(page_title="中文注音查詢平板版", layout="centered")

# ==================== 功能函式區 ====================

def get_random_color():
    """ 產生隨機且較深、清晰的顏色 """
    r = random.randint(0, 200)
    g = random.randint(0, 200)
    b = random.randint(0, 200)
    return f'#{r:02x}{g:02x}{b:02x}'

def generate_zhuyin_html(text):
    """ 將注音轉換為直式排版的 HTML/CSS """
    result = pinyin(text, style=Style.BOPOMOFO)
    tone_marks = ['ˊ', 'ˇ', 'ˋ', '˙']
    
    # 字體大小設定 (超過 5 個字自動縮小以適應畫面)
    font_size = "24px" if len(text) <= 5 else "16px"
    
    # 外層容器：使用 flexbox 讓多個字橫向排列，且對齊底部 (align-items: flex-end)
    html = '<div style="display: flex; flex-direction: row; flex-wrap: wrap; gap: 30px; justify-content: center; align-items: flex-end; margin-top: 50px;">'
    
    for item in result:
        zhuyin = item[0]
        
        # 分離聲調與注音主體
        tone = [c for c in zhuyin if c in tone_marks]
        body = [c for c in zhuyin if c not in tone_marks]
        ordered_chars = tone + body  # 確保聲調在最上方
        
        color = get_random_color()
        
        # 內層容器：單一注音的直向排列
        html += f'<div style="display: flex; flex-direction: column; align-items: center; justify-content: flex-end; color: {color}; font-size: {font_size}; font-family: \'Microsoft JhengHei\', sans-serif; font-weight: bold; background-color: #f5f6fa; padding: 10px; border-radius: 10px;">'
        
        for char in ordered_chars:
            html += f'<div style="line-height: 1.2;">{char}</div>'
            
        html += '</div>'
        
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

st.title("📚 中文注音查詢")
st.markdown("<hr>", unsafe_allow_html=True)

# 輸入區與選項
text = st.text_input("請輸入文字：", key="input_text", placeholder="例如：你好嗎")
speak_chinese = st.checkbox("朗讀中文", value=True)

# 按鈕區 (使用欄位並排)
col1, col2 = st.columns(2)

with col1:
    if st.button("🔍 查詢注音與朗讀", use_container_width=True):
        if not text.strip():
            st.warning("請輸入文字！")
        else:
            st.session_state.result_text = text.strip()
            st.session_state.play_audio = speak_chinese  # 只在按下按鈕的當下標記需要播放語音

with col2:
    st.button("🗑️ 清除重填", on_click=clear_all, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==================== 結果顯示區 ====================
if st.session_state.result_text:
    # 顯示注音 HTML 排版
    zhuyin_html = generate_zhuyin_html(st.session_state.result_text)
    st.markdown(zhuyin_html, unsafe_allow_html=True)
    
    # 處理語音朗讀
    if st.session_state.play_audio:
        try:
            tts = gTTS(text=st.session_state.result_text, lang='zh-TW')
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                tts.save(fp.name)
                # 使用 Streamlit 的 audio 元件，並啟用 autoplay 自動播放
                st.audio(fp.name, format='audio/mp3', autoplay=True)
        except Exception as e:
            st.error(f"語音播放失敗: {e}")
            
        # 播放完後重置狀態，避免下次單純點擊頁面其他元件時重複發聲
        st.session_state.play_audio = False
