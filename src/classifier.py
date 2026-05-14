import requests


def _build_prompt(subject, body, folder_config, mail_type):
    categories = folder_config[mail_type]
    lines = []
    for name, signals in categories.items():
        if signals:
            signals_str = ", ".join(f'"{s}"' for s in signals)
            lines.append(f'- "{name}": signals: {signals_str}')
        else:
            lines.append(f'- "{name}": catch-all for emails not matching other categories')

    valid_labels = ", ".join(f'"{name}"' for name in categories)

    return f"""You are an email classifier for an Outlook mailbox.

Classify the following email into exactly one of the listed categories using the keyword signals as guidance.

Categories:
{chr(10).join(lines)}

Rules:
1. Return ONLY the category name — no punctuation, no explanation
2. Valid responses: {valid_labels}
3. If you are not confident, return: unsure

Email:
Subject: {subject}
Body: {body}

Category:"""


def classify_email(subject, body, config, mail_type):
    prompt = _build_prompt(subject, body, config["folders"], mail_type)

    try:
        response = requests.post(
            f"{config['ollama']['endpoint']}/api/generate",
            json={"model": config["ollama"]["model"], "prompt": prompt, "stream": False},
            timeout=30,
        )
        response.raise_for_status()
        raw = response.json().get("response", "").strip().strip('"').lower()

        valid = {name.lower(): name for name in config["folders"][mail_type]}
        return valid.get(raw)

    except Exception:
        return None
