import streamlit as st
import requests
import re
from io import BytesIO
from docx import Document
from fpdf import FPDF

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="centered"
)

st.title("⚖️ LegalEase")
st.subheader("AI-Powered Legal Document Generator")
st.write("Fill in the details to generate your legal document.")

document_type = st.selectbox(
    "Document Type",
    [
        "Rental Agreement",
        "Employment Contract",
        "Non-Disclosure Agreement"
    ]
)

st.subheader("Party Details")
parties = st.text_area(
    "Names and details of the parties",
    placeholder="Example: Owner: Ravi, Tenant: Kumar"
)

st.subheader("Terms and Conditions")
terms = st.text_area(
    "Enter the terms",
    placeholder="Example: Monthly rent is Rs. 5000."
)

dates = st.text_input(
    "Important Dates",
    placeholder="Example: Agreement starts on 1 October 2026"
)

if st.button("Generate Document"):
    if not parties.strip() or not terms.strip() or not dates.strip():
        st.warning("Please fill in all the fields.")
    else:
        with st.spinner("Generating your document..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8001/generate",
                    json={
                        "document_type": document_type,
                        "parties": parties,
                        "terms": terms,
                        "dates": dates
                    },
                    timeout=120
                )

                if response.status_code == 200:
                    st.session_state["document"] = (
                        response.json()["document"]
                    )
                    st.success("Document generated successfully!")
                else:
                    st.error(
                        f"Backend Error ({response.status_code}): "
                        f"{response.text}"
                    )

            except requests.exceptions.ConnectionError:
                st.error("Backend is not running.")
            except requests.exceptions.Timeout:
                st.error("Request timed out. Please try again.")
            except Exception as e:
                st.error(f"An error occurred: {e}")


def clean_text(text):
    """Remove common Markdown formatting for document exports."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    return text


def create_docx(text):
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)

    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output.getvalue()


def create_pdf(text):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    for line in text.splitlines():
        # Built-in PDF font supports Latin-1 only.
        safe_line = line.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 7, safe_line)

    return bytes(pdf.output())


if "document" in st.session_state:
    document = st.session_state["document"]

    st.subheader("Generated Document")
    st.text_area(
        "Document Preview",
        value=document,
        height=500
    )

    clean_document = clean_text(document)

    st.subheader("Download Document")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.download_button(
            label="Download TXT",
            data=clean_document,
            file_name="LegalEase_Document.txt",
            mime="text/plain"
        )

    with col2:
        st.download_button(
            label="Download DOCX",
            data=create_docx(clean_document),
            file_name="LegalEase_Document.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    with col3:
        try:
            pdf_data = create_pdf(clean_document)
            st.download_button(
                label="Download PDF",
                data=pdf_data,
                file_name="LegalEase_Document.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"PDF creation failed: {e}")