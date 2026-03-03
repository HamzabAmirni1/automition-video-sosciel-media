import ollama
import os
import requests
from config import get_ollama_base_url, get_nanobanana2_api_key

_selected_model: str | None = None

def _client() -> ollama.Client:
    return ollama.Client(host=get_ollama_base_url())

def list_models() -> list[str]:
    """
    Lists all models available on the local Ollama server.
    Returns:
        models (list[str]): Sorted list of model names.
    """
    try:
        response = _client().list()
        return sorted(m.model for m in response.models)
    except:
        return []

def select_model(model: str) -> None:
    """
    Sets the model to use for all subsequent generate_text calls.
    Args:
        model (str): An Ollama model name.
    """
    global _selected_model
    _selected_model = model

def get_active_model() -> str | None:
    """
    Returns the currently selected model, or None if none has been selected.
    """
    return _selected_model

def generate_text_gemini(prompt: str) -> str:
    """
    Generates text using Gemini Pro (Flash) API as a fallback.
    """
    api_key = get_nanobanana2_api_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY or nanobanana2_api_key not found. Required for cloud deployment.")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    data = response.json()
    return data['candidates'][0]['content']['parts'][0]['text'].strip()

def generate_text(prompt: str, model_name: str = None) -> str:
    """
    Generates text using the local Ollama server or Gemini API as a cloud fallback.
    """
    model = model_name or _selected_model
    
    # Cloud mode: If no Ollama model selected or Ollama seems unavailable, fallback to Gemini
    if not model or model.startswith("gemini"):
        try:
            return generate_text_gemini(prompt)
        except Exception as e:
            if not model:
                raise RuntimeError(f"Failed to generate text with Gemini fallback: {e}")
    
    # Try Ollama if model provided
    try:
        response = _client().chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response["message"]["content"].strip()
    except Exception as e:
        # Final fallback to Gemini for reliability in cloud environments
        try:
            return generate_text_gemini(prompt)
        except:
            raise e # Raise original Ollama error if Gemini also fails
