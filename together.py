from together import Together
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
secret_key = os.getenv("api_key")
client = Together(api_key=secret_key)

# --- User Configuration Section ---
user_text = input("Please enter the text you want explained: ")
user_prompt_instruction = input("Please enter the main instruction for the AI (e.g., 'Explain the key concepts'): ")
user_system_prompt = input("Please enter the system prompt/AI's persona (e.g., 'You are a helpful assistant'): ")

print("\nSelect desired output format:")
print("1. Table")
print("2. List")
print("3. JSON")
print("4. Structured Paragraph")
format_choice = input("Enter the number corresponding to your choice: ")

output_format_instruction = ""
if format_choice == '1':
    output_format_instruction = "and put the result in a table."
elif format_choice == '2':
    output_format_instruction = "and format the result as a bulleted list."
elif format_choice == '3':
    output_format_instruction = "and provide the output as a JSON object, with keys representing concepts and values their explanations."
elif format_choice == '4':
    output_format_instruction = "and provide the output as a structured paragraph."
else:
    print("Invalid format choice. Defaulting to structured paragraph.")
    output_format_instruction = "and provide the output as a structured paragraph."

# --- Construct the final prompt ---
prompt = f"""{user_prompt_instruction} delimited by triple backticks in simple terms {output_format_instruction} ```{user_text}```"""
system_prompt = user_system_prompt # The user-defined system prompt

# --- API Call Section ---
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
        # You might not always need an assistant role message unless it's for few-shot learning or specific context setting
        # {
        #   "role": "assistant",
        #   "content": "You are a data science specialist"
        # }
    ]
)
print("\n--- AI Response ---")
print(response.choices[0].message.content)
