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
    st.session_state.followup_questions_generated = False # 確保只生成一次延伸問題

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
        "temperature": 0.7 # 增加一點溫度，讓回答更自然
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
            # 確保 text_area 的預設值是空的，避免顯示上一個問題的答案
            user_input = st.text_area("你的回答：", key=f"input_{st.session_state.step}", height=100, value="")
            
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
                    st.rerun() # 使用 st.rerun() 確保 UI 更新
                    

    # ✅ 當回答完初始問題，且尚未生成延伸問題時，觸發延伸提問
    elif not st.session_state.followup_questions_generated: # 新增此條件
        st.info("已回答完主要問題，正在思考為您補充更多細節…")
        summary = "\n".join([f"{i+1}. {q}：{a}" for i, (q, a) in enumerate(zip(initial_questions, st.session_state.answers))])
        
        # 修改 prompt，明確要求 1-2 個問題，並確保每個問題獨立一行
        cot_prompt = f"請根據以下使用者提供的資訊，提出 **1 到 2 個** 可以幫助其更完善遺囑的**延伸問題**。請確保每個問題都以獨立的一行顯示，並使用清晰的繁體中文提問。例如：\n1. 請問您是否有特別想要指定受益人的比例？\n2. 您希望如何安排您的數位遺產？\n\n使用者提供的資訊：\n{summary}"
        
        # 在這裡呼叫 Groq API
        with st.spinner("正在生成延伸問題…"):
            follow = call_groq(cot_prompt)
            
        # 解析 Groq 回應，只取 1-2 個問題
        new_questions = [q.strip() for q in follow.split("\n") if q.strip()]
        new_questions = new_questions[:2] # 確保只取前兩個問題

        if new_questions: # 如果有生成新的問題
            st.session_state.questions.extend(new_questions)
            st.session_state.chat.append({"role": "assistant", "content": "讓我們深入一點，還有幾個問題想請教您…"})
            # 不再循環將所有問題添加到聊天紀錄，Streamlit 會自動在下一個 step 顯示當前問題
            st.session_state.followup_questions_generated = True # 標記已生成延伸問題
            st.rerun() # 強制重新運行以顯示新的問題
        else: # 如果沒有生成延伸問題，直接進入完成階段
            st.session_state.done = True
            st.rerun()


    # ✅ 所有問題都問完，才進入生成階段
    elif st.session_state.step == len(st.session_state.questions):
        st.session_state.done = True
        st.rerun() # 強制重新運行進入最終生成階段

# ✅ 最終階段：產出遺囑
if st.session_state.done and not st.session_state.generated:
    st.info("已收集所有必要資訊，正在為您撰寫遺囑草稿…")
    # 將所有問答組合成最終 prompt
    final_prompt_parts = []
    for i in range(len(st.session_state.questions)):
        q = st.session_state.questions[i]
        a = st.session_state.answers[i] if i < len(st.session_state.answers) else "未回答" # 避免索引超出範圍
        final_prompt_parts.append(f"問題: {q}\n回答: {a}")
    
    full_prompt = f"請根據以下資訊，幫我生成一份溫柔但格式清晰的中文遺囑草稿。請確保草稿包含所有提及的關鍵資訊。最後請加上今日日期結尾。\n\n{''.join(final_prompt_parts)}"

    with st.spinner("正在生成遺囑草稿…"):
        result = call_groq(full_prompt)
        st.session_state.generated = result
        st.session_state.chat.append({"role": "assistant", "content": result})
        st.rerun() # 強制重新運行以顯示最終結果

# 🧾 顯示最終遺囑草稿
if st.session_state.generated:
    st.markdown("### 📝 你的遺囑草稿如下：")
    st.success(st.session_state.generated)
