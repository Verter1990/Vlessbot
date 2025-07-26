# core/locales/translations.py

import json
import os
from loguru import logger

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
    logger.debug(f"get_text called with key: '{key}', lang_code: '{lang_code}'")

    # Fallback to 'ru' if lang_code is None or not in _loaded_translations
    effective_lang_code = lang_code
    if not lang_code or lang_code not in _loaded_translations:
        logger.warning(f"lang_code '{lang_code}' not found or invalid. Falling back to 'ru'.")
        effective_lang_code = 'ru'

    lang_dict = _loaded_translations.get(effective_lang_code, {})
    text = lang_dict.get(key)

    if text:
        logger.debug(f"Found key '{key}' in '{effective_lang_code}'.")
        return text
    else:
        logger.warning(f"Key '{key}' not found for lang_code '{effective_lang_code}'. Trying 'ru' fallback.")
        default_lang_dict = _loaded_translations.get('ru', {})
        return default_lang_dict.get(key, f"<{key}>")

def get_db_text(json_data: dict, lang_code: str = 'ru'):
    """
    Extracts text from a JSON object based on the language code.
    Falls back to 'ru' or the first available language.
    """
    if not isinstance(json_data, dict):
        return str(json_data) # Return as is if it's not a dict

    # Try to get the text for the requested language
    text = json_data.get(lang_code)
    if text:
        return text

    # Fallback to Russian
    text = json_data.get('ru')
    if text:
        return text

    # Fallback to English
    text = json_data.get('en')
    if text:
        return text

    # Fallback to the first value in the dictionary
    if json_data:
        return next(iter(json_data.values()))

    # If all else fails, return a placeholder
    return "<no_translation>"