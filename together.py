from together import Together
from dotenv import load_dotenv
import os
#load environment variables from .env file
#load_dotenv()
#secret_key =os.gotenv("api_key")
client = Together(api_key="c56046f8febede7b8c4fd1c94e6d8183437e8ab7c5048fc59ca4bbd9a2e79f60") # auth defaults to os.environ.get()
#define your prompt
text = "Machine learning is a field of artificial intelligence that enables computers to learn from data and make predictions"
prompt = f"""Explain the key concepts of the text delimmited by triple backticks in simple terms. ```{text}```"""
#add your prompt to an endpoint
response = client.chat.completions.create(
    model="Qwen/Qwen3-235B-A22B-Thinking-2507",
    messages=[
      {
        "role": "user",
        "content": prompt
      }
    ]
)
print(response.choices[0].message.content)
#Client = Together(api_key="c56046f8febede7b8c4fd1c94e6d8183437e8ab7c5048fc59ca4bbd9a2e79f60") # auth defaults to os.environ.get()
#print(prompt)
