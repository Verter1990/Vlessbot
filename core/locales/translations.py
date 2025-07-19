import json
from loguru import logger

# Глобальный кэш для загруженных переводов
_translations_cache = {}

def _load_translations(lang):
    if lang not in _translations_cache:
        logger.info(f"Attempting to load translations for language: {lang}")
        try:
            with open(f'core/locales/{lang}.json', 'r', encoding='utf-8') as f:
                _translations_cache[lang] = json.load(f)
                logger.info(f"Successfully loaded translations for {lang}. Keys loaded: {len(_translations_cache[lang])}")
        except FileNotFoundError:
            logger.warning(f"Translation file not found for language: {lang}. Using empty translations.")
            _translations_cache[lang] = {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON for language {lang}: {e}. Using empty translations.")
            _translations_cache[lang] = {}
    return _translations_cache[lang]

def get_text(key, lang, **kwargs):
    translations = _load_translations(lang)
    text = translations.get(key, "")
    if not text:
        logger.warning(f"Missing translation for key '{key}' in language '{lang}'.")
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception as e:
            logger.error(f"Error formatting text for key '{key}' in language '{lang}': {e}. Text: '{text}'")
            return text
    return text

def get_db_text(key_or_dict, lang):
    if isinstance(key_or_dict, dict):
        return key_or_dict.get(lang, key_or_dict.get('en', ''))
    else:
        translations = _load_translations(lang)
        db_content = translations.get('db_content', {})
        text = db_content.get(key_or_dict, "")
        if not text:
            logger.warning(f"Missing db_content translation for key '{key_or_dict}' in language '{lang}'.")
        return text