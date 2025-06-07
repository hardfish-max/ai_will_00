from streamlit_lottie import st_lottie #動畫
import requests
import base64 #匯入圖片、音檔
import streamlit as st
   
# 取得 GROQ API 金鑰（從 Streamlit Secrets 介面匯入）
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 初始問題
initial_questions = [
    "你希望這份遺囑是寫給誰的？",
    "你有什麼話想對這個人說？",
    "有沒有什麼未完成的心願或故事，想交代的？",
    "是否有任何財產、物品、或資料需要安排？",
    "你想以什麼語氣或風格呈現這份遺囑？（例如莊嚴、溫柔、幽默）"
]

# --- 頁面設定 ---
st.set_page_config(page_title="AI 遺囑生成器", page_icon="🕊", layout="wide")

#動畫元素
def load_lottieurl(url: str):
    r = requests.get(url)
    print("Status code:", r.status_code)
    if r.status_code != 200:
        return None
    return r.json()

# ✅ 使用完整的 JSON 連結
lottie_url = "https://lottie.host/8e67f872-e483-4e8c-9b28-6ca11329eb42/rgznX6aYYt.json"
lottie_animation = load_lottieurl(lottie_url)



# --- 初始化 session_state ---
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.questions = initial_questions.copy()
    st.session_state.initial_questions = initial_questions.copy()
    st.session_state.answers = []  # 儲存所有回答
    st.session_state.chat = []     # 儲存對話紀錄
    st.session_state.done = False  # 標誌是否完成所有問題
    st.session_state.generated = ""# 最終生成的遺囑草稿
    st.session_state.followup_questions_generated = False # 確保只生成一次延伸問題
    st.session_state.current_user_input = "" # 用於暫存用戶輸入，避免渲染問題

# Groq API 呼叫函數
def call_groq(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "你是一位溫柔且善於理解人心的助手，幫助使用者書寫遺囑，請用台灣繁體中文回答。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    try:
        res = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        st.error(f"呼叫 Groq API 時發生錯誤: {e}")
        return "很抱歉，API 呼叫失敗，請稍後再試。"
      


# --- 功能函式：轉檔成 base64 ---
def to_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# --- 加入背景圖片與音樂 ---
image_base64 = to_base64("assets/background.jpg")      
audio_base64 = to_base64("assets/echoofsadness.mp3")    

st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{image_base64}");
        background-size: cover;
        background-attachment: fixed;
    }}
    
    /* 強制所有文字為黑色 */
    html, body, .stApp, .css-18ni7ap, .css-1d391kg, .css-qrbaxs, .css-ffhzg2, .css-1v0mbdj {{
        color: black !important;
    }}
    
    /* 所有輸入框、選擇框、文字區塊背景為白，文字為黑 */
    input, textarea, .stTextInput input, .stTextArea textarea, .stSelectbox, .stMultiSelect, .stNumberInput input {{
        background-color: white !important;
        color: black !important;
    }}

    /* 按鈕樣式 */
    button, .stButton>button {{
        background-color: white !important;
        color: black !important;
        border: 1px solid #ccc !important;
        border-radius: 8px !important;
    }}
    /* 音樂播放器樣式 */
    .audio-player {{
        position: fixed;
        bottom: 40px;
        right: 20px;
        width: 500px;
        opacity: 0.7;
        z-index: 1000;
    }}
    audio {{
        width: 100% !important;
        min-width: 180px !important;
        min-height: 32px !important;
        display: block !important;
    }}
    .audio-player:hover {{
        opacity: 1.0;
    }}
    
     /*測攔 */
    .sidebar-container {{
        position: absolute;
        top: 120px;
        right: 40px;
        width: 300px;
        background: rgba(255, 255, 255, 0.85);
        padding: 16px;
        border-radius: 12px;
        font-size: 15px;
        color: #222;
    }}
    </style>
   
   # <div class="audio-player">
    #    <audio autoplay loop controls>
    #        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    #    </audio>
   # </div>
    
   #####
   
   <div class="audio-player">
       <audio id="bg-music" autoplay loop controls>
           <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
       </audio>
   </div>
   <!-- 嘗試強制播放 -->
   <script>
        window.addEventListener('load', function() {{
            const music = document.getElementById('bg-music');
            const playPromise = music.play();
            if (playPromise !== undefined) {{
                playPromise.catch(function(error) {{
                    console.warn("自動播放失敗，瀏覽器可能禁止自動撥放：", error);
                }});
            }}
        }});
    </script>
    
    """,
    unsafe_allow_html=True
)


   


# 顯示動畫
if lottie_animation:
    st_lottie(
        lottie_animation,
        speed=1,
        reverse=False,
        loop=True,
        quality="high",
        height=300,
        key="ending_animation"
    )
else:
    st.error("動畫載入失敗，請確認 URL 是否正確。")



# --- UI 主視覺區塊 設定 ---   
# st.title("🕊 AI您好，我的遺囑如下…")
# st.markdown("這是一個由 AI 協助撰寫遺囑的互動工具，請放心作答，最後會生成一份完整草稿。")
# st.toast("🎶 本頁有音樂播放器，請善用右下角控制！", icon="🎶") 
#st.markdown("""
#<div style='background: linear-gradient(90deg, #f9d423 0%, #ff4e50 100%); padding: 16px; border-radius: 10px; margin-bottom: 24px; color: white; font-size: 22px;'>
#    🕊️ <b>歡迎使用 AI 遺囑撰寫小助手</b><br>
#    本工具將引導您輕鬆撰寫專屬遺囑，過程中所有資料僅供草稿產生，不會被儲存。
#</div>
#""", unsafe_allow_html=True)

#st.info("🎶 本頁右下角有背景音樂播放器，讓您在舒適氛圍下進行撰寫。")

#current_step = 1
#total_steps = 5
#st.progress(current_step/total_steps, text=f"步驟 {current_step} / {total_steps}")

#st.markdown("""
#<div style='font-size:16px; color:#555; margin-top:18px; margin-bottom:0;'>
 #   💡 <i>「遺囑是對摯愛的最後叮嚀，也是對自己人生的溫柔交代。」</i>
#</div>
#""", unsafe_allow_html=True)


#-----
# --- 主視覺與歡迎區塊 ---
col1, col2 = st.columns([2, 1])  # 左：主畫面，右：提示欄

with col1:
    # 🟦 主畫面內容：動畫、標題、進度、問題等
    #st.markdown("""
    #<div style='background: linear-gradient(90deg, #f9d423 0%, #ff4e50 100%); padding: 16px; border-radius: 10px; margin-bottom: 24px; color: white; font-size: 22px;'>
    #    🕊️ <b>AI您好，我的遺囑如下…</b><br>
    #    本工具將引導您輕鬆撰寫專屬遺囑，過程中所有資料僅供草稿產生，不會被儲存。
    #</div>
    #""", unsafe_allow_html=True)
   
    # --- 插入動畫 --
    #if lottie_animation:
    #    st_lottie(lottie_animation, height=140, key="main_anim")

    
   <div style='font-size:36px; font-weight:bold; color:#222; padding:8px 0;'>
      🕊 AI您好，我的遺囑如下…
   </div>

    

with col2:
    # 🟨 側欄：說明區塊
    st.markdown("<i>💡 「遺囑是對摯愛的最後叮嚀，也是對自己人生的溫柔交代。」</i>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background: rgba(255,255,255,0.9); padding: 16px; border-radius: 12px; font-size: 15px; color: #222; box-shadow: 0 0 8px rgba(0,0,0,0.1);'>
        <b>🎶 音樂播放提示：</b><br>
        右下角播放器可開啟或暫停背景音樂。<br><br>
    </div>
    """, unsafe_allow_html=True) 
    with st.expander("❓ 常見問題"):
        st.write("""
           - 撰寫的內容會被保存嗎？  
             不會，所有資料僅用於產生草稿，不會儲存。
             
           - <我不知道怎麼開始怎麼辦？  
             試著先寫一句感謝或道別的話，例如「謝謝你陪我這一生」。
             
           - 寫的時候覺得想哭，是正常的嗎？
             很正常，這是對人生與親情深層的整理，請溫柔對待自己。
             
         """)









# 顯示對話紀錄
for entry in st.session_state.chat:
    if entry["role"] == "user":
        st.markdown(f"🧑‍💬 **你：** {entry['content']}")
    else:
        st.markdown(f"🤖 **AI：** {entry['content']}")


# --- 提問流程 ---
if not st.session_state.done:
    if st.session_state.step < len(st.session_state.questions):
        current_q = st.session_state.questions[st.session_state.step]
        with col1:
            #st.markdown(f"**問題 {st.session_state.step + 1}：** {current_q}")
            st.markdown(f"""
<           div style='font-size:24px; font-weight:bold; margin-bottom:8px; color:#333;'>
            問題 {st.session_state.step + 1}：{current_q}
            </div>
            """, unsafe_allow_html=True)



           
            # 使用一個佔位符來處理輸入框和按鈕
            # 將輸入框的 current_user_input 從 session_state 中取值
            # 這樣在重新運行時，text_area 的值會保持，直到明確提交。
            user_input_val = st.session_state.current_user_input
            
            user_input = st.text_area(
                "您的回答：",
                key=f"input_{st.session_state.step}",
                placeholder="請在這裡輸入你的回答⋯⋯",
                height=100,
                value=user_input_val # 使用 session_state 中的暫存值
            )
            
            # 當 text_area 的值發生變化時，更新 session_state 中的暫存值
            if user_input != st.session_state.current_user_input:
                st.session_state.current_user_input = user_input
                # 注意：這裡不應該直接觸發 rerun，否則會陷入循環
            
            # 送出按鈕
            if st.button("送出回答", key=f"submit_q_{st.session_state.step}"):
                if st.session_state.current_user_input.strip() == "": # 檢查暫存值
                    st.warning("請輸入您的回答。")
                else:
                    # 提交回答前，將暫存值添加到 chat 和 answers
                    st.session_state.chat.append({"role": "user", "content": st.session_state.current_user_input})
                    st.session_state.answers.append(st.session_state.current_user_input)
                    
                    # 清空暫存值，為下一個問題做準備
                    st.session_state.current_user_input = "" 
                    
                    st.session_state.step += 1
                    st.rerun() # 提交回答後強制重新運行，顯示下一個問題或進入下一階段
                
            #current_step = len(session_state.step)
            #total_steps = 5
             #   st.progress(current_step / total_steps, text=f"步驟 {current_step} / {total_steps}")
    # --- 延伸問題生成邏輯 ---
# 階段 2: 生成延伸問題的提示階段（僅在生成時顯示資訊，不需回答）
    # 只有當所有初始問題都回答完，且延伸問題尚未生成時進入此階段
    elif st.session_state.step == len(st.session_state.initial_questions) and not st.session_state.followup_questions_generated:
        st.info("已回答完主要問題，正在思考為您補充更多細節…")
        
        # 整合所有初始問題的回答作為 AI 生成延伸問題的上下文
        summary = "\n".join([f"{i+1}. {q}：{a}" for i, (q, a) in enumerate(zip(st.session_state.initial_questions, st.session_state.answers[:len(st.session_state.initial_questions)]))])
        
        cot_prompt = f"請根據以下使用者提供的資訊，提出 **1 到 2 個** 可以幫助其更完善遺囑的**延伸問題**。請確保每個問題都以獨立的一行顯示，並使用清晰的繁體中文提問。例如：\n1. 請問您是否有特別想要指定受益人的比例？\n2. 您希望如何安排您的數位遺產？\n\n使用者提供的資訊：\n{summary}"
        
        with st.spinner("正在生成延伸問題…"):
            follow = call_groq(cot_prompt)
            
        new_questions = [q.strip() for q in follow.split("\n") if q.strip()]
        new_questions = [q for q in new_questions if q.startswith(('1.', '2.', '3.'))] # 篩選確保是問題格式
        new_questions = new_questions[:2] # 確保只取前兩個問題

        if new_questions:
            # 將新問題添加到總問題列表中，這樣後續的 step 就能處理它們
            st.session_state.questions.extend(new_questions)
            st.session_state.chat.append({"role": "assistant", "content": "好的，我們還有幾個問題想請教您，這能幫助我們完善遺囑…"})
            st.session_state.followup_questions_generated = True # 標記延伸問題已生成
            st.rerun() # 強制重新運行，讓 Streamlit 在下一個 step 顯示第一個延伸問題

        else: # 如果沒有生成延伸問題，直接進入完成階段
            st.session_state.done = True
            st.rerun()

    # 階段 3: 所有問題問完，進入最終生成階段
    elif st.session_state.step == len(st.session_state.questions) and not st.session_state.done:
        st.session_state.done = True
        st.rerun()

# --- 最終階段：產出遺囑 ---
if st.session_state.done and not st.session_state.generated:
    st.info("已收集所有必要資訊，正在為您撰寫遺囑草稿…")
    final_prompt_parts = []
    for i in range(len(st.session_state.questions)):
        q = st.session_state.questions[i]
        a = st.session_state.answers[i] if i < len(st.session_state.answers) else "未回答"
        final_prompt_parts.append(f"問題: {q}\n回答: {a}")
    
    full_prompt = f"請根據以下資訊，幫我生成一份溫柔但格式清晰的中文遺囑草稿。請確保草稿包含所有提及的關鍵資訊。最後請加上今日日期結尾。\n\n{''.join(final_prompt_parts)}"

    with st.spinner("正在生成遺囑草稿…"):
        result = call_groq(full_prompt)
        st.session_state.generated = result
        st.session_state.chat.append({"role": "assistant", "content": result})
        st.rerun() # 生成遺囑後強制重新運行，以顯示最終結果

# --- 顯示最終遺囑草稿 ---
if st.session_state.generated:
    st.markdown("### 📝 你的遺囑草稿如下：")
    st.success(st.session_state.generated)
