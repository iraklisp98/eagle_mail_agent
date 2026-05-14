from .classifier import classify_email
from .logger import log_moved, log_skipped, log_error


def process_inbox(client, config):
    for email in client.get_unread_inbox_emails():
        try:
            subject = getattr(email, "Subject", "") or ""
            body = (getattr(email, "Body", "") or "")[: config["max_body_chars"]]
            sender = client.get_sender(email)

            folder = classify_email(subject, body, config, "received")

            if folder:
                client.move_to_received_folder(email, folder)
                log_moved("inbox", sender, subject, folder)
            else:
                log_skipped("inbox", sender, subject, "low confidence")
        except Exception as e:
            log_error(f"Inbox email processing failed: {e}")


def process_sent(client, config, processed_ids):
    for email in client.get_new_sent_emails(processed_ids):
        try:
            entry_id = email.EntryID
            processed_ids.add(entry_id)

            subject = getattr(email, "Subject", "") or ""
            body = (getattr(email, "Body", "") or "")[: config["max_body_chars"]]
            recipient = client.get_first_recipient(email)

            folder = classify_email(subject, body, config, "sent")

            if folder:
                client.move_to_sent_folder(email, folder)
                log_moved("sent", recipient, subject, folder)
            else:
                log_skipped("sent", recipient, subject, "low confidence")
        except Exception as e:
            log_error(f"Sent email processing failed: {e}")
