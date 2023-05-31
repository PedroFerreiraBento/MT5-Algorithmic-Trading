from datetime import datetime


def get_timestamp_ms(date: datetime) -> int:
    """Get the timestamp in ms

    Args:
        date (datetime): Datetime that will be converted

    Returns:
        int: Timestamp in ms
    """
    # Split datetime
    timestamp = str(date.timestamp())
    seconds, microseconds = timestamp.split(".")

    # Set the standard microseconds size
    microseconds = microseconds.ljust(6, "0")

    return int(seconds + microseconds)
