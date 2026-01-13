# id: protocol-added-default-arg
# EXPECTED:
#   mypy: Error (inconsistent default argument for parameter)
#   pyright: No error
#   pyre: Error (inconsistent override)
#   zuban: Error (likely similar to Mypy/Pyre)
# REASON: Mypy and Pyre generally require that if a protocol method declares a parameter
#         without a default, any implementing method must also not have a default for that parameter.
#         Pyright is more lenient, focusing only on the callable signature and parameter types,
#         allowing an implementation to add a default where the protocol had none, as long as the parameter
#         is positionally compatible.

from typing import Protocol

class Notifier(Protocol):
    def send_notification(self, message: str, recipient: str) -> None: ...

class EmailNotifier:
    def send_notification(self, message: str, recipient: str = "admin@example.com") -> None:
        print(f"Sending email to {recipient}: {message}")

def notify_all(notifier: Notifier, msg: str) -> None:
    notifier.send_notification(msg, "default@example.com")

if __name__ == "__main__":
    email_n = EmailNotifier()
    notify_all(email_n, "Urgent message!")
    # mypy (with --strict): Protocol member "send_notification" of "Notifier" has inconsistent default argument for parameter "recipient" in "EmailNotifier" [misc]
    # pyright: No error (as of 1.1.346)
    # pyre: Inconsistent override [1]: `send_notification` in `EmailNotifier` is not a consistent override of `send_notification` in `Notifier`.
