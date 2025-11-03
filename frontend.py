import streamlit as st
from backend import workflow
from langchain_core.messages import HumanMessage

if "messages" not in st.session_state:
    st.session_state["messages"] = []

messages = st.session_state["messages"]

for i in range(len(messages)):
    if messages[i]["role"]=="user":
        with st.chat_message("user"):
            st.text(messages[i]["content"])
    else:
        with st.chat_message("ai"):
            st.text(messages[i]["content"])

user_input = st.chat_input(placeholder="Type here")


if user_input:
    messages.append({"role":"user", "content":user_input})
    with st.chat_message("user"):
        st.text(user_input)
    config = {'configurable': {'thread_id': 1}}
    response = workflow.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
    ai_message = response["messages"][-1].content
    messages.append({"role":"ai", "content":ai_message})
    with st.chat_message("ai"):
        st.text(ai_message)
    



