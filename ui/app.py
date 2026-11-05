from datetime import datetime
from html import escape

import streamlit as st

from src.client import ApiError, PolicyLensClient


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


st.set_page_config(page_title="PolicyLens", layout="wide")
st.title("PolicyLens")

with st.sidebar:
    api_url = st.text_input("API address", "http://127.0.0.1:8000")
    tenant = st.text_input("Tenant", "acme")
    api_key = st.text_input("API key", type="password", key="api_key")
client = PolicyLensClient(api_url, api_key=api_key)

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

with overview_tab:
    if load_error:
        st.error(load_error)
    else:
        summary = activity["summary"]
        columns = st.columns(4)
        columns[0].metric("Documents", len(docs["documents"]))
        columns[1].metric("Chunks", docs["total_chunks"])
        columns[2].metric("Questions", summary["questions"])
        columns[3].metric(
            "Answers with a valid citation",
            f"{summary['verified_questions']} of {summary['questions']}",
        )

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
