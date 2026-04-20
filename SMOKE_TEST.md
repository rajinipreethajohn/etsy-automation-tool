# Smoke Test Checklist — Etsy Automation Tool

**Run this before and after each refactor to confirm the golden path still works.**

---

## Prerequisites

- [ ] Ollama running locally (`ollama list` shows `llama3.1:latest`)
- [ ] `google_service_account.json` present in project root
- [ ] Google Sheet "MYB Content Queue" exists and is accessible

---

## Test Run

| # | Check | Expected | Pass | Fail | Notes |
|---|-------|----------|------|------|-------|
| 1 | **App Launch** — `streamlit run app.py` | App opens in browser, no traceback in terminal | ☐ | ☐ | |
| 2 | **Template Apply** — Select a template, click "Apply Template" | Form fields populate (product name, age group, keywords, etc.) | ☐ | ☐ | |
| 3 | **Generate Variants** — Fill form, click "Generate 3 Variants" | Spinner shows, completes in ~30-60s, success message appears | ☐ | ☐ | |
| 4 | **Tabs Render** — 3 tabs appear (SEO Safe, Emotional Parent Hook, Premium Brand Voice) | All 3 tabs clickable, no blank/empty tabs | ☐ | ☐ | |
| 5 | **Etsy Content** — Inside each tab | Title, 13 tags, description all populated (not empty) | ☐ | ☐ | |
| 6 | **Social Content** — Inside each tab | Pinterest title/description, Instagram caption all populated | ☐ | ☐ | |
| 7 | **Tag Validation** — Check tag warnings | No unexpected warnings (or warnings correctly flag long/duplicate tags) | ☐ | ☐ | |
| 8 | **Send to Sheets** — Click "Send 3 Variants to Google Sheet" | Success toast: "Sent 3 variants to MYB Content Queue" | ☐ | ☐ | |
| 9 | **Google Sheets Verify** — Open sheet in browser | 3 new rows with: timestamp, product info, variant names, status = "Draft", two "No" columns | ☐ | ☐ | |
| 10 | **Download Buttons** — Click JSON + TXT download for one variant | Files download, content is valid JSON / readable text | ☐ | ☐ | |
| 11 | **No UI Crashes** — Scan terminal for errors | No Python exceptions, no Streamlit errors | ☐ | ☐ | |

---

## Result

- [ ] **All checks passed** — Safe to proceed with refactor
- [ ] **Failures noted above** — Investigate before continuing

---

**Date Tested:** _______________  
**Tester:** _______________
