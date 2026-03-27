import io
from typing import Optional

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

try:
    import docx
except ImportError:
    docx = None

from core.adapters.file_system_adapter import FileSystemAdapter


class ContentAnalysisService:
    """
    Responsible for extracting text content from files.
    Supports: .txt, .pdf, .docx, .png/.jpg/.jpeg (OCR).
    """

    SUPPORTED_TEXT = {".txt"}
    SUPPORTED_PDF = {".pdf"}
    SUPPORTED_DOCX = {".doc", ".docx"}
    SUPPORTED_IMAGE = {".png", ".jpg", ".jpeg"}

    def __init__(self, fs_adapter: FileSystemAdapter):
        self._fs = fs_adapter

    @property
    def supported_extensions(self) -> set:
        return self.SUPPORTED_TEXT | self.SUPPORTED_PDF | self.SUPPORTED_DOCX | self.SUPPORTED_IMAGE

    def extract_text(self, file_path: str) -> str:
        """
        Extract text content from a file based on its extension.
        Returns the extracted text or an error message string.
        """
        ext = self._fs.get_extension(file_path)

        try:
            if ext == ".doc":
                return "Error: Legacy .doc files are not supported by python-docx. Please convert to .docx or .pdf."
            elif ext in self.SUPPORTED_TEXT:
                return self._extract_txt(file_path)
            elif ext in self.SUPPORTED_PDF:
                return self._extract_pdf(file_path)
            elif ext in self.SUPPORTED_DOCX:
                return self._extract_docx(file_path)
            elif ext in self.SUPPORTED_IMAGE:
                return self._extract_image(file_path)
            else:
                return f"Unsupported file format for text extraction: {ext}"
        except Exception as e:
            return f"Error reading file {file_path}: {e}"

    # ------------------------------------------------------------------
    # Private extraction methods
    # ------------------------------------------------------------------

    def _extract_txt(self, file_path: str) -> str:
        return self._fs.read_text(file_path)

    def _extract_pdf(self, file_path: str) -> str:
        if PyPDF2 is None:
            return "Error: PyPDF2 not installed. Use 'pip install PyPDF2' to read PDFs."

        raw = self._fs.read_bytes(file_path)
        reader = PyPDF2.PdfReader(io.BytesIO(raw))
        text_parts = []
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text_parts.append(extracted)
        return "\n".join(text_parts)

    def _extract_docx(self, file_path: str) -> str:
        if docx is None:
            return "Error: python-docx not installed. Use 'pip install python-docx' to read DOCX files."

        raw = self._fs.read_bytes(file_path)
        document = docx.Document(io.BytesIO(raw))
        text_parts = [paragraph.text for paragraph in document.paragraphs if paragraph.text]
        return "\n".join(text_parts)

    def _extract_image(self, file_path: str) -> str:
        if pytesseract is None or Image is None:
            return ("Error: pytesseract or Pillow not installed. "
                    "Use 'pip install pytesseract Pillow' to scan images.")

        raw = self._fs.read_bytes(file_path)
        image = Image.open(io.BytesIO(raw))
        return pytesseract.image_to_string(image)
