import streamlit as st
import requests

# 取得 GROQ API 金鑰（從 Streamlit Secrets 介面注入）
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 初始問題（Chain-of-Thought 問答起點）
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
    st.session_state.trigger_next = False

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
    res = requests.post(GROQ_API_URL, headers=headers, json=payload)
    return res.json()["choices"][0]["message"]["content"]

# UI 開始
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
        user_input = st.text_input("你的回答：", key=f"input_{st.session_state.step}")
        if st.button("送出回答", key=f"submit_{st.session_state.step}"):
            st.session_state.chat.append({"role": "user", "content": user_input})
            st.session_state.answers.append(user_input)
            st.session_state.step += 1
            st.session_state.trigger_next = True

    elif len(st.session_state.questions) == len(initial_questions):
        # Chain of Thought：讓 AI 提出進一步提問
        summary = "\\n".join([f"{i+1}. {q}：{a}" for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers))])
        follow_prompt = f"以下是使用者關於遺囑的初步回答，請根據內容提出 1~2 個進一步的釐清或補充問題，用中文發問：\\n{summary}"
        followup = call_groq(follow_prompt)
        new_questions = [line.strip("-：• ") for line in followup.split("\\n") if line.strip()]
        st.session_state.questions.extend(new_questions)
        st.session_state.chat.append({"role": "assistant", "content": new_questions[0]})
        st.session_state.step += 0  # 等待使用者回答新問題
        st.session_state.trigger_next = False

    else:
        st.session_state.done = True
        st.session_state.trigger_next = True

# 最終生成遺囑
if st.session_state.done and not st.session_state.generated:
    full_prompt = "\\n".join([f"{i+1}. {q}：{a}" for i, (q, a) in enumerate(zip(st.session_state.questions, st.session_state.answers))])
    will_prompt = f"請根據以下資訊幫我生成一份格式化、情感真摯、結尾附上日期的遺囑草稿：\\n{full_prompt}"
    with st.spinner("🖊️ 正在撰寫遺囑草稿…"):
        st.session_state.generated = call_groq(will_prompt)
        st.session_state.chat.append({"role": "assistant", "content": st.session_state.generated})
        st.experimental_rerun()

# 顯示結果
if st.session_state.generated:
    st.markdown("### 📝 你的遺囑草稿如下：")
    st.success(st.session_state.generated)

# 控制重新載入安全觸發
if st.session_state.trigger_next:
    st.session_state.trigger_next = False
    st.markdown("### 📝 你的遺囑草稿如下：")
    st.success(st.session_state.generated)
