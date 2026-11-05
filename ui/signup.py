import re
import unicodedata
from html import escape

import streamlit as st

from src.client import ApiError, PolicyLensClient

MAX_LENGTH = 64

HERO = (
    '<div class="pl-hero"><div class="pl-hero-brand">PolicyLens</div>'
    '<h1 class="pl-hero-title">Your company policies. One intelligent place.</h1>'
    '<p class="pl-hero-text">Upload your HR policies and handbooks, then ask questions '
    "in plain language. Every answer shows the document and page it came from.</p>"
    '<div class="pl-flow"><div class="pl-step">Documents</div><div class="pl-arrow">&rarr;</div>'
    '<div class="pl-step">Retrieval</div><div class="pl-arrow">&rarr;</div>'
    '<div class="pl-step">Answer [1]</div></div>'
    '<div class="pl-trust">Every answer shows its source, so you can check it.</div></div>'
)


def workspace_slug(company: str) -> str:
    plain = unicodedata.normalize("NFKD", company).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")
    return slug[:MAX_LENGTH].rstrip("-")


def company_error(company: str) -> str | None:
    if not company.strip():
        return "Enter your company name."
    if not workspace_slug(company):
        return "Use letters or numbers in the company name."
    return None


def signin_credentials(name: str, key: str) -> tuple[str, str]:
    cleaned = name.strip().lower()
    if not re.fullmatch(r"[a-z0-9_-]+", cleaned):
        cleaned = workspace_slug(name)
    return cleaned, key.strip()


def key_file(tenant: str, key: str) -> str:
    return (
        "PolicyLens workspace key\n"
        f"Workspace: {tenant}\n"
        f"Key: {key}\n\n"
        "Keep this file private. Anyone with this key can read and change the workspace.\n"
        "The server stores only a fingerprint of the key, so it cannot be recovered.\n"
    )


def render_signup(api_url: str) -> None:
    left, right = st.columns(2)
    with left:
        st.markdown(HERO, unsafe_allow_html=True)
    with right:
        pending = st.session_state.get("new_workspace")
        if pending:
            _show_key(pending)
        else:
            _show_forms(api_url)


def _show_forms(api_url: str) -> None:
    st.markdown(
        '<h2 class="pl-form-title">Create your PolicyLens workspace</h2>'
        '<p class="pl-sub">A workspace keeps your documents separate from everyone else\'s. '
        "You get a private key to sign in with.</p>",
        unsafe_allow_html=True,
    )
    create_tab, signin_tab = st.tabs(["Create workspace", "Sign in"])
    with create_tab:
        _create_form(api_url)
    with signin_tab:
        _signin_form(api_url)


def _create_form(api_url: str) -> None:
    company = st.text_input("Company name", key="company")
    slug = workspace_slug(company)
    if company.strip():
        address = escape(slug) or "-"
        st.markdown(
            f'<div class="pl-address">Workspace address: <b>{address}</b></div>',
            unsafe_allow_html=True,
        )
    if st.button("Create workspace", key="create", type="primary"):
        error = company_error(company)
        if error:
            st.error(error)
            return
        try:
            with st.spinner("Creating your workspace..."):
                st.session_state["new_workspace"] = PolicyLensClient(api_url).create_workspace(slug)
        except ApiError as problem:
            st.error(str(problem))
        else:
            st.rerun()


def _signin_form(api_url: str) -> None:
    typed_name = st.text_input("Workspace name", key="signin_name")
    typed_key = st.text_input("Workspace key", type="password", key="signin_key")
    if not st.button("Sign in", key="signin", type="primary"):
        return
    name, key = signin_credentials(typed_name, typed_key)
    try:
        PolicyLensClient(api_url, api_key=key).documents(name)
    except ApiError as problem:
        if str(problem).startswith("Cannot reach"):
            st.error(str(problem))
        else:
            st.error("That workspace name and key don't match.")
    else:
        st.session_state["workspace"] = name
        st.session_state["workspace_key"] = key
        st.rerun()


def _show_key(pending: dict) -> None:
    tenant, key = pending["tenant"], pending["api_key"]
    st.markdown(
        '<h2 class="pl-form-title">Your workspace is ready</h2>'
        '<p class="pl-sub">This is your key. It is shown only once and cannot be recovered. '
        "Copy it or download it now.</p>",
        unsafe_allow_html=True,
    )
    st.code(key, language=None)
    st.download_button(
        "Download key",
        data=key_file(tenant, key),
        file_name=f"{tenant}-policylens-key.txt",
        mime="text/plain",
        key="download",
    )
    saved = st.checkbox(
        "I've saved my key. It is shown only once and can't be recovered.", key="saved"
    )
    if st.button("Continue to dashboard", key="continue", disabled=not saved, type="primary"):
        st.session_state["workspace"] = tenant
        st.session_state["workspace_key"] = key
        del st.session_state["new_workspace"]
        st.rerun()
