import re
import unicodedata

MAX_LENGTH = 64


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
