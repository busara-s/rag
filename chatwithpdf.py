import streamlit as st
import fitz
from langchain.chat_models import ChatOllama
from langchain.schema import HumanMessage, SystemMessage, AIMessage

st.title("🦜🔗 Chat with PDF")
st.write("llama3.2:1b")

# Initialize the Ollama chat model
chat_model = ChatOllama(model="llama3.2:1b")  # Replace with your actual model

# Upload file
uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

def extract_text_from_pdf(uploaded_file):
    """Extract text from an uploaded PDF file."""
    pdf_text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            pdf_text += page.get_text("text") + "\n"
    return pdf_text

pdf_text = ""
if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        SystemMessage(content="You are a helpful assistant.")  # System-level instruction 
    ]
    

# Function to send a new user query and update conversation history
def chat_with_llm(user_query):
    # Append user's question
    st.session_state.conversation_history.append(HumanMessage(content=user_query))

    # Add PDF content as context (only once)
    if pdf_text and not any(isinstance(msg, SystemMessage) and "Use the following document" in msg.content for msg in st.session_state.conversation_history):
        st.session_state.conversation_history.insert(1, SystemMessage(content=f"Use the following document content as context:\n{pdf_text}"))  # Limit for efficiency

    # Get response from the LLM
    response = chat_model.invoke(st.session_state.conversation_history)

    # Append AI response to conversation history
    st.session_state.conversation_history.append(AIMessage(content=response.content))

    return response.content

# Streamlit UI
with st.form("my_form"):
    #text = st.text_area("Ask a question about the PDF:", pdf_text if pdf_text else "Enter your query")
    user_input = st.text_area("Ask a question about the PDF:", "Brief for what the content of this pdf. ")
    submitted = st.form_submit_button("Submit")

    if submitted:
        response = chat_with_llm(user_input)
        st.info(response)

# Display chat history
st.subheader("Chat History")
for msg in st.session_state.conversation_history[1:]:  # Skip system message
    role = "🧑 User" if isinstance(msg, HumanMessage) else "🤖 AI"
    st.write(f"{role}: {msg.content}")
    
