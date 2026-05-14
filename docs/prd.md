# PRD: Eagle Mail Agent — Ollama-Powered Outlook Sorter

## 1. Overview

A local, background-running Python agent that automatically classifies and moves emails in a local Outlook mailbox using a locally-hosted Ollama LLM (llama3). The agent runs continuously via a `.bat` file, polls for new unread emails, and sorts them into predefined folders — without ever deleting any message.

---

## 2. Goals

- Automatically sort incoming and sent emails into predefined Outlook folders based on content
- Run silently in the background via a `.bat` file
- Use a local Ollama model (llama3) for classification — no cloud dependency
- Be fully configurable via `config.json` without touching source code
- Log every action to `log.txt`

## 3. Non-Goals

- Deleting emails (strictly prohibited under any circumstance)
- Marking emails as read
- Replying to, forwarding, or composing emails
- Accessing remote or cloud-only mailboxes
- Retroactive sorting of existing emails on first run

---

## 4. Folder Structure

### Received (Inbox → Received subfolders)

Received emails are placed inside a `Received` parent folder under Inbox (`Inbox/Received/<folder>`).

| Folder | Classification Signals |
|---|---|
| automated mails | "this is an automatic mail", "do not reply", "automated notification" |
| route file | "route file" |
| spam mails | Unsolicited, promotional, no business context |
| perfect store | "Perfect store", "secondaries", "shelf share" |
| stales | "Stales" |

### Sent (Sent Items subfolders)

| Folder | Classification Signals |
|---|---|
| automated mails sent | Mirror of received automated mails |
| route file sent | Mirror of received route file |
| spam mails sent | Mirror of received spam mails |
| perfect store sent | "Perfect store", "Perfect Store", "perfect store", "secondaries", "shelf share", "2POS" |
| stales sent | "Stales", "stales" |

---

## 5. Classification Logic

Classification uses a two-stage pipeline:

**Stage 1 — Keyword scoring (fast path)**
1. Concatenate subject + body (lowercased)
2. For each folder, count how many of its keyword signals appear in the text
3. If one or more folders scored > 0:
   - Pick the folder with the highest keyword count
   - If two folders tie on count, the one listed first in `config.json` wins (priority by order)
   - Move the email immediately — no LLM call
4. If no folder scored > 0 → fall through to Stage 2

**Stage 2 — Ollama LLM (fallback)**
1. Build a structured prompt with the folder list and their signals
2. Send subject + body to the local Ollama model (llama3) via `/api/generate` at **temperature 0** for deterministic output
3. Parse the response in two passes:
   - **Exact match**: response lowercased matches a folder name exactly → move the email
   - **Fuzzy match**: a valid folder name appears as a substring of the response → move the email
4. If neither pass succeeds (ambiguous, "unsure", or unrecognisable output) → leave the email in place

Email always remains **unread** after processing.

### Prompt Strategy

- Provide the model with the list of valid folder names and their keyword signals from `config.json`
- Ask for a single label response only — no explanation, no punctuation
- Folders with no signals are described as catch-all categories
- Temperature is set to 0 so output is deterministic and format-compliant
- Any response that does not contain a valid label after both parse passes is treated as low confidence → skip

---

## 6. Trigger Mechanism

- The `.bat` file launches a Python process that runs continuously in the background
- Agent polls Outlook at a configurable interval (default: 60 seconds)
- On each poll, the agent fetches all **unread** emails not yet processed in the current session
- A processed email ID set is kept in memory to avoid reprocessing within the same session

---

## 7. Project Structure

```
eagle_mail_agent/
├── src/
│   ├── __init__.py
│   ├── classifier.py        # Keyword match + Ollama fallback classifier
│   ├── config_loader.py     # Loads and validates config.json
│   ├── folder_manager.py    # Subfolder lookup and auto-creation
│   ├── logger.py            # Append-mode logger (file + console)
│   ├── outlook_client.py    # Outlook COM interface (read, move emails)
│   └── process.py           # Per-email processing logic (inbox and sent)
├── docs/
│   └── prd.md               # This document
├── main.py                  # Entry point and polling loop
├── config.json              # User-editable settings
├── requirements.txt         # Python dependencies
├── setup.bat                # One-time setup (venv + install)
├── run.bat                  # Windows launcher
└── log.txt                  # Auto-generated at runtime
```

---

## 8. config.json Schema

```json
{
  "ollama": {
    "model": "llama3",
    "endpoint": "http://localhost:11434"
  },
  "polling_interval_seconds": 60,
  "max_body_chars": 2000,
  "folders": {
    "received": {
      "automated mails": ["this is an automatic mail", "do not reply", "automated notification"],
      "route file": ["route file"],
      "spam mails": [],
      "perfect store": ["Perfect store", "secondaries", "shelf share"],
      "stales": ["Stales"]
    },
    "sent": {
      "automated mails sent": ["this is an automatic mail", "do not reply", "automated notification"],
      "route file sent": ["route file"],
      "spam mails sent": [],
      "perfect store sent": ["Perfect store", "secondaries", "shelf share", "2POS", "Perfect Store", "perfect store"],
      "stales sent": ["Stales", "stales"]
    }
  },
  "log_path": "log.txt",
  "fallback_behavior": "leave_in_place"
}
```

---

## 9. Logging Format

Every action is written to `log.txt` in append mode:

```
[2025-05-14 14:32:01] MOVED    | inbox  | From: john@example.com | Subject: Route File Q1 | → route file
[2025-05-14 14:32:02] SKIPPED  | inbox  | From: unknown@x.com    | Subject: Hi            | Reason: low confidence
[2025-05-14 14:32:03] MOVED    | sent   | To: team@example.com   | Subject: Shelf Share   | → perfect store sent
[2025-05-14 14:32:04] ERROR    | Could not connect to Outlook COM interface
```

---

## 10. Safety Constraints

| Rule | Detail |
|---|---|
| No delete | The agent never calls any delete, trash, or remove operation |
| No read marking | Emails remain unread after being moved |
| No compose | The agent never replies, forwards, or creates emails |
| Write scope | The only permitted write operation is moving emails between folders |

---

## 11. Technical Stack

| Component | Technology |
|---|---|
| Language | Python 3.x |
| Outlook Interface | pywin32 (`win32com.client`) |
| LLM | Ollama running locally (llama3) |
| LLM HTTP Client | `requests` library |
| Configuration | JSON (`config.json`) |
| Launcher | Windows `.bat` file |
| Logging | Python `logging` module → `log.txt` |

---

## 12. Decisions

- [x] Agent auto-creates Outlook subfolders if they don't exist
- [x] Single growing `log.txt` (no rotation)
- [x] Sent emails processed on every poll — only new ones not yet seen in the current session (tracked by Entry ID in memory)
