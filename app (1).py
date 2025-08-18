
import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# ------------------------------
# Setup
# ------------------------------
st.set_page_config(page_title="🦙 LLaMA-2 Chatbot", layout="centered")

MODEL_ID = "meta-llama/Llama-2-7b-chat-hf"
SYSTEM_PROMPT = "You are a helpful assistant."

@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        device_map="auto",
        torch_dtype="auto"
    )
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
    return tokenizer, pipe

tokenizer, pipe = load_model()

# ------------------------------
# Helpers
# ------------------------------
def format_prompt(history, user_message):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for u, a in history:
        if u:
            messages.append({"role": "user", "content": u})
        if a:
            messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": user_message})

    prompt = ""
    for m in messages:
        if m["role"] == "system":
            prompt += f"<s>[INST] <<SYS>>\n{m['content']}\n<</SYS>>\n"
        elif m["role"] == "user":
            prompt += f"{m['content']} [/INST] "
        elif m["role"] == "assistant":
            prompt += f"{m['content']} </s><s>[INST] "
    return prompt

def generate_response(history, user_message):
    prompt = format_prompt(history, user_message)
    out = pipe(
        prompt,
        eos_token_id=tokenizer.eos_token_id
    )
    reply = out[0]["generated_text"][len(prompt):]
    return reply.strip()

# ------------------------------
# Streamlit Chat UI
# ------------------------------
st.title("🦙 LLaMA-2 7B Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
if prompt := st.chat_input("Type a message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    reply = generate_response(
        [(m["role"], m["content"]) for m in st.session_state.messages if m["role"] in ["user","assistant"]],
        prompt
    )
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)
