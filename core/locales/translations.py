import json

# Глобальный кэш для загруженных переводов
_translations_cache = {}

def _load_translations(lang):
    if lang not in _translations_cache:
        try:
            with open(f'core/locales/{lang}.json', 'r', encoding='utf-8') as f:
                _translations_cache[lang] = json.load(f)
        except FileNotFoundError:
            # Обработка случая, если файл языка не найден
            _translations_cache[lang] = {}
    return _translations_cache[lang]

def get_text(lang, key, **kwargs):
    translations = _load_translations(lang)
    text = translations.get(key, "")
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text

def get_db_text(lang, key):
    translations = _load_translations(lang)
    return translations.get('db_content', {}).get(key, "")
