# Languages — code ↔ name cheat sheet

The docs use **folder-per-language** i18n (`mkdocs-static-i18n`, `docs_structure: folder`).
English originals live at the `docs/` root. Each translation lives in its own folder
`docs/<code>/…`, mirroring the same tree. Untranslated pages fall back to English
automatically — you only create the pages you actually translate.

**To translate a page:** put the translated file at the same relative path under the
language folder, e.g. translate `docs/All_Guides/GLOSSARY.md` → `docs/ru/All_Guides/GLOSSARY.md`.

Folders are named by the **code** below (mkdocs requires codes, not full names).

| Code | Native name | Language (English) | Folder |
| --- | --- | --- | --- |
| `en` | English | English (source) | `docs/` (root) |
| `zh` | 简体中文 | Chinese (Simplified) | `docs/zh/` |
| `ja` | 日本語 | Japanese | `docs/ja/` |
| `ko` | 한국어 | Korean | `docs/ko/` |
| `vi` | Tiếng Việt | Vietnamese | `docs/vi/` |
| `th` | ไทย | Thai | `docs/th/` |
| `id` | Bahasa Indonesia | Indonesian | `docs/id/` |
| `zh-TW` | 繁體中文 | Chinese (Traditional) | `docs/zh-TW/` |
| `hi` | हिन्दी | Hindi | `docs/hi/` |
| `ar` | العربية | Arabic | `docs/ar/` |
| `ms` | Bahasa Melayu | Malay | `docs/ms/` |
| `tl` | Filipino | Filipino / Tagalog | `docs/tl/` |
| `tr` | Türkçe | Turkish | `docs/tr/` |
| `fa` | فارسی | Persian (Farsi) | `docs/fa/` |
| `ur` | اردو | Urdu | `docs/ur/` |
| `bn` | বাংলা | Bengali | `docs/bn/` |
| `ta` | தமிழ் | Tamil | `docs/ta/` |
| `my` | မြန်မာ | Burmese | `docs/my/` |
| `km` | ខ្មែរ | Khmer | `docs/km/` |
| `lo` | ລາວ | Lao | `docs/lo/` |
| `he` | עברית | Hebrew | `docs/he/` |
| `es` | Español | Spanish | `docs/es/` |
| `pt-BR` | Português (Brasil) | Portuguese (Brazil) | `docs/pt-BR/` |
| `ru` | Русский | Russian | `docs/ru/` |
| `fr` | Français | French | `docs/fr/` |
| `de` | Deutsch | German | `docs/de/` |
| `it` | Italiano | Italian | `docs/it/` |
| `pl` | Polski | Polish | `docs/pl/` |

**On-demand setup:** this repo does not pre-copy English into every language folder
(that would be ~4,300 stale files). When you want to start a language/section, ask and
the English copies for that section are dropped into `docs/<code>/…` ready to translate;
everything else keeps falling back to English until translated.
