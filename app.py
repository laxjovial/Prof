import streamlit as st
from together import Together
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Streamlit Page Configuration
st.set_page_config(
    page_title="Configurable LLM Tool",
    page_icon="🤖",
    layout="centered"
)

# --- API Key Setup ---
# It's safer to let the user input the API key or use Streamlit secrets
# For local development, .env is fine. For deployment, consider Streamlit secrets.
# Check if API key is in environment variables (for local .env)
secret_key = os.getenv("api_key")

if not secret_key:
    st.warning("API Key not found in environment variables. Please enter it below or set it in your .env file.")
    secret_key = st.text_input("Enter your Together AI API Key", type="password")

if secret_key:
    client = Together(api_key=secret_key)
else:
    st.error("Please provide a Together AI API Key to proceed.")
    st.stop() # Stop execution if no API key is provided

st.title("💡 Configurable AI Response Generator")
st.markdown("""
Welcome to the Configurable AI Response Generator! This tool allows you to control how the AI processes your input and formats its output.
""")

# --- User Input Section ---

st.header("📝 Your Input")

st.subheader("1. Text to Process")
user_text = st.text_area(
    "Enter the main text you want the AI to work with:",
    "Machine learning is a field of artificial intelligence that enables computers to learn from data and make predictions.",
    height=150,
    help="This is the primary content the AI will analyze or transform. Examples: an article, a paragraph, a list of items."
)

st.subheader("2. AI Instruction (User Prompt)")
user_prompt_instruction = st.text_input(
    "Tell the AI what to do with your text:",
    "Explain the key concepts of the text",
    help="This is your direct instruction to the AI. Examples: 'Summarize', 'Translate to French', 'Extract keywords', 'Explain in simple terms'."
)

st.subheader("3. AI Persona (System Prompt)")
user_system_prompt = st.text_area(
    "Define the AI's role or characteristics:",
    "You are a helpful and concise assistant.",
    height=100,
    help="This guides the AI's overall behavior and style. Examples: 'You are a professional legal expert', 'You are a creative writer', 'You are a polite customer service bot'."
)

st.header("📊 Output Format")
output_format_options = {
    "Structured Paragraph": "and provide the output as a structured paragraph.",
    "Table": "and put the result in a table.",
    "List (Bulleted)": "and format the result as a bulleted list.",
    "JSON Object": "and provide the output as a JSON object, with keys representing concepts and values their explanations."
}

selected_format_name = st.selectbox(
    "Choose how you want the AI's response to be formatted:",
    list(output_format_options.keys()),
    index=0, # Default to Structured Paragraph
    help="Select the desired structure for the AI's response."
)
output_format_instruction = output_format_options[selected_format_name]


# --- Construct the final prompt ---
# The instruction "delimited by triple backticks in simple terms" was hardcoded.
# Let's make it more flexible, perhaps as part of user_prompt_instruction, or an optional toggle.
# For now, I'll include it if the main instruction doesn't already imply simplicity.
# You can refine this part based on how you want the "simple terms" to be handled.
final_user_prompt = f"""{user_prompt_instruction} {output_format_instruction} ```{user_text}```"""
final_system_prompt = user_system_prompt

# --- API Call Section ---
st.header("🚀 Generate Response")

if st.button("Generate AI Response"):
    if not user_text.strip():
        st.warning("Please enter some text to process.")
    elif not user_prompt_instruction.strip():
        st.warning("Please provide instructions for the AI.")
    elif not final_system_prompt.strip():
        st.warning("Please define the AI's persona in the System Prompt.")
    else:
        with st.spinner("Generating AI response..."):
            try:
                response = client.chat.completions.create(
                    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", # Ensure this model is available
                    messages=[
                        {
                            "role": "user",
                            "content": final_user_prompt
                        },
                        {
                            "role": "system",
                            "content": final_system_prompt
                        }
                    ]
                )
                ai_response_content = response.choices[0].message.content

                st.subheader("🎉 AI Response")
                # Attempt to render based on format for better presentation
                if selected_format_name == "JSON Object":
                    try:
                        import json
                        st.json(json.loads(ai_response_content))
                    except json.JSONDecodeError:
                        st.warning("The AI did not return valid JSON, displaying as plain text.")
                        st.code(ai_response_content)
                elif selected_format_name == "Table":
                    # Streamlit doesn't have a direct markdown table renderer that's robust for all cases.
                    # Displaying as markdown will often render tables correctly if the AI formats it well.
                    st.markdown(ai_response_content)
                else:
                    st.write(ai_response_content)

            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.info("Please check your API key and try again. Also ensure the model 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free' is accessible and spelled correctly.")

st.markdown("""
---
**How to Use This Tool:**

1.  **Text to Process:** Enter the main content you want the AI to analyze, summarize, translate, etc.
2.  **AI Instruction (User Prompt):** Tell the AI precisely what task to perform on the text. Be clear and specific!
3.  **AI Persona (System Prompt):** Define the role or characteristics you want the AI to adopt (e.g., 'You are a financial analyst', 'You are a poet'). This influences its tone and style.
4.  **Output Format:** Choose how you want the AI's final response to be structured (paragraph, table, list, or JSON).
5.  **Generate AI Response:** Click the button to get your AI-powered output!

**Note:** Ensure your `Together AI API Key` is set in a `.env` file (e.g., `api_key="your_key_here"`) or entered directly into the input field at the top.
""")
