import json
import ssl
import subprocess
import urllib.request

# 1. СПИСОК ССЫЛОК НА ГИТХАБ
GITHUB_URLS = [
    "https://raw.githubusercontent.com/shigalovalexs/geosite-rules/refs/heads/main/custom.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geoip/cloudflare.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geoip/fastly.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geoip/google.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geoip/telegram.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geoip/twitter.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/anthropic.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/aws.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/cloudflare.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/fastly.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/google-gemini.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/google.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/instagram.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/openai.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/slack.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/telegram.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/twitter.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/whatsapp.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/xai.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/youtube.json",
]

OUTPUT_JSON = "combined_single_rule.json"
OUTPUT_SRS = "combined_single_rule.srs"

master_rules = {}
ssl_context = ssl._create_unverified_context()

print("Начало загрузки файлов из GitHub...")
for url in GITHUB_URLS:
    url = url.strip()
    if not url:
        continue
    try:
        print(f"Скачиваю: {url} ...")
        with urllib.request.urlopen(url, context=ssl_context) as response:
            html = response.read().decode('utf-8')
            data = json.loads(html)

        if "rules" in data and isinstance(data["rules"], list):
            for rule in data["rules"]:
                for key, value in rule.items():
                    if key not in master_rules:
                        master_rules[key] = []
                    if isinstance(value, list):
                        master_rules[key].extend(value)
                    elif isinstance(value, str):
                        master_rules[key].append(value)
    except Exception as e:
        print(f"Ошибка при обработке ссылки {url}: {e}")

single_rule = {}
for key, values in master_rules.items():
    unique_values = list(dict.fromkeys(values))
    if not unique_values:
        continue
    if len(unique_values) == 1 and key == "domain_keyword":
        single_rule[key] = unique_values[0]
    else:
        single_rule[key] = unique_values

combined_data = {
    "version": 2,
    "rules": [single_rule]
}

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(combined_data, f, indent=2, ensure_ascii=False)
print(f"Текстовый файл сохранен как: {OUTPUT_JSON}")

# 2. АВТОМАТИЧЕСКАЯ КОМПИЛЯЦИЯ В БИНАРНЫЙ ФОРМАТ .SRS
print(f"Компиляция {OUTPUT_JSON} в бинарный формат {OUTPUT_SRS}...")
try:
    result = subprocess.run(
        ["sing-box", "rule-set", "compile", "--output", OUTPUT_SRS, OUTPUT_JSON],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(
            f"Успешно скомпилировано! Бинарный файл сохранен как: {OUTPUT_SRS}")
    else:
        print(f"Ошибка компиляции sing-box: {result.stderr}")
except FileNotFoundError:
    print("Ошибка: Команда 'sing-box' не найдена в системе. Скрипт сохранил только JSON.")
except Exception as e:
    print(f"Произошла ошибка при компиляции: {e}")
