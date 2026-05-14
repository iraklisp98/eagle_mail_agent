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

### Received (Inbox subfolders)

| Folder | Classification Signals |
|---|---|
| automated mails | "this is an automatic mail", "do not reply", "automated notification" |
| route file | "route file" |
| spam mails | Unsolicited, promotional, no business context |
| perfect store | "Perfect store", "secondaries", "shelf share" |
| other projects | Work-related emails not matching any above category |

### Sent (Sent Items subfolders)

| Folder | Classification Signals |
|---|---|
| automated mails sent | Mirror of received automated mails |
| route file sent | Mirror of received route file |
| spam mails sent | Mirror of received spam mails |
| perfect store sent | Mirror of received perfect store |
| other projects sent | Mirror of received other projects |

---

## 5. Classification Logic

1. Agent fetches unread emails from Inbox and Sent Items
2. For each email, subject + body are passed to Ollama (llama3) via a structured prompt
3. The prompt instructs the model to return exactly one folder label from the valid list
4. If the model output matches a valid label → email is moved to that folder
5. If the model output is ambiguous, empty, or does not match any valid label → email is left in place (no move)
6. Email always remains **unread** after processing

### Prompt Strategy

- Provide the model with the list of valid folder names and their keyword signals from `config.json`
- Ask for a single label response only
- Treat any non-matching output as low confidence → skip

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
├── main.py              # Entry point and polling loop
├── outlook_client.py    # win32com Outlook interface (read emails, move between folders)
├── classifier.py        # Ollama API call and label parsing
├── folder_manager.py    # Folder lookup and validation
├── logger.py            # Append-mode log writer
├── config_loader.py     # Loads and validates config.json
├── config.json          # User-editable settings
├── run.bat              # Windows launcher
├── prd.md               # This document
└── log.txt              # Auto-generated at runtime
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
      "other projects": []
    },
    "sent": {
      "automated mails sent": ["this is an automatic mail", "do not reply", "automated notification"],
      "route file sent": ["route file"],
      "spam mails sent": [],
      "perfect store sent": ["Perfect store", "secondaries", "shelf share"],
      "other projects sent": []
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
