# core/locales/translations.py

import json
import os

_loaded_translations = {}

def _load_translations_from_json():
    global _loaded_translations
    locales_dir = os.path.dirname(__file__)
    for filename in os.listdir(locales_dir):
        if filename.endswith('.json'):
            lang_code = filename.split('.')[0]
            file_path = os.path.join(locales_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    _loaded_translations[lang_code] = json.load(f)
                print(f"Successfully loaded {filename}")
            except FileNotFoundError:
                print(f"Translation file not found: {file_path}")
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file: {file_path}")

# Load translations when the module is imported
_load_translations_from_json()


def get_text(key: str, lang_code: str = 'ru'):
    """
    Returns the translated text for a given key and language code.
    Defaults to Russian if the key or language is not found.
    """
    # Fallback to 'ru' if lang_code is None or not in _loaded_translations
    if lang_code not in _loaded_translations:
        lang_code = 'ru'

    # Fallback to the key itself if not found in the specific language or in 'ru'
    default_lang_dict = _loaded_translations.get('ru', {})
    lang_dict = _loaded_translations.get(lang_code, {})

    return lang_dict.get(key, default_lang_dict.get(key, f"<{key}>"))

def get_db_text(json_text: dict, lang_code: str = 'ru'):
    """
    Returns the translated text from a JSON object based on the language code.
    Falls back to 'ru' or the first available language if the specified lang_code is not found.
    """
    if not isinstance(json_text, dict):
        return str(json_text) # Return the text as is if it's not a dict

    if lang_code in json_text:
        return json_text[lang_code]

    # Fallback logic
    if 'ru' in json_text:
        return json_text['ru']
    if 'en' in json_text:
        return json_text['en']

    # If no preferred languages are found, return the first value
    for key in json_text:
        return json_text[key]

    return "[no name]"""