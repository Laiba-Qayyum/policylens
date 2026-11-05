import streamlit as st

from src.client import ApiError, PolicyLensClient

st.set_page_config(page_title="PolicyLens")
st.title("PolicyLens")

with st.sidebar:
    api_url = st.text_input("API address", "http://127.0.0.1:8000")
    tenant = st.text_input("Tenant", "acme")
client = PolicyLensClient(api_url)

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
            st.info("These files may disagree (newest first): " + ", ".join(answer["competing"]))
        for source in answer["sources"]:
            st.caption(f"Source: {source['source']}, page {source['page']}")
        st.caption("The source shown is a best match, not proof. Check it before relying on it.")
