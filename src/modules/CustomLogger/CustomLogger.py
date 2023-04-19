from datetime import datetime

# pylint: disable=all


class Logger:
    """Generic logger class"""

    def info(self, msg: str = "") -> None:
        """."""
        tm_n: datetime = datetime.now()
        _hr: str = f"{tm_n.hour:0>2}"
        _mn: str = f"{tm_n.minute:0>2}"
        _sec: str = f"{tm_n.second:0>2}"
        _msec: str = f"{tm_n.microsecond:0>2}"
        _tm: str = f"{_hr}:{_mn}:{_sec}:{_msec[:2]}"

        print(f"[INFO]  ({_tm})\t{msg.upper()}")

    def warn(self, msg: str = "") -> None:
        """."""
        tm_n: datetime = datetime.now()
        _hr: str = f"{tm_n.hour:0>2}"
        _mn: str = f"{tm_n.minute:0>2}"
        _sec: str = f"{tm_n.second:0>2}"
        _msec: str = f"{tm_n.microsecond:0>2}"
        _tm: str = f"{_hr}:{_mn}:{_sec}:{_msec[:2]}"

        print(f"[WARN]  ({_tm})\t{msg.upper()}")

    def error(self, msg: str = "") -> None:
        """."""
        tm_n: datetime = datetime.now()
        _hr: str = f"{tm_n.hour:0>2}"
        _mn: str = f"{tm_n.minute:0>2}"
        _sec: str = f"{tm_n.second:0>2}"
        _msec: str = f"{tm_n.microsecond:0>2}"
        _tm: str = f"{_hr}:{_mn}:{_sec}:{_msec[:2]}"

        print(f"[ERROR] ({_tm})\t{msg.upper()}")
