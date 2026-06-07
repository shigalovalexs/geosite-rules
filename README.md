# 🛠️ Автоматический сборщик правил для sing-box

Этот репозиторий автоматически раз в сутки (в 00:00 UTC) собирает актуальные правила маршрутизации из внешних источников, очищает их от дубликатов, распределяет по целевым маршрутам и компилирует в бинарный формат `.srs` для sing-box.

## 🔀 Как это работает

Скрипт распределяет правила на **две независимые группы**, что позволяет гибко настраивать маршрутизацию через разные прокси-серверы:

* **Прокси A (`proxy_a_rules`)** — базовые сервисы, поисковые системы и облачная инфраструктура (Google, Cloudflare, AWS, Telegram и др.).
* **Прокси B (`proxy_b_rules`)** — социальные сети, видеохостинги и нейросети (YouTube, OpenAI, Anthropic, Instagram, X/Twitter и др.).

---

## 📦 Что генерируется на выходе

После каждого запуска в репозитории обновляются следующие файлы:

| Группа | Текстовый формат (исходник) | Бинарный формат (для sing-box) |
| :--- | :--- | :--- |
| **Прокси A** | `proxy_a_rules.json` | `proxy_a_rules.srs` |
| **Прокси B** | `proxy_b_rules.json` | `proxy_b_rules.srs` |

---

## ⚙️ Использование в конфиге sing-box

Достаточно подключить сгенерированные `.srs` файлы в блок `route.rule-set` вашего клиента:

```json
{
  "route": {
    "rule-set": [
      {
        "tag": "proxy_a_list",
        "type": "remote",
        "format": "binary",
        "url": "https://raw.githubusercontent.com/shigalovalexs/geosite-rules/main/proxy_a_rules.srs",
        "download_detour": "direct"
      },
      {
        "tag": "proxy_b_list",
        "type": "remote",
        "format": "binary",
        "url": "https://raw.githubusercontent.com/shigalovalexs/geosite-rules/main/proxy_b_rules.srs",
        "download_detour": "direct"
      }
    ],
    "rules": [
      { "rule_set": "proxy_a_list", "outbound": "proxy-a" },
      { "rule_set": "proxy_b_list", "outbound": "proxy-b" }
    ]
  }
}
