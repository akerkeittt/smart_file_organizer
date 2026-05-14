# pyre-ignore-all-errors

import time
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.services.notification_service import NotificationService

class DownloadHandler(FileSystemEventHandler):

    def __init__(self, file_processing):
        self.file_processing = file_processing

    def on_moved(self, event):

        if event.is_directory:
            return

        file_path = event.dest_path

        # Ignore temporary Chrome download files
        if file_path.endswith(".crdownload"):
            return

        # Allowed file extensions
        ALLOWED_EXTENSIONS = {
            ".txt",
            ".pdf",
            ".doc",
            ".docx",
            ".png",
            ".jpg",
            ".jpeg",
            ".tiff",
            ".tif",
            ".bmp"
        }

        if Path(file_path).suffix.lower() not in ALLOWED_EXTENSIONS:
            return

        print(f"[WATCHER] Download completed: {file_path}")

        # Wait a moment to ensure file is fully written
        time.sleep(2)

        try:

            # Add file to database
            self.file_processing.add_file(file_path)

            # Generate AI tags
            tags = self.file_processing.process_file(file_path)

            # Save generated tags
            self.file_processing.update_tags(file_path, tags)

            print(f"[WATCHER] Tags generated: {tags}")

            NotificationService.notify(
                "Smart File Organizer",
                f"Tags generated: {', '.join(tags)}"
            )
        except Exception as e:
            print(f"[WATCHER ERROR] {e}")


class DownloadWatcher:

    def __init__(self, file_processing):
        self.file_processing = file_processing
        self.observer = Observer()

    def start(self):

        # YOUR DOWNLOADS FOLDER
        downloads_path = str(Path.home() / "Downloads")

        print(f"[WATCHER] Monitoring folder: {downloads_path}")

        event_handler = DownloadHandler(self.file_processing)

        self.observer.schedule(
            event_handler,
            downloads_path,
            recursive=False
        )

        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()