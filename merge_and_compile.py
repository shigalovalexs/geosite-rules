import json
import ssl
import subprocess
import urllib.request

# 1. РАЗДЕЛЬНЫЕ СПИСКИ ССЫЛОК НА ГИТХАБ

# Список для Прокси A
URLS_PROXY_A = [
    "https://raw.githubusercontent.com/shigalovalexs/geosite-rules/refs/heads/main/proxy_a_custom_rules.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo-lite/geosite/applemusic.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geoip/cloudflare.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/anthropic.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/aws.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/cloudflare.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/openai.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/protonmail.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/spotify.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/xai.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/youtube.json",
]

# Список для Прокси B
URLS_PROXY_B = [
    "https://raw.githubusercontent.com/shigalovalexs/geosite-rules/refs/heads/main/proxy_b_custom_rules.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geoip/facebook.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geoip/fastly.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geoip/google.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geoip/telegram.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geoip/twitter.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/adobe.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/atlassian.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/discord.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/facebook.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/fastly.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/github.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/google-gemini.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/google.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/instagram.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/linkedin.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/meta.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/slack.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/telegram.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/twitter.json",
    "https://raw.githubusercontent.com/MetaCubeX/meta-rules-dat/refs/heads/sing/geo/geosite/whatsapp.json",
]

def process_urls(urls, ssl_context):
    """Скачивает JSON по ссылкам и объединяет их правила."""
    master_rules = {}
    for url in urls:
        url = url.strip()
        if not url:
            continue
        try:
            print(f"  Скачиваю: {url} ...")
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
            print(f"  [Ошибка] при обработке ссылки {url}: {e}")
    return master_rules


def save_and_compile(master_rules, output_json, output_srs):
    """Формирует финальный JSON и компилирует его в .srs через sing-box."""
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

    # Сохраняем JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, indent=2, ensure_ascii=False)
    print(f"  Текстовый файл сохранен как: {output_json}")

    # Компиляция в SRS
    print(f"  Компиляция в бинарный формат {output_srs}...")
    try:
        result = subprocess.run(
            ["sing-box", "rule-set", "compile", "--output", output_srs, output_json],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"  [Успех] Бинарный файл сохранен как: {output_srs}")
        else:
            print(f"  [Ошибка sing-box]: {result.stderr}")
    except FileNotFoundError:
        print("  [Предупреждение]: Команда 'sing-box' не найдена. Создан только JSON.")
    except Exception as e:
        print(f"  [Ошибка] при компиляции: {e}")


def main():
    ssl_context = ssl._create_unverified_context()

    # --- Обработка ПРОКСИ А ---
    print("\n=== НАЧАЛО ОБРАБОТКИ: ПРОКСИ А ===")
    rules_a = process_urls(URLS_PROXY_A, ssl_context)
    save_and_compile(rules_a, "proxy_a_rules.json", "proxy_a_rules.srs")

    # --- Обработка ПРОКСИ Б ---
    print("\n=== НАЧАЛО ОБРАБОТКИ: ПРОКСИ B ===")
    rules_b = process_urls(URLS_PROXY_B, ssl_context)
    save_and_compile(rules_b, "proxy_b_rules.json", "proxy_b_rules.srs")

    print("\n=== ВСЕ ПРОЦЕССЫ ЗАВЕРШЕНЫ ===")


if __name__ == "__main__":
    main()
