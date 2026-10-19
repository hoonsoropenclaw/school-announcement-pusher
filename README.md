# 校園公告抓取與去重推送腳本

每日抓取三個高中官網公告，去重後推送到 Telegram。

## 模組
- `fetcher/` 三個 adapter（Playwright/JSON/RSS）+ demo fallback
  - 每個 adapter 內建 `RateLimiter` semaphore，保護單一學校不被瞬間打爆
- `deduper/` SQLite URL + sha256(title|date|body)
- `notifier/` Telegram sendMessage，dry-run fallback
- `scheduler/` fcntl 檔案鎖 / Redis SET NX EX + heartbeat URL + Sentry

## 環境變數
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- `HEARTBEAT_URL` (e.g. Healthchecks.io)
- `SENTRY_DSN`
- `LOCK_REDIS_URL`：設置時改用分散式 Redis 鎖，否則落回 `flock`

## 跑法
```
pip install -r requirements.txt
python run.py --db data/announcements.sqlite --dry-run
pytest -q
ruff check fetcher deduper notifier scheduler tests
mypy fetcher deduper notifier scheduler
```

## Cron 範例
```
*/30 * * * * cd /srv/announcement && python run.py
```

## CI
GitHub Actions：ruff → mypy → pytest（見 `.github/workflows/ci.yml`）。
