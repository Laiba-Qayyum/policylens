from datetime import datetime
from html import escape

import streamlit as st

from src.client import ApiError, PolicyLensClient

STYLE = """<style>
@keyframes pl-rise {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0b2a4a 0%, #0e4a5a 100%); }
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: #e6f2f5; }
.pl-brand { font-size: 1.7rem; font-weight: 700; color: #ffffff; margin-bottom: 14px; }
[data-baseweb="tab-list"] { gap: 8px; }
[data-baseweb="tab"] { border-radius: 999px; padding: 6px 18px; }
[data-baseweb="tab"][aria-selected="true"] { background: #0f766e; color: #ffffff; }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display: none; }
.pl-head { display: flex; justify-content: space-between; align-items: center; gap: 16px; }
.pl-welcome { margin: 0; font-size: 2rem; font-weight: 700; }
.pl-sub { margin: 4px 0 0; opacity: 0.75; }
.pl-chips { display: flex; gap: 10px; align-items: center; }
.pl-chip { padding: 6px 14px; border-radius: 999px; background: rgba(128, 128, 128, 0.15); }
.pl-pill { padding: 6px 14px; border-radius: 999px; font-size: 0.9rem; }
.pl-pill.ok { background: rgba(34, 197, 94, 0.18); color: #22c55e; }
.pl-pill.bad { background: rgba(239, 68, 68, 0.18); color: #ef4444; }
.pl-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 14px 0; }
@media (max-width: 900px) { .pl-grid { grid-template-columns: repeat(2, 1fr); } }
.pl-card, .pl-panel {
  padding: 16px 18px;
  border-radius: 14px;
  background: rgba(128, 128, 128, 0.10);
  border: 1px solid rgba(128, 128, 128, 0.18);
  animation: pl-rise 0.5s ease both;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.pl-card:hover, .pl-panel:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}
.pl-grid .pl-card:nth-child(2) { animation-delay: 0.08s; }
.pl-grid .pl-card:nth-child(3) { animation-delay: 0.16s; }
.pl-grid .pl-card:nth-child(4) { animation-delay: 0.24s; }
.pl-icon {
  width: 38px; height: 38px; border-radius: 10px; margin-bottom: 10px;
  display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
}
.pl-icon.t1 { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
.pl-icon.t2 { background: rgba(20, 184, 166, 0.2); color: #2dd4bf; }
.pl-icon.t3 { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.pl-icon.t4 { background: rgba(34, 197, 94, 0.2); color: #4ade80; }
.pl-num { font-size: 2rem; font-weight: 700; line-height: 1.1; }
.pl-label { opacity: 0.75; }
.pl-panel-title { font-weight: 700; margin-bottom: 10px; }
.pl-table { width: 100%; border-collapse: collapse; }
.pl-table th { text-align: left; opacity: 0.6; font-weight: 600; padding: 6px 8px; }
.pl-table td { padding: 8px; border-top: 1px solid rgba(128, 128, 128, 0.18); }
.pl-panel > .pl-ring-label { opacity: 0.75; padding: 8px 0; }
.pl-ring-wrap { position: relative; width: 150px; height: 150px; margin: 8px auto; }
.pl-ring {
  width: 150px; height: 150px; border-radius: 50%;
  background: conic-gradient(#14b8a6 calc(var(--pct) * 1%), rgba(128, 128, 128, 0.25) 0);
  -webkit-mask: radial-gradient(farthest-side, transparent 66%, #000 67%);
  mask: radial-gradient(farthest-side, transparent 66%, #000 67%);
}
.pl-ring-wrap .pl-ring-label {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  font-size: 1.8rem; font-weight: 700;
}
.pl-ring-caption { text-align: center; opacity: 0.75; }
.pl-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 14px;
  margin-bottom: 8px;
  border-radius: 10px;
  background: rgba(128, 128, 128, 0.08);
  animation: pl-rise 0.4s ease both;
  transition: transform 0.2s ease, background 0.2s ease;
}
.pl-row:hover { transform: translateX(4px); background: rgba(128, 128, 128, 0.16); }
.pl-row span:last-child { opacity: 0.7; white-space: nowrap; }
.pl-row:nth-child(2) { animation-delay: 0.05s; }
.pl-row:nth-child(3) { animation-delay: 0.10s; }
.pl-row:nth-child(4) { animation-delay: 0.15s; }
.pl-row:nth-child(5) { animation-delay: 0.20s; }
.pl-row:nth-child(n+6) { animation-delay: 0.25s; }
@media (prefers-reduced-motion: reduce) {
  .pl-card, .pl-panel, .pl-row { animation: none; transition: none; }
}
</style>"""


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


st.set_page_config(page_title="PolicyLens", layout="wide")
st.markdown(STYLE, unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="pl-brand">PolicyLens</div>', unsafe_allow_html=True)
    api_url = st.text_input("API address", "http://127.0.0.1:8000")
    tenant = st.text_input("Tenant", "acme")
    api_key = st.text_input("API key", type="password", key="api_key")
client = PolicyLensClient(api_url, api_key=api_key)

header = st.container()
overview_tab, ask_tab, documents_tab, activity_tab = st.tabs(
    ["Overview", "Ask", "Documents", "Activity"]
)

with documents_tab:
    st.subheader("Add documents")
    uploads = st.file_uploader(
        "PDF, DOCX or TXT files", type=["pdf", "docx", "txt"], accept_multiple_files=True
    )
    if st.button("Upload", key="upload") and uploads:
        try:
            result = client.upload(tenant, [(f.name, f.getvalue()) for f in uploads])
            st.success(f"Added {result['chunks']} chunks from {', '.join(result['files'])}")
        except ApiError as error:
            st.error(str(error))

with ask_tab:
    st.subheader("Ask a question")
    question = st.text_input("Question", key="question")
    if st.button("Ask", key="ask") and question:
        try:
            with st.spinner("Thinking..."):
                answer = client.ask(tenant, question)
        except ApiError as error:
            st.error(str(error))
        else:
            st.write(answer["answer"])
            if not answer["verified"]:
                st.warning(
                    "Unverified: the reply did not cite a valid source. "
                    "Check the sources below yourself."
                )
            if answer["competing"]:
                st.info(
                    "These files may disagree (newest first): " + ", ".join(answer["competing"])
                )
            for source in answer["sources"]:
                st.caption(f"Source: {source['source']}, page {source['page']}")
            st.caption(
                "The source shown is a best match, not proof. Check it before relying on it."
            )

try:
    docs = client.documents(tenant)
    activity = client.activity(tenant)
    load_error = None
except ApiError as error:
    docs = activity = None
    load_error = str(error)

with header:
    status = "bad" if load_error else "ok"
    text = "API unreachable" if load_error else "API connected"
    pill = f'<span class="pl-pill {status}">{text}</span>'
    chips = f'<div class="pl-chips"><span class="pl-chip">{escape(tenant)}</span>{pill}</div>'
    intro = (
        '<div><h1 class="pl-welcome">Welcome to PolicyLens</h1>'
        '<p class="pl-sub">Ask questions about your policy documents and see which '
        "source each answer comes from.</p></div>"
    )
    st.markdown(f'<div class="pl-head">{intro}{chips}</div>', unsafe_allow_html=True)

with overview_tab:
    if load_error:
        st.error(load_error)
    else:
        summary = activity["summary"]
        valid, total = summary["verified_questions"], summary["questions"]
        st.markdown(
            '<div class="pl-grid">'
            + card(str(len(docs["documents"])), "Documents", "≡", "t1")
            + card(str(docs["total_chunks"]), "Indexed chunks", "▦", "t2")
            + card(str(total), "Questions asked", "?", "t3")
            + card(f"{valid} of {total}", "Answers with a valid citation", "✓", "t4")
            + "</div>",
            unsafe_allow_html=True,
        )
        left, right = st.columns([2, 1])
        left.markdown(recent_panel(activity["events"]), unsafe_allow_html=True)
        right.markdown(ring_panel(valid, total), unsafe_allow_html=True)

with documents_tab:
    if not load_error:
        st.subheader("Your documents")
        files = [(d["source"], plural(d["chunks"], "chunk")) for d in docs["documents"]]
        st.markdown(rows(files) or "No documents yet.", unsafe_allow_html=True)

with activity_tab:
    if not load_error:
        st.subheader("Recent activity")
        events = [(describe(e), when(e)) for e in activity["events"]]
        st.markdown(rows(events) or "No activity yet.", unsafe_allow_html=True)
