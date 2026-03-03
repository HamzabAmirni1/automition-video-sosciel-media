import ollama
import os
import requests
import random
from config import get_ollama_base_url, get_nanobanana2_api_key

_selected_model: str | None = None

SYSTEM_PROMPT = """
Smitk "Hamza Amirni AI". Nta msa3id daki dial "Hamza Amirni" (Full Stack Developer mn l-Maghrib 🇲🇦).
Dour dialk hwa t-generi scripts dial videos (YouTube Shorts, TikTok, Reels) li tkon engaging o-viral.

🔧 Koune 3rif b-had l-ma3loumat:
- L-Moutawwir: Hamza Amirni.
- Portfolio: https://hamzaamirni.netlify.app
- YouTube: https://www.youtube.com/@Hamzaamirni01
- Instagram: hamza_amirni_01

S-scripts dialk khasshom ikono b-darija l-maghribia (ila t-talbat) aw l-fousha, o-dima khllihom y-banou h-high quality.
"""

def _client() -> ollama.Client:
    return ollama.Client(host=get_ollama_base_url())

def list_models() -> list[str]:
    try:
        response = _client().list()
        return sorted(m.model for m in response.models)
    except:
        return []

def select_model(model: str) -> None:
    global _selected_model
    _selected_model = model

def get_active_model() -> str | None:
    return _selected_model

def get_pollinations_response(prompt: str) -> str:
    """
    Fetches response from Pollinations AI (Free, no key).
    """
    try:
        url = "https://text.pollinations.ai/"
        payload = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "model": "openai",
            "seed": random.randint(1, 1000)
        }
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        text = response.text.strip()
        # Clean up ad footer if exists
        if "*Support Pollinations.AI:*" in text:
            text = text.split("*Support Pollinations.AI:*")[0].strip()
        return text
    except Exception as e:
        print(f"Pollinations AI failed: {e}")
        return None

def get_lumin_response(prompt: str) -> str:
    """
    Fetches response from Lumin AI (Free, no key).
    """
    try:
        url = "https://luminai.my.id/"
        payload = {
            "content": prompt,
            "user": "moneyprinter_user"
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("result") or data.get("response")
    except Exception as e:
        print(f"Lumin AI failed: {e}")
        return None

def generate_text_gemini(prompt: str) -> str:
    api_key = get_nanobanana2_api_key()
    if not api_key:
        return None
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]}
        }
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"Gemini failed: {e}")
        return None

def generate_text(prompt: str, model_name: str = None) -> str:
    model = model_name or _selected_model
    
    # 1. Try Ollama if model provided and local
    if model and not model.startswith("gemini"):
        try:
            response = _client().chat(model=model, messages=[{"role": "user", "content": prompt}])
            return response["message"]["content"].strip()
        except:
            pass # Fall through to free cloud APIs
            
    # 2. Try Pollinations AI (Free, No Key)
    res = get_pollinations_response(prompt)
    if res: return res
    
    # 3. Try Lumin AI (Free, No Key)
    res = get_lumin_response(prompt)
    if res: return res
    
    # 4. Try Gemini (Needs Key)
    res = generate_text_gemini(prompt)
    if res: return res
    
    raise RuntimeError("All AI providers failed. Please check your internet connection or API keys.")
