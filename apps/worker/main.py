from __future__ import annotations

import time

from core.bot_runtime import BotRuntime


def main() -> None:
    runtime = BotRuntime()
    runtime.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        runtime.stop()


if __name__ == "__main__":
    main()

