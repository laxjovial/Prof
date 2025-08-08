import os
from llm_config import LLM_PROVIDERS

# Import individual LLM clients
from together import Together
import openai
import google.generativeai as genai
from langchain_together import TogetherEmbeddings

# New function to get embedding client for FastAPI startup
def get_embedding_client():
    """Initializes and returns the TogetherEmbeddings client."""
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        raise ValueError("TOGETHER_API_KEY not found in environment variables.")
    return TogetherEmbeddings(model="togethercomputer/m2-bert-80M-8k-retrieval", api_key=api_key)

def get_ai_response(
    provider: str,
    system_prompt: str,
    messages: list,
    vector_store=None,
    use_rag=True
) -> str:
    """
    Generates a response from the specified LLM provider, augmented with RAG context.
    """
    if provider not in LLM_PROVIDERS:
        raise ValueError(f"Unsupported LLM provider: {provider}")

    config = LLM_PROVIDERS[provider]
    api_key = os.getenv(config["api_key_env"])
    if not api_key:
        raise ValueError(f"API key for {provider} not found in environment variables.")

    # 1. Augment prompt with RAG context if applicable
    prompt = messages[-1]['content']
    context = ""
    if vector_store and use_rag:
        docs = vector_store.similarity_search(prompt, k=3)
        context = "\n\n---\n\nContext from uploaded document:\n" + "\n".join([d.page_content for d in docs])

    final_prompt_content = prompt + context

    # Construct the full message history for the API call
    api_messages = messages[:-1] + [{"role": "user", "content": final_prompt_content}]

    # 2. Dispatch to the correct LLM client
    try:
        if provider == "TogetherAI":
            client = Together(api_key=api_key)
            # Prepend system prompt for TogetherAI
            full_api_messages = [{"role": "system", "content": system_prompt}] + api_messages
            response = client.chat.completions.create(
                model=config["model"],
                messages=full_api_messages,
            )
            return response.choices[0].message.content

        elif provider == "OpenAI":
            openai.api_key = api_key
            # Prepend system prompt for OpenAI
            full_api_messages = [{"role": "system", "content": system_prompt}] + api_messages
            response = openai.chat.completions.create(
                model=config["model"],
                messages=full_api_messages,
            )
            return response.choices[0].message.content

        elif provider == "Google":
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name=config["model"],
                system_instruction=system_prompt
            )
            # Google's format is slightly different; it doesn't use the "role" for history in the same way for a simple chat.
            # We'll need to format the history. For simplicity, we'll just send the final prompt.
            # A more robust implementation would handle the conversation history formatting.
            response = model.generate_content(final_prompt_content)
            return response.text

    except Exception as e:
        print(f"Error calling {provider} API: {e}")
        # Return a user-friendly error message
        return f"An error occurred while communicating with the {provider} API. Please check the backend logs."

    return "Error: No response from AI."
