import time

from src.config_loader import load_config
from src.logger import init_logger, log_info, log_error
from src.outlook_client import OutlookClient
from src.process import process_inbox, process_sent


def main():
    config = load_config()
    init_logger(config["log_path"])
    log_info("Eagle Mail Agent starting...")

    client = OutlookClient(config)

    processed_sent_ids = client.get_all_sent_ids()
    log_info(f"Snapshot taken: {len(processed_sent_ids)} existing sent emails will be skipped.")
    log_info(f"Polling every {config['polling_interval_seconds']}s. Press Ctrl+C to stop.")

    while True:
        try:
            process_inbox(client, config)
            process_sent(client, config, processed_sent_ids)
        except Exception as e:
            log_error(f"Poll cycle error: {e}")

        time.sleep(config["polling_interval_seconds"])


if __name__ == "__main__":
    main()
