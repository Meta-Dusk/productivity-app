import asyncio
from datetime import datetime


# Async Timers
async def safe_sleep(duration: float, stop_event: asyncio.Event) -> None:
    try:
        await asyncio.wait_for(stop_event.wait(), timeout=duration)
    except asyncio.TimeoutError:
        pass
    

# Formatting
def format_time(seconds: int) -> str:
    """Format a duration in seconds into a human-readable string."""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes}m {seconds}s" if seconds else f"{minutes}m"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m" if minutes else f"{hours}h"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h" if hours else f"{days}d"

# Date Stuff
def get_date() -> str:
    """Returns a formatted `date` + `time` string."""
    now = datetime.now()
    formatted = now.strftime("%Y-%m-%d %H:%M:%S")
    return formatted