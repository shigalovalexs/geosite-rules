# 🛠️ Автоматический сборщик правил для sing-box

Этот репозиторий автоматически раз в сутки (в 00:00 UTC) собирает актуальные правила маршрутизации из внешних источников, очищает их от дубликатов и компилирует в бинарный формат `.srs` для sing-box.

## 📦 Что генерируется на выходе

После каждого запуска в репозитории обновляются следующие файлы:

| Текстовый формат (исходник) | Бинарный формат (для sing-box) |
| :--- | :--- |
| `proxy_rules.json` | `proxy_rules.srs` |

## ⚙️ Использование в конфиге sing-box

Достаточно подключить сгенерированные `.srs` файлы в блок `route.rule_set` вашего клиента:

```json
{
  "route": {
    "rule_set": [
      {
        "tag": "proxy_rules",
        "type": "remote",
        "format": "binary",
        "url": "https://raw.githubusercontent.com/shigalovalexs/geosite-rules/main/proxy_rules.srs",
        "download_detour": "direct"
      }
    ],
    "rules": [
      { "rule_set": "proxy_rules", "outbound": "proxy" }
    ]
  }
}
