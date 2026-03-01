# ESM Systems Demo

A small, editable demo environment for exploring ESM-style turns: signals → features → policy decision.

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

Open http://localhost:8000
```

### Codespaces

Click **Code → Codespaces → Create codespace on main.**

(Once it’s on GitHub, the green “Code” button is the UX.)

---

# Human testing instructions (pass/fail)

### Test A — Boot
1. `pip install -r requirements.txt`
2. `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
3. Visit `http://localhost:8000`

**PASS**: you see “ESM Systems Demo”, an era tag, a risk number, and events listed.  
**FAIL**: import error, template error, or blank page.

### Test B — Teacher edit loop
1. Open `config/signals.yml`
2. Change `threat_level` weight from `1.0` → `2.0`
3. Refresh page

**PASS**: risk number increases (or changes noticeably).  
**FAIL**: risk unchanged, or YAML parsing error.

### Test C — New era creation
1. Copy folder: `examples/eras/ww2_1941_1945` → `examples/eras/my_era`
2. Edit `metadata.yml` title
3. Open: `http://localhost:8000/?era=my_era`

**PASS**: title updates + events render  
**FAIL**: 404 / file-not-found

---

## What I need from you (one small thing)
When you create the GitHub repo, tell me the repo name (or paste it), and I’ll give you the exact “first landing copy” you can put on the home page later **plus** a simple “Add your own era” teacher guide in plain language.

If you want, next we can add:
- a “download this era pack” link
- a tiny form UI to edit weights without touching YAML  
…but this MVP is enough to prove the concept fast.
