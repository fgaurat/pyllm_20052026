import streamlit as st
from ollama import chat
import time
from ollama import ChatResponse

@st.cache_data
def longfunction():
    time.sleep(5)

def main():
    st.write("Hello, *World!* :sunglasses:")

    # st.button("Reset", type="primary")
    # if st.button("Say hello"):
    #     st.write("Why hello there")
    # else:
    #     st.write("Goodbye")

    # if st.button("Aloha", type="tertiary"):
    #     st.write("Ciao")


    # title = st.text_input("Name ?", "")
    # if title:
    #     st.write("The current movie title is", title)

    st.title("Echo Bot")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []


    # longfunction()
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        response: ChatResponse = chat(model='mistral', messages=st.session_state.messages)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response.message.content})    
        st.markdown(response.message.content)


if __name__=='__main__':
    main()
