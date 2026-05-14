import win32com.client
from .folder_manager import ensure_subfolders
from .logger import log_info, log_error


class OutlookClient:
    def __init__(self, config):
        self.config = config
        self._connect()

    def _connect(self):
        try:
            self.app = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.app.GetNamespace("MAPI")
            self.inbox = self.namespace.GetDefaultFolder(6)   # olFolderInbox
            self.sent = self.namespace.GetDefaultFolder(5)    # olFolderSentMail
            self.received_folders, self.sent_folders = ensure_subfolders(
                self.inbox, self.sent, self.config
            )
            log_info("Connected to Outlook. Folders verified/created.")
        except Exception as e:
            log_error(f"Failed to connect to Outlook: {e}")
            raise

    def get_unread_inbox_emails(self):
        emails = []
        for item in self.inbox.Items:
            try:
                if hasattr(item, "UnRead") and item.UnRead:
                    emails.append(item)
            except Exception:
                continue
        return emails

    def get_all_sent_ids(self):
        ids = set()
        for item in self.sent.Items:
            try:
                ids.add(item.EntryID)
            except Exception:
                continue
        return ids

    def get_new_sent_emails(self, processed_ids):
        emails = []
        for item in self.sent.Items:
            try:
                if item.EntryID not in processed_ids:
                    emails.append(item)
            except Exception:
                continue
        return emails

    def move_to_received_folder(self, email, folder_name):
        target = self.received_folders.get(folder_name)
        if target:
            email.Move(target)
            return True
        return False

    def move_to_sent_folder(self, email, folder_name):
        target = self.sent_folders.get(folder_name)
        if target:
            email.Move(target)
            return True
        return False

    def get_sender(self, email):
        try:
            return email.SenderEmailAddress or "unknown"
        except Exception:
            return "unknown"

    def get_first_recipient(self, email):
        try:
            recipients = email.Recipients
            if recipients.Count > 0:
                return recipients.Item(1).Address
            return "unknown"
        except Exception:
            return "unknown"
