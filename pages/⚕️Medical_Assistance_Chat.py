import streamlit as st
from langchain.chains import LLMChain
from langchain.llms import openai
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.prompts import PromptTemplate 
from openai import OpenAI
from functions import *
from pathlib import Path

# set page icon and tab title
st.set_page_config(
        page_title="MedAI- AI Chat",
        page_icon="⚕️",
    )


# Make page content larger (zoom)
st.markdown("""<style>body {zoom: 1.5;  /* Adjust this value as needed */}</style>""", unsafe_allow_html=True)

# check if authenticated is in session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# check if user is authenticated
if not st.session_state['authenticated']:
    authenticate()

# Show page if user is authenticated
if st.session_state['authenticated']:

    #page content start here 

     # Use columns to layout the title and image
    col2, col1 = st.columns([1.5, 2.7])
    with col1:
        st.markdown("## ⚕️ Medical Assistance", unsafe_allow_html=True)
        with st.expander("⚠️ Important Notice on Usage"):
            st.write("""
    **Important Notice on Usage:** This AI-powered chat interface is designed to simulate natural human conversations and provide informative responses across a wide range of topics. However, please be advised that the responses generated by the AI are based on patterns in data and may not always be accurate or reflect the most current information. Users are encouraged to use critical judgment and verify facts independently, especially for important decisions. Remember, the AI does not possess consciousness or understanding; its responses are generated based on training data and algorithms. Enjoy your interaction responsibly.
                
        Powered by OPENAI LLM Models    
                            """)

        # Dropdown menu for model selection
        model_version = st.selectbox("Choose GPT Model", ["Please choose a Model First", "gpt-3.5-turbo", "gpt-4"])
    with col2:
        st.image("nova_image.png", width=250)
                
    # Get API key
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    # Check if key was retrieved 
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
                    

    def clear_session_state_except_password():
        # Make a copy of the session_state keys
        keys = list(st.session_state.keys())
                
        # Iterate over the keys
        for key in keys:
            # If the key is not 'password_correct', delete it from the session_state
            if key != 'authenticated':
                del st.session_state[key]

    # set up memory
    msgs = StreamlitChatMessageHistory(key = "langchain_messages")
    memory = ConversationBufferMemory(chat_memory=msgs)

    # provide an initial message
    if len(msgs.messages) == 0:
        msgs.add_ai_message("Hi! How can I help you?")

    # template for prompt 
    health_template = """ 
    Task: Simulate a conversation with a general GPT assistant designed to help users understand a variety of health symptoms and concerns. The assistant should provide straightforward, empathetic responses that can guide non-medical users in recognizing when it might be appropriate to seek further medical advice.
    Topic: Address general question and a wide range of health symptoms and concerns based on the user's input, offering general advice and information in an accessible manner, if the user does not ask a health related questions, make sure your answer is appropriate to the questions.
    Style: Informative, empathetic, and reassuring, ensuring the information is easy to understand for individuals without medical training.
    Tone: Supportive and friendly
    Audience: Individuals seeking information about health symptoms and concerns, including those with little to no medical knowledge.
    Length: 1-3 paragraphs
    Format: markdown; **include ```GPT Response``` headings**

    Example interaction:

    User: I've been feeling really tired lately, more than usual. Should I be worried?
    GPT:
    ```GPT Response:```
    Feeling unusually tired can be due to a range of factors, including stress, poor sleep, diet, or lifestyle. Sometimes, it can also be a sign of an underlying health issue, especially if it persists or is accompanied by other symptoms. If you're experiencing this fatigue for a prolonged period, or if it's affecting your daily life, it might be a good idea to consult a healthcare professional. They can help determine if there's a specific cause that needs to be addressed. Remember, taking care of your mental and physical health is important, and seeking professional advice is a positive step forward.

    {history}
    User: {human_input}
    GPT: 
    """

    # prompt the llm and send 
    prompt = PromptTemplate(input_variables=["history", "human_input"], template= health_template)
    llm_chain = LLMChain(llm=ChatOpenAI(openai_api_key = OPENAI_API_KEY, model = model_version), prompt=prompt, memory=memory)

    if model_version == "Please choose a Model First":
        st.info("Please choose a model")
    else:

        for msg in msgs.messages:
            st.chat_message(msg.type).write(msg.content)

        if prompt := st.chat_input():
            st.chat_message("user").write(prompt)
            with st.spinner("Generating response..."):
                response = llm_chain.run(prompt)
            st.session_state.last_response = response
            st.chat_message("assistant").write(response)


            # Text to speech setup
            client = OpenAI()
            with st.spinner("Converting response to speech..."):
                try:
                    speech = client.audio.speech.create(
                        model="tts-1",
                        voice="nova",
                        input=remove_first_two_words(response)
                    )
                    binary_content = speech.content
                    # speech_file_path = str(Path("speech.mp3"))
                    autoplay_audio(binary_content)
                    #st.audio(speech_file_path, format="audio/mp3", start_time=0)
                except Exception as e:
                    st.error(f"Failed to convert text to speech: {e} ")
               

                
    # clear chat button
    clear_memory = st.sidebar.button("Clear Chat")
    if clear_memory:
        clear_session_state_except_password()
        st.session_state["last_response"] = "GPT: Hi there, hope you're doing great! How can I help you?"