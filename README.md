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

### Installation & Setup

You can install the YasinAI package locally or use Docker for containerized environments.

#### Local installation:
```bash
# Clone the repository (if not already done)
git clone https://github.com/yusi20006-max/Yasin-AI.git
cd Yasin-AI

# Install dependencies and package in editable mode
pip install -e .
```

#### Docker installation:
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Running Tests

To verify that all modules are working correctly and the platform starts up flawlessly, run the complete `pytest` test suite:

```bash
pytest
```

### CLI Quick Reference

The CLI entrypoint `yasin` is available globally after installation. It supports a global `--json` argument to output results in a structured format.

```bash
# Check general platform/runtime status
yasin status [--json]

# Create a custom AI Agent
yasin agent create [name] --role [role] --description [description] --type [type] [--json]

# Query the semantic memory store
yasin memory search [query] --limit [limit] --threshold [threshold] [--json]

# Run platform security checks and vulnerability scans
yasin security check [--json]

# Build deployment artifacts and packages
yasin package build --output [directory] --version [version] [--json]
```

#### Detailed CLI Commands and Options:

*   **`yasin status`**: Orchestrates the Core Runtime, boots the services and displays environment/runtime diagnostics.
*   **`yasin agent create`**: Scaffolds a new agent using the `AgentSDK`.
    *   `[name]`: Positional argument (defaults to `default_agent`).
    *   `--role`: Role of the agent (e.g. `general`, `security`, `knowledge`; defaults to `general`).
    *   `--description`: Description of the agent's intent (defaults to `A helpful AI agent`).
    *   `--type`: Type of agent (e.g. `standard`, `specialist`; defaults to `standard`).
*   **`yasin memory search`**: Queries semantic retriever in the Knowledge Platform.
    *   `[query]`: Positional search string.
    *   `--limit`: Maximum retrieval count (defaults to `5`).
    *   `--threshold`: Similarity confidence cutoff (defaults to `0.7`).
*   **`yasin security check`**: Performs comprehensive system configuration, file permissions, and cryptographic validation.
*   **`yasin package build`**: Triggers `PackageBuilder` to build deployable artifacts.
    *   `--output`: Target directory (defaults to `dist/`).
    *   `--version`: Target release version (defaults to `1.0.0`).

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

### نصب و راه‌اندازی

شما می‌توانید پکیج YasinAI را به‌صورت محلی نصب کرده یا از Docker برای محیط‌های کانتینری استفاده کنید.

#### نصب محلی:
```bash
# کلون کردن مخزن (در صورتی که قبلاً انجام نشده باشد)
git clone https://github.com/yusi20006-max/Yasin-AI.git
cd Yasin-AI

# نصب وابستگی‌ها و پکیج به صورت قابل ویرایش (Editable Mode)
pip install -e .
```

#### نصب با Docker:
```bash
# ساخت و اجرای کانتینرها با Docker Compose
docker-compose up --build
```

### اجرای تست‌ها

برای اطمینان از عملکرد صحیح تمام ماژول‌ها و اجرای بی‌نقص پلتفرم، کل مجموعه تست‌های `pytest` را اجرا کنید:

```bash
pytest
```

### مرجع سریع دستورات CLI

پس از نصب، ابزار خط فرمان `yasin` به صورت سراسری در دسترس است. این ابزار از فلگ `--json` پشتیبانی می‌کند تا خروجی را با فرمت ساختاریافته ارائه دهد.

```bash
# بررسی وضعیت عمومی پلتفرم و زمان اجرا
yasin status [--json]

# ایجاد یک عامل هوش مصنوعی سفارشی
yasin agent create [name] --role [role] --description [description] --type [type] [--json]

# جستجو در مخزن حافظه معنایی
yasin memory search [query] --limit [limit] --threshold [threshold] [--json]

# اجرای ممیزی امنیتی پلتفرم و بررسی آسیب‌پذیری‌ها
yasin security check [--json]

# ساخت بسته‌ها و محصولات استقرار
yasin package build --output [directory] --version [version] [--json]
```

#### جزئیات دستورات و گزینه‌های خط فرمان:

*   **`yasin status`**: هسته اجرایی را لود و مدیریت کرده و عیب‌یابی‌ها و جزییات وضعیت سیستم را نمایش می‌دهد.
*   **`yasin agent create`**: یک عامل جدید مبتنی بر `AgentSDK` ایجاد می‌کند.
    *   `[name]`: آرگومان موقعیتی نام عامل (به طور پیش‌فرض `default_agent`).
    *   `--role`: نقش عامل (مانند `general`, `security`, `knowledge`؛ پیش‌فرض: `general`).
    *   `--description`: توضیح و ماموریت عامل (پیش‌فرض: `A helpful AI agent`).
    *   `--type`: نوع عامل (مانند `standard`, `specialist`؛ پیش‌فرض: `standard`).
*   **`yasin memory search`**: جستجوی معنایی را در پلتفرم دانش اجرا می‌کند.
    *   `[query]`: متن مورد جستجو.
    *   `--limit`: حداکثر تعداد نتایج (پیش‌فرض: `5`).
    *   `--threshold`: حد آستانه شباهت معنایی (پیش‌فرض: `0.7`).
*   **`yasin security check`**: ممیزی جامع امنیتی، کنترل مجوزها و احراز هویت را بررسی می‌کند.
*   **`yasin package build`**: پکیج استقرار را از طریق `PackageBuilder` آماده می‌سازد.
    *   `--output`: دایرکتوری خروجی (پیش‌فرض: `dist/`).
    *   `--version`: نسخه هدف پکیج (پیش‌فرض: `1.0.0`).

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
