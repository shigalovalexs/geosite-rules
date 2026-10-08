import json
import ssl
import subprocess
import urllib.request

URLS = [
    "https://docs.google.com/spreadsheets/d/1J5RLblcEolS1_c5wjpV0D9AXoMS-zv5fhdtMXSilMjY/export?format=tsv&gid=1143023545",
    "https://docs.google.com/spreadsheets/d/1J5RLblcEolS1_c5wjpV0D9AXoMS-zv5fhdtMXSilMjY/export?format=tsv&gid=712038739",
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
            req = urllib.request.Request(url, headers={"User-Agent": "User-Agent: curl/7.54.1"})
            with urllib.request.urlopen(req, context=ssl_context, timeout=30) as response:
                html = response.read().decode("utf-8")
                data = json.loads(text)

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

    combined_data = {"version": 2, "rules": [single_rule]}

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
            text=True,
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

    print("\n=== НАЧАЛО ОБРАБОТКИ ===")
    rules = process_urls(URLS, ssl_context)
    save_and_compile(rules, "proxy_rules.json", "proxy_rules.srs")

    print("\n=== ВСЕ ПРОЦЕССЫ ЗАВЕРШЕНЫ ===")


if __name__ == "__main__":
    main()
