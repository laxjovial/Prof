from together import Together
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()
secret_key = os.getenv("api_key")
client = Together(api_key=secret_key)
# Define your prompt
text = "Machine learning is a field of artificial intelligence that enables computers to learn from data and make prediction."
prompt = f"""Explain the key concepts of the text delimited by triple backticks in simple terms. ```{text}```"""
system_prompt = f"""You should explain everything machine learning, emmerging technologies, improvements and limitations and ongoing research addressed at solving these limitations"""
# Add your prompt to your end-point
response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    messages=[
      {
        "role": "user",
        "content": prompt
      },
      {
        "role": "system",
        "content": system_prompt
      },
      {
        "role": "assistant",
        "content": "You are a data science specialist"
      }
    ]
)
print(response.choices[0].message.content)
