# This file will contain the configuration for various LLM providers.
# In a real-world scenario, this might be more complex, loading from YAML or another config format.

LLM_PROVIDERS = {
    "TogetherAI": {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "api_key_env": "TOGETHER_API_KEY",
    },
    "OpenAI": {
        "model": "gpt-4-turbo",
        "api_key_env": "OPENAI_API_KEY",
    },
    "Google": {
        "model": "gemini-1.5-pro-latest",
        "api_key_env": "GOOGLE_API_KEY",
    }
    # Anthropic, Hugging Face, etc., could be added here following the same pattern.
}
