<div align="center">

# YasinAI

**Modular AI Platform** — runtime, agents, memory, security, developer tools, and deployment.

[English](#english) | [فارسی](#فارسی)

</div>

---

<a name="english"></a>
## English

### What is YasinAI?

YasinAI is a modular artificial intelligence ecosystem built to support AI agents, developer extensions, knowledge management, long-term memory, secure execution, application development, and automation — all as independent, composable platforms sitting on top of a shared core runtime.

For the full architecture and vision, see [`MASTER_PLAN.md`](./MASTER_PLAN.md). For technical/module-level detail, see [`ARCHITECTURE.md`](./ARCHITECTURE.md). If you are an AI coding agent (Codex, Jules, Aider, Claude Code, etc.) working on this repo, read [`AGENTS.md`](./AGENTS.md) first.

### Status

Target release: **v1.0.0** — GitHub production release in progress. See [`PROJECT_STATUS.md`](./PROJECT_STATUS.md) for live progress.

### Core Platforms

| Platform | Purpose | Location |
|---|---|---|
| Core Runtime | Module loading, service management, runtime lifecycle | `yasinai/core/` |
| Developer Platform | Agent/Plugin/App SDKs, CLI tools, generator, debugger, profiler | `developer_platform/` |
| Security Platform | Identity, auth, authorization, encryption, monitoring | `security_platform/` |
| Knowledge Platform | Memory, knowledge graph, semantic search, reasoning | `knowledge_platform/` |
| CLI System | Command-line management interface | `yasinai/cli/` |
| Deployment System | Installer, Docker support, packaging, health checks | `yasinai/deployment/` |

### CLI Quick Reference

```
yasin status
yasin agent create
yasin memory search
yasin security check
yasin package build
```

### Development Rules (summary)

- Keep components independent and modular.
- Preserve backward compatibility; don't remove modules without approval.
- Clean, clearly named, documented Python code. Tests required for core features.
- Never commit API keys, passwords, tokens, private credentials, or backup files.

See `MASTER_PLAN.md` for the complete rule set, release process, and roadmap.

### Roadmap

Planned for v2.x: distributed AI network, advanced automation, robotics integration, self-improvement systems, and a broader global AI ecosystem.

### License

MIT

---

<a name="فارسی"></a>
## فارسی

### YasinAI چیست؟

YasinAI یک اکوسیستم هوش مصنوعی ماژولار است که برای پشتیبانی از عامل‌های هوش مصنوعی (AI Agents)، افزونه‌های توسعه‌دهنده، مدیریت دانش، حافظه بلندمدت، اجرای امن، توسعه اپلیکیشن و اتوماسیون ساخته شده است — همه به‌صورت پلتفرم‌های مستقل و ترکیب‌پذیر روی یک هسته اجرایی مشترک.

برای دیدن معماری و چشم‌انداز کامل پروژه، فایل [`MASTER_PLAN.md`](./MASTER_PLAN.md) را ببینید. برای جزئیات فنی و سطح ماژول‌ها، به [`ARCHITECTURE.md`](./ARCHITECTURE.md) مراجعه کنید. اگر یک عامل کدنویسی هوش مصنوعی هستید (Codex، Jules، Aider، Claude Code و غیره) و روی این مخزن کار می‌کنید، ابتدا [`AGENTS.md`](./AGENTS.md) را بخوانید.

### وضعیت پروژه

هدف انتشار: **v1.0.0** — نسخه تولیدی در حال آماده‌سازی برای گیت‌هاب است. برای مشاهده وضعیت لحظه‌ای پیشرفت به [`PROJECT_STATUS.md`](./PROJECT_STATUS.md) مراجعه کنید.

### پلتفرم‌های اصلی

| پلتفرم | هدف | مسیر |
|---|---|---|
| Core Runtime | بارگذاری ماژول‌ها، مدیریت سرویس‌ها، چرخه اجرا | `yasinai/core/` |
| Developer Platform | SDK های Agent/Plugin/App، ابزارهای CLI، Generator، Debugger، Profiler | `developer_platform/` |
| Security Platform | هویت، احراز هویت، مجوزدهی، رمزنگاری، مانیتورینگ | `security_platform/` |
| Knowledge Platform | حافظه، گراف دانش، جستجوی معنایی، استدلال | `knowledge_platform/` |
| CLI System | رابط خط فرمان برای مدیریت سیستم | `yasinai/cli/` |
| Deployment System | نصب‌کننده، پشتیبانی از Docker، بسته‌بندی، بررسی سلامت | `yasinai/deployment/` |

### مرجع سریع دستورات CLI

```
yasin status
yasin agent create
yasin memory search
yasin security check
yasin package build
```

### قوانین توسعه (خلاصه)

- اجزای پروژه باید مستقل و ماژولار بمانند.
- سازگاری با نسخه‌های قبلی حفظ شود؛ بدون تأیید هیچ ماژولی حذف نشود.
- کد پایتون تمیز، با نام‌گذاری واضح و مستندسازی شده. ویژگی‌های اصلی نیازمند تست هستند.
- هرگز کلیدهای API، رمزها، توکن‌ها، اطلاعات محرمانه یا فایل‌های بکاپ commit نشوند.

برای مجموعه کامل قوانین، فرآیند انتشار و نقشه راه، فایل `MASTER_PLAN.md` را ببینید.

### نقشه راه

برنامه‌ریزی‌شده برای نسخه v2.x: شبکه هوش مصنوعی توزیع‌شده، اتوماسیون پیشرفته، یکپارچه‌سازی رباتیک، سیستم‌های خودبهبود‌دهنده، و اکوسیستم جهانی گسترده‌تر هوش مصنوعی.

### مجوز

MIT
