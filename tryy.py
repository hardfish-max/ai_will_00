import streamlit as st
import requests

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

# 初始化 session_state
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.questions = initial_questions.copy()
    st.session_state.answers = []
    st.session_state.chat = []
    st.session_state.done = False
    st.session_state.generated = ""
    st.session_state.followup_added = False # 避免重複加問題

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
        ]
    }
    try:
        res = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60) # 增加 timeout
        res.raise_for_status() # 檢查 HTTP 錯誤
        return res.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        st.error(f"呼叫 Groq API 時發生錯誤: {e}")
        return "很抱歉，API 呼叫失敗，請稍後再試。"

# UI 設定
st.title("🕊 AI您好，我的遺囑如下…")
st.markdown("這是一個由 AI 協助撰寫遺囑的互動工具，請放心作答，最後會生成一份完整草稿。")

# 顯示對話紀錄
for entry in st.session_state.chat:
    if entry["role"] == "user":
        st.markdown(f"🧑‍💬 **你：** {entry['content']}")
    else:
        st.markdown(f"🤖 **AI：** {entry['content']}")

# 提問流程
if not st.session_state.done:
    if st.session_state.step < len(st.session_state.questions):
        current_q = st.session_state.questions[st.session_state.step]
        st.markdown(f"**問題 {st.session_state.step + 1}：** {current_q}")
        
        # 使用一個佔位符來處理輸入框和按鈕，有時可以減少 DOM 混淆
        input_placeholder = st.empty()
        with input_placeholder.container():
            user_input = st.text_area("你的回答：", key=f"input_{st.session_state.step}", height=100)
            
            # 使用一個唯一的鍵來確保按鈕是獨立的
            if st.button("送出回答", key=f"submit_q_{st.session_state.step}"):
                if user_input.strip() == "":
                    st.warning("請輸入您的回答。")
                else:
                    st.session_state.chat.append({"role": "user", "content": user_input})
                    st.session_state.answers.append(user_input)
                    st.session_state.step += 1
                    # 清除目前的輸入框和按鈕，讓 Streamlit 在下一個 step 重新渲染新的
                    input_placeholder.empty()
                    # 強制重新運行，確保 UI 更新
                    st.rerun() # 使用 st.rerun() 代替 st.session_state.trigger_next = True
                    

    # ✅ 當回答完初始問題，觸發延伸提問
    elif not st.session_state.followup_added:
        # 顯示一個提示，讓使用者知道正在生成延伸問題
        st.info("已回答完主要問題，正在思考為您補充更多細節…")
        summary = "\n".join([f"{i+1}. {q}：{a}" for i, (q, a) in enumerate(zip(initial_questions, st.session_state.answers))])
        cot_prompt = f"請根據以下回答，提出 1~2 個可以補充的延伸問題：\n{summary}"
        
        # 在這裡呼叫 Groq API
        with st.spinner("正在生成延伸問題…"):
            follow = call_groq(cot_prompt)
            
        new_questions = [q.strip("•-： ") for q in follow.split("\n") if q.strip()]
        
        # ✅ 加入延伸問題
        st.session_state.questions.extend(new_questions)
        st.session_state.chat.append({"role": "assistant", "content": "讓我們深入一點…"}) # 簡單提示
        for nq in new_questions:
            st.session_state.chat.append({"role": "assistant", "content": nq})
        st.session_state.followup_added = True
        st.rerun() # 強制重新運行以顯示新的問題

    # ✅ 所有問題都問完，才進入生成階段
    elif st.session_state.step == len(st.session_state.questions):
        st.session_state.done = True
        st.rerun() # 強制重新運行進入最終生成階段

# ✅ 最終階段：產出遺囑
if st.session_state.done and not st.session_state.generated:
    st.info("已收集所有必要資訊，正在為您撰寫遺囑草稿…")
    final_prompt = "\n".join([f"{i+1}. {q}：{a}" for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers))])
    full_prompt = f"請根據以下資訊，幫我生成一份溫柔但格式清晰的中文遺囑草稿：\n{final_prompt}\n請加上今日日期結尾。"

    with st.spinner("正在生成遺囑草稿…"):
        result = call_groq(full_prompt)
        st.session_state.generated = result
        st.session_state.chat.append({"role": "assistant", "content": result})
        st.rerun() # 強制重新運行以顯示最終結果

# 🧾 顯示最終遺囑草稿
if st.session_state.generated:
    st.markdown("### 📝 你的遺囑草稿如下：")
    st.success(st.session_state.generated)
