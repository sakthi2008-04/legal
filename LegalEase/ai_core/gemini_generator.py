import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


def generate_document(document_type, parties, terms, dates):

    if not API_KEY:
        raise ValueError("GEMINI_API_KEY is missing in .env")

    client = genai.Client(api_key=API_KEY)

    prompt = f"""
    Create a draft legal document.

    Document type: {document_type}
    Parties: {parties}
    Terms: {terms}
    Dates: {dates}

    Include a title, parties, clauses, dates, and signature lines.
    Clearly mention that this is a draft for review by a qualified lawyer.
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        return response.text or "No document was generated."

    except Exception as e:
        error_message = str(e)

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            raise Exception(
                "Gemini API quota exceeded. Please try again later."
            )

        raise Exception(f"Document generation failed: {error_message}")