import os
import streamlit as st
from dotenv import load_dotenv
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index import ServiceContext, VectorStoreIndex, SimpleDirectoryReader

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(page_title="App Simplificado", layout="wide")
st.title("App Simplificado")


# Error handling function
def handle_error(error_msg):
    st.error(f"Error: {error_msg}")
    st.stop()


# Initialize Azure OpenAI
try:
    llm = AzureOpenAI(
        model=os.environ.get("AZURE_OPENAI_MODEL", "gpt-35-turbo"),
        deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
        api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2023-07-01-preview"),
    )
except Exception as e:
    handle_error(f"Failed to initialize Azure OpenAI: {str(e)}")


# Main app functionality
def main():
    user_query = st.text_input("Enter your question:")

    if user_query:
        try:
            response = llm.complete(user_query)
            st.write("Response:")
            st.write(response)
        except Exception as e:
            handle_error(f"Failed to get response: {str(e)}")


if __name__ == "__main__":
    main()
