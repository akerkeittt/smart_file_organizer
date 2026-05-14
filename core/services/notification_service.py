# pyre-ignore-all-errors

from plyer import notification


class NotificationService:

    @staticmethod
    def notify(title: str, message: str):
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=5
            )
        except Exception as e:
            print(f"[NOTIFICATION ERROR] {e}")