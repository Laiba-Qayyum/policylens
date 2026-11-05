from datetime import datetime
from html import escape


def plural(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}s"


def describe(event: dict) -> str:
    if event["kind"] == "upload":
        return f"Uploaded {event['detail']}"
    if event["verified"]:
        return "Question answered, citation valid"
    return "Question answered, no valid citation"


def when(event: dict) -> str:
    return datetime.fromisoformat(event["time"]).strftime("%Y-%m-%d %H:%M UTC")


def rows(pairs: list[tuple[str, str]]) -> str:
    return "".join(
        f'<div class="pl-row"><span>{escape(left)}</span><span>{escape(right)}</span></div>'
        for left, right in pairs
    )


def card(value: str, label: str, icon: str, tone: str) -> str:
    return (
        f'<div class="pl-card"><div class="pl-icon {tone}">{icon}</div>'
        f'<div class="pl-num">{value}</div><div class="pl-label">{label}</div></div>'
    )


def event_name(event: dict) -> str:
    return "Document uploaded" if event["kind"] == "upload" else "Question asked"


def event_detail(event: dict) -> str:
    if event["kind"] == "upload":
        return event["detail"]
    return "Citation valid" if event["verified"] else "No valid citation"


def recent_panel(events: list[dict]) -> str:
    title = '<div class="pl-panel-title">Recent activity</div>'
    if not events:
        return f'<div class="pl-panel">{title}No activity yet.</div>'
    body = "".join(
        f"<tr><td>{escape(when(e))}</td><td>{event_name(e)}</td>"
        f"<td>{escape(event_detail(e))}</td></tr>"
        for e in events[:5]
    )
    head = "<tr><th>Time</th><th>Event</th><th>Details</th></tr>"
    return f'<div class="pl-panel">{title}<table class="pl-table">{head}{body}</table></div>'


def ring_panel(valid: int, total: int) -> str:
    title = '<div class="pl-panel-title">Citation check</div>'
    if total == 0:
        empty = '<div class="pl-ring-label">No questions yet</div>'
        return f'<div class="pl-panel">{title}{empty}</div>'
    percent = round(100 * valid / total)
    ring = f'<div class="pl-ring" style="--pct:{percent}"></div>'
    label = f'<div class="pl-ring-label">{percent}%</div>'
    caption = f"{valid} of {total} answers had a valid citation"
    return (
        f'<div class="pl-panel">{title}<div class="pl-ring-wrap">{ring}{label}</div>'
        f'<div class="pl-ring-caption">{caption}</div></div>'
    )
