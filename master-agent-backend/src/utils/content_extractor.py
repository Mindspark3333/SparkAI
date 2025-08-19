import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import tempfile
import os
import mimetypes
from typing import Dict, Any, List, Optional


class ContentExtractor:
    """
    Utility class for extracting text and metadata from different content types.
    Supports: web pages (HTML), PDF documents, and plain text.
    """

    def __init__(self):
        self.session = requests.Session()

    def fetch_url(self, url: str) -> str:
        """Download raw content from a URL."""
        try:
            response = self.session.get(url, timeout=20)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise RuntimeError(f"Failed to fetch URL {url}: {e}")

    def extract_from_html(self, html_content: str) -> Dict[str, Any]:
        """Parse and extract clean text + metadata from HTML."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        text = " ".join(soup.get_text().split())

        title = soup.title.string if soup.title else None
        meta_description = None
        meta = soup.find("meta", attrs={"name": "description"})
        if meta and "content" in meta.attrs:
            meta_description = meta["content"]

        return {
            "title": title,
            "description": meta_description,
            "raw_text": text,
        }

    def extract_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text from a PDF file."""
        text = ""
        try:
            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from PDF: {e}")

        return {
            "title": os.path.basename(file_path),
            "raw_text": text.strip(),
        }

    def extract(self, source: str, content_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Auto-detect and extract content.
        - If content_type provided: use it directly.
        - Otherwise: detect by URL or file extension.
        """
        if not content_type:
            content_type, _ = mimetypes.guess_type(source)

        if content_type:
            if "html" in content_type:
                html = self.fetch_url(source)
                return self.extract_from_html(html)
            elif "pdf" in content_type:
                # Download to temp file
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                try:
                    response = self.session.get(source, timeout=30)
                    response.raise_for_status()
                    tmp.write(response.content)
                    tmp.close()
                    return self.extract_from_pdf(tmp.name)
                finally:
                    os.unlink(tmp.name)

        # Fallback: assume plain text
        return {
            "title": None,
            "raw_text": self.fetch_url(source),
        }