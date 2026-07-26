# FeedBridge Architecture

Version: 0.7

## Core Modules

Configuration

Scheduler

Database

Channel Manager

Fetch Engine

Duplicate Detector

Queue Manager

Publish Engine

Dashboard

AI Engine

Health Monitor

Plugin Manager

## Data Flow

Vendored Fetcher (embedded Go component — Telegram via Google Translate domain fronting + uTLS)

↓ internal call (subprocess, or compiled to a local binary invoked by Fetch Engine)

Fetch Engine

↓

Duplicate Detector

↓

AI Engine

↓

Queue

↓

Publisher

↓

Eitaa

## Vendored Fetcher Component

FeedBridge is one project — it does not depend on a separately running
OpenFeed instance. The core Telegram-fetching logic from OpenFeed
(the `telemirror` and `provider` packages: domain fronting via Google
Translate + TLS fingerprint spoofing via uTLS) is vendored directly
into this repository (e.g. under `/fetcher`), built as part of the
FeedBridge build/deploy process, and invoked internally by Fetch
Engine. OpenFeed's PWA and its own HTTP API layer are not needed here
and are not carried over — only the fetch/bypass logic is reused.
This avoids re-solving filtering circumvention from scratch in
Python while keeping FeedBridge fully self-contained.

## Future

REST API

Web Dashboard

Plugin Marketplace

Distributed Workers
