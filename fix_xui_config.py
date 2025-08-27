import json

config_path = "/usr/local/x-ui/bin/config.json"

try:
    with open(config_path, "r") as f:
        config = json.load(f)

    # Фильтруем инбаунды, оставляя только те, у которых security == "reality"
    original_inbounds = config.get("inbounds", [])
    inbounds_to_keep = []
    removed_count = 0

    for inbound in original_inbounds:
        stream_settings = inbound.get("streamSettings")
        if inbound.get("streamSettings") and inbound["streamSettings"].get("security") == "reality"
            removed_count += 1
        else:
            inbounds_to_keep.append(inbound)

    config["inbounds"] = inbounds_to_keep

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"Конфигурация исправлена. Удалено {removed_count} инбаундов с REALITY.")

except Exception as e:
    print(f"Произошла ошибка: {e}")