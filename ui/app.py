from html import escape

import streamlit as st

from src.client import ApiError, PolicyLensClient
from ui.components import (
    card,
    describe,
    plural,
    recent_panel,
    ring_panel,
    rows,
    when,
)
from ui.signup import render_signup
from ui.styles import STYLE

st.set_page_config(page_title="PolicyLens", layout="wide")
st.markdown(STYLE, unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="pl-brand">PolicyLens</div>', unsafe_allow_html=True)
    with st.expander("Advanced"):
        api_url = st.text_input("API address", "http://127.0.0.1:8000", key="api_url")

if "workspace" not in st.session_state:
    render_signup(api_url)
    st.stop()

tenant = st.session_state["workspace"]
client = PolicyLensClient(api_url, api_key=st.session_state["workspace_key"])

with st.sidebar:
    st.caption(f"Signed in as {tenant}")
    if st.button("Sign out", key="signout"):
        for name in ("workspace", "workspace_key", "new_workspace"):
            st.session_state.pop(name, None)
        st.rerun()

header = st.container()
overview_tab, ask_tab, documents_tab, activity_tab = st.tabs(
    ["Overview", "Ask", "Documents", "Activity"]
)

with documents_tab:
    st.subheader("Add documents")
    uploads = st.file_uploader(
        "PDF, DOCX or TXT files", type=["pdf", "docx", "txt"], accept_multiple_files=True
    )
    st.caption("Choose your files, then click Upload to add them.")
    if st.button("Upload", key="upload") and uploads:
        try:
            result = client.upload(tenant, [(f.name, f.getvalue()) for f in uploads])
            st.success(f"Added {result['chunks']} chunks from {', '.join(result['files'])}")
        except ApiError as error:
            st.error(str(error))

with ask_tab:
    st.subheader("Ask a question")
    empty_hint = st.empty()
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

if docs is not None and not docs["documents"]:
    empty_hint.info(
        "Upload a document first: open the Documents tab, choose a file, then click Upload."
    )

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
