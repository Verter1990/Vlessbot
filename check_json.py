
import json
import os

def check_json_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
        print(f"File {filepath}: JSON is valid.")
    except FileNotFoundError:
        print(f"File {filepath}: Not found.")
    except json.JSONDecodeError as e:
        print(f"File {filepath}: JSON decoding error at line {e.lineno}, column {e.colno}: {e.msg}")
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if e.lineno <= len(lines):
                print("Error context:")
                start_line = max(0, e.lineno - 3)
                end_line = min(len(lines), e.lineno + 2)
                for i in range(start_line, end_line):
                    print(f"{i+1}: {lines[i].rstrip()}")
                print(" " * (e.colno + len(str(e.lineno)) + 1) + "^")
    except Exception as e:
        print(f"File {filepath}: An unexpected error occurred: {e}")

if __name__ == "__main__":
    locales_dir = '/app/core/locales'
    check_json_file(os.path.join(locales_dir, 'ru.json'))
    check_json_file(os.path.join(locales_dir, 'en.json'))
