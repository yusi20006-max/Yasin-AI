# FeedBridge

FeedBridge is a self-contained content bridge for Telegram. It embeds its own Telegram fetcher (a vendored Go component, ported from OpenFeed's proven `telemirror` engine — Google Translate domain fronting + uTLS to bypass filtering), processes the content, optionally improves it using AI, and publishes it to Eitaa. No separate OpenFeed instance is required at runtime.

## Features

- Persistent Channel Manager
- SQLite Database
- Queue System
- Duplicate Detection
- AI Processing
- Dashboard
- Plugin Architecture
- Health Monitor
- Logging

## Architecture

Vendored Fetcher (Go, embedded — Telegram via Google Translate fronting + uTLS)

↓ internal call (subprocess or Go↔Python bridge)

Fetch Engine

↓

Duplicate Detector

↓

AI Engine

↓

Queue Manager

↓

Publish Engine

↓

Eitaa

## Requirements

Python 3.14+

Go 1.22+ (for the vendored fetcher component, built as part of the repo — not a separate service)

SQLite

## Building the vendored fetcher

```bash
cd fetcher
# اگر دانلود ماژول‌ها با خطای پراکسی گو مواجه شد:
export GOPROXY=https://goproxy.cn,direct
export GOSUMDB=off
go mod tidy
go build -o fetch ./cmd/fetch
```

Fetch Engine invokes `fetcher/fetch <channel_username>` as a subprocess and reads its JSON stdout.

## Roadmap

See ROADMAP.md

## License

MIT
