# Eagle Mail Agent

A local, background-running Python agent that automatically classifies and sorts emails in Microsoft Outlook using a locally-hosted Ollama LLM (llama3). No cloud dependency — everything runs on your machine.

---

## How It Works

On each polling cycle (default: every 60 seconds) the agent:

1. Fetches all **unread emails** from your Inbox
2. Fetches any **new sent emails** not yet seen in the current session
3. Sends each email's subject and body to the local Ollama model (llama3)
4. Moves the email to the matching Outlook subfolder
5. If the model is not confident — the email is left untouched
6. Logs every action to `log.txt`

The agent **never** deletes, marks as read, replies to, or forwards any email.

---

## Prerequisites

### 1. Python 3.8+
Download from [python.org](https://www.python.org/downloads/).
During installation, check **"Add Python to PATH"**.

Verify in a terminal:
```
python --version
```

### 2. Microsoft Outlook (desktop)
Must be installed locally and configured with your mailbox. The agent connects to Outlook via COM — Outlook should be open when the agent is running.

### 3. Ollama
Download from [ollama.com](https://ollama.com) and install.

After installation, pull the llama3 model:
```
ollama pull llama3
```

Ollama runs as a background service automatically on Windows. You can verify it is running at:
```
http://localhost:11434
```

---

## Installation

**Step 1 — Download the project**

Place the `eagle_mail_agent` folder anywhere on your machine.

**Step 2 — Run setup**

Double-click `setup.bat`.

This will:
- Create a Python virtual environment (`venv/`) inside the project folder
- Install all dependencies (`pywin32`, `requests`)

You only need to run this once.

---

## Running the Agent

Double-click `run.bat`.

A terminal window will open showing the agent's activity in real time. Keep it running in the background — do not close it.

To stop the agent, close the terminal window or press `Ctrl+C`.

---

## Folder Structure in Outlook

The agent will automatically create the following subfolders in Outlook if they do not exist:

**Inside Inbox:**
| Folder | Sorted emails |
|---|---|
| automated mails | Emails containing automated/no-reply signals |
| route file | Emails mentioning "route file" |
| spam mails | Unsolicited or promotional emails |
| perfect store | Emails mentioning "Perfect store", "secondaries", "shelf share" |
| other projects | Work emails not matching any other category |

**Inside Sent Items:**
| Folder | Sorted emails |
|---|---|
| automated mails sent | Mirror of received automated mails |
| route file sent | Mirror of received route file |
| spam mails sent | Mirror of received spam mails |
| perfect store sent | Mirror of received perfect store |
| other projects sent | Mirror of received other projects |

---

## Configuration

All settings live in `config.json`. You can edit this file without touching any code.

| Setting | Description |
|---|---|
| `ollama.model` | Ollama model to use (default: `llama3`) |
| `ollama.endpoint` | Ollama API URL (default: `http://localhost:11434`) |
| `polling_interval_seconds` | How often the agent checks for new emails (default: `60`) |
| `max_body_chars` | Max characters of email body sent to the model (default: `2000`) |
| `folders.received` | Received folder names and their keyword signals |
| `folders.sent` | Sent folder names and their keyword signals |
| `log_path` | Path to the log file (default: `log.txt`) |

To add or change keywords for a folder, edit the signal list in `config.json`:
```json
"perfect store": ["Perfect store", "secondaries", "shelf share"]
```

---

## Logs

Every action is appended to `log.txt`:

```
[2025-05-14 14:32:01] INFO    | Eagle Mail Agent starting...
[2025-05-14 14:32:02] INFO    | Connected to Outlook. Folders verified/created.
[2025-05-14 14:32:03] MOVED   | inbox  | john@example.com          | Route File Q1 Weekly       | -> route file
[2025-05-14 14:32:04] SKIPPED | inbox  | unknown@promo.com         | Special Offer Just For You | Reason: low confidence
[2025-05-14 14:32:05] MOVED   | sent   | team@company.com          | Shelf Share Update         | -> perfect store sent
[2025-05-14 14:32:06] ERROR   | Inbox email processing failed: ...
```

---

## Project Structure

```
eagle_mail_agent/
├── src/
│   ├── __init__.py
│   ├── classifier.py        # Ollama API call and label parsing
│   ├── config_loader.py     # Loads and validates config.json
│   ├── folder_manager.py    # Subfolder lookup and auto-creation
│   ├── logger.py            # Append-mode logger (file + console)
│   └── outlook_client.py    # Outlook COM interface (read, move emails)
├── docs/
│   └── prd.md               # Product requirements document
├── main.py                  # Entry point and polling loop
├── config.json              # All user-editable settings
├── requirements.txt         # Python dependencies
├── setup.bat                # One-time setup (venv + install)
├── run.bat                  # Agent launcher
└── log.txt                  # Auto-generated at runtime
```

---

## Troubleshooting

**"Virtual environment not found" when running run.bat**
Run `setup.bat` first.

**"Failed to connect to Outlook"**
Make sure Microsoft Outlook is open and your mailbox is loaded before starting the agent.

**Emails are not being moved**
- Check `log.txt` for SKIPPED entries and their reason
- Verify Ollama is running: open a browser and go to `http://localhost:11434`
- Check that the llama3 model is pulled: run `ollama list` in a terminal

**Agent is moving emails I didn't expect**
Edit the keyword signals in `config.json` to be more specific, then restart the agent.
