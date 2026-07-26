پروژه: yusi20006-max/Feedbridge
Milestone: V 0.7

قبل از هر کاری این فایل‌ها رو از ریشه‌ی ریپازیتوری بخون و کامل رعایت کن:
- ARCHITECTURE.md
- DEVELOPMENT_RULES.md
- DATABASE_SCHEMA.md
- API_SPEC.yaml
- MODULES.yaml

نکته‌ی خیلی مهم و غیرقابل‌مذاکره:
Fetch Engine نباید هیچ‌وقت مکانیزم عبور از فیلترینگ (Domain Fronting با گوگل‌ترنسلیت + جعل TLS) رو از صفر در پایتون پیاده‌سازی کنه. این منطق از قبل به‌صورت کد Go آماده و تست‌شده، داخل پوشه‌ی fetcher/ (زیرپوشه‌های telemirror و provider) وندور شده. کافیه این باینری رو با go build -o fetch ./cmd/fetch بسازی و از پایتون به‌صورت subprocess صداش بزنی (fetcher/fetch <channel_username>)، خروجی JSON رو از stdout بخونی. این بخش نباید بازنویسی یا دستکاری اساسی بشه.

روش کار:
هر Issue باز در Milestone به‌نام V 0.7 رو جدا جدا بردار.
برای هر Issue، دقیقاً یک Pull Request جدا باز کن — کد چند Issue رو با هم قاطی نکن.
هر PR باید build و تست‌های واحد (طبق DEVELOPMENT_RULES.md) رو پاس کنه.
شماره‌ی Issue رو توی توضیحات PR لینک کن (مثلاً Closes #3).
ترتیب اجرا رو طبق phase1 تا phase5 در TASKS.yaml رعایت کن (یعنی اول Issueهای Phase 1 رو تموم کن، بعد برو سراغ Phase 2).

زبان کد و کامنت‌ها: انگلیسی.
