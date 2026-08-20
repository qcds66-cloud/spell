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
    r = random.randint(0, 160)
    g = random.randint(0, 160)
    b = random.randint(0, 160)
    return f'#{r:02x}{g:02x}{b:02x}'

def parse_zhuyin(zhuyin_str):
    """ 正確分離注音主體與聲調 """
    tone_marks = ['ˊ', 'ˇ', 'ˋ', '˙']
    tone = ""
    body = []
    
    for char in zhuyin_str:
        if char in tone_marks:
            tone = char
        else:
            body.append(char)
            
    return body, tone

def generate_zhuyin_html(text):
    """ 將文字與注音轉換為直式對照卡片 (無多餘縮排，防止 Markdown 渲染錯誤) """
    result = pinyin(text, style=Style.BOPOMOFO)
    
    hanzi_size = "36px" if len(text) <= 5 else "28px"
    zhuyin_size = "20px" if len(text) <= 5 else "16px"
    
    cards = []
    for char, item in zip(text, result):
        zhuyin = item[0]
        body, tone = parse_zhuyin(zhuyin)
        color = get_random_color()
        
        # 組合注音主體直排內容
        body_html = "".join([f'<div style="line-height: 1.1;">{b}</div>' for b in body])
        
        # 聲調處理：輕聲(˙)置頂；二/三/四聲(ˊ ˇ ˋ)置於右上/右側
        if tone == '˙':
            zhuyin_block = f'<div style="display:flex; flex-direction:column; align-items:center;"><div style="line-height:1;">˙</div>{body_html}</div>'
        elif tone:
            zhuyin_block = f'<div style="display:flex; flex-direction:row; align-items:center;">' \
                           f'<div style="display:flex; flex-direction:column; align-items:center;">{body_html}</div>' \
                           f'<div style="font-size: 0.8em; margin-left: 2px; align-self: flex-start;">{tone}</div></div>'
        else:
            zhuyin_block = f'<div style="display:flex; flex-direction:column; align-items:center;">{body_html}</div>'

        # 單字卡片 HTML（單行緊湊寫法，避免 Markdown 解析錯誤）
        card = (
            f'<div style="display: flex; flex-direction: column; align-items: center; justify-content: flex-end; '
            f'background-color: #ffffff; padding: 16px 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">'
            f'<div style="color: {color}; font-size: {zhuyin_size}; font-family: \'Microsoft JhengHei\', sans-serif; '
            f'font-weight: bold; margin-bottom: 8px;">{zhuyin_block}</div>'
            f'<div style="font-size: {hanzi_size}; font-family: \'Microsoft JhengHei\', sans-serif; font-weight: bold; '
            f'color: #2c3e50;">{char}</div>'
            f'</div>'
        )
        cards.append(card)
    
    container = f'<div style="display: flex; flex-direction: row; flex-wrap: wrap; gap: 16px; justify-content: center; align-items: flex-end; margin-top: 20px;">{"".join(cards)}</div>'
    return container

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
    zhuyin_html = generate_zhuyin_html(st.session_state.result_text)
    st.markdown(zhuyin_html, unsafe_allow_html=True)
    
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
