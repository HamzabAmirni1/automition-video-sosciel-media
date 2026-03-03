import os
import sys
import json
import srt_equalizer

from termcolor import colored

ROOT_DIR = os.path.dirname(sys.path[0])

def assert_folder_structure() -> None:
    """
    Make sure that the nessecary folder structure is present.

    Returns:
        None
    """
    # Create the .mp folder
    if not os.path.exists(os.path.join(ROOT_DIR, ".mp")):
        if get_verbose():
            print(colored(f"=> Creating .mp folder at {os.path.join(ROOT_DIR, '.mp')}", "green"))
        os.makedirs(os.path.join(ROOT_DIR, ".mp"))

def get_first_time_running() -> bool:
    """
    Checks if the program is running for the first time by checking if .mp folder exists.

    Returns:
        exists (bool): True if the program is running for the first time, False otherwise
    """
    return not os.path.exists(os.path.join(ROOT_DIR, ".mp"))

def get_config_value(key: str, default: any = None) -> any:
    """
    Helper function to get a configuration value, prioritizing environment variables.
    """
    env_key = key.upper()
    if env_key in os.environ:
        val = os.environ[env_key]
        if isinstance(default, bool):
            return val.lower() in ("true", "1", "yes")
        if isinstance(default, int):
            try: return int(val)
            except: return default
        return val

    config_path = os.path.join(ROOT_DIR, "config.json")
    if not os.path.exists(config_path):
        return default
        
    try:
        with open(config_path, "r") as file:
            config = json.load(file)
            return config.get(key, default)
    except Exception:
        return default

def get_email_credentials() -> dict:
    return get_config_value("email", {"smtp_server": "smtp.gmail.com", "smtp_port": 587, "username": "", "password": ""})

def get_verbose() -> bool:
    return get_config_value("verbose", True)

def get_firefox_profile_path() -> str:
    return get_config_value("firefox_profile", "")

def get_headless() -> bool:
    return get_config_value("headless", True) # Default to True for servers

def get_ollama_base_url() -> str:
    return get_config_value("ollama_base_url", "http://127.0.0.1:11434")

def get_ollama_model() -> str:
    return get_config_value("ollama_model", "")

def get_twitter_language() -> str:
    return get_config_value("twitter_language", "English")

def get_nanobanana2_api_base_url() -> str:
    return get_config_value("nanobanana2_api_base_url", "https://generativelanguage.googleapis.com/v1beta")

def get_nanobanana2_api_key() -> str:
    return get_config_value("nanobanana2_api_key", "") or os.environ.get("GEMINI_API_KEY", "")

def get_nanobanana2_model() -> str:
    return get_config_value("nanobanana2_model", "gemini-3.1-flash-image-preview")

def get_nanobanana2_aspect_ratio() -> str:
    return get_config_value("nanobanana2_aspect_ratio", "9:16")

def get_threads() -> int:
    return get_config_value("threads", 2)
    
def get_zip_url() -> str:
    return get_config_value("zip_url", "")

def get_is_for_kids() -> bool:
    return get_config_value("is_for_kids", False)

def get_google_maps_scraper_zip_url() -> str:
    return get_config_value("google_maps_scraper", "https://github.com/gosom/google-maps-scraper/archive/refs/tags/v0.9.7.zip")

def get_google_maps_scraper_niche() -> str:
    return get_config_value("google_maps_scraper_niche", "")

def get_scraper_timeout() -> int:
    return get_config_value("scraper_timeout", 300)

def get_outreach_message_subject() -> str:
    return get_config_value("outreach_message_subject", "I have a question...")
    
def get_outreach_message_body_file() -> str:
    return get_config_value("outreach_message_body_file", "outreach_message.html")

def get_tts_voice() -> str:
    return get_config_value("tts_voice", "Jasper")

def get_assemblyai_api_key() -> str:
    return get_config_value("assembly_ai_api_key", "")

def get_stt_provider() -> str:
    return get_config_value("stt_provider", "local_whisper")

def get_whisper_model() -> str:
    return get_config_value("whisper_model", "base")

def get_whisper_device() -> str:
    return get_config_value("whisper_device", "auto")

def get_whisper_compute_type() -> str:
    return get_config_value("whisper_compute_type", "int8")
    
def equalize_subtitles(srt_path: str, max_chars: int = 10) -> None:
    srt_equalizer.equalize_srt_file(srt_path, srt_path, max_chars)
    
def get_font() -> str:
    return get_config_value("font", "bold_font.ttf")

def get_fonts_dir() -> str:
    return os.path.join(ROOT_DIR, "fonts")

def get_imagemagick_path() -> str:
    # On linux (Koyeb), simply 'convert' usually works or it's in /usr/bin/convert
    default_path = "magick" if sys.platform == "win32" else "/usr/bin/convert"
    return get_config_value("imagemagick_path", default_path)

def get_script_sentence_length() -> int:
    return get_config_value("script_sentence_length", 4)

