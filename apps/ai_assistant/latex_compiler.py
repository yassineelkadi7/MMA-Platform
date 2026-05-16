"""
LaTeX compiler for the AI assistant — converts LaTeX source to PDF bytes.
"""

import os
import subprocess
import tempfile


class LaTeXCompilationError(Exception):
    pass


class LaTeXCompiler:
    def compile(self, latex_source: str) -> bytes:
        """
        Compile a LaTeX source string to PDF bytes.

        Attempts pdflatex first; falls back to WeasyPrint if pdflatex is
        unavailable. Raises LaTeXCompilationError with compiler output on
        non-zero exit code.
        """
        try:
            return self._compile_with_pdflatex(latex_source)
        except FileNotFoundError:
            # pdflatex not installed — fall back to WeasyPrint
            return self._compile_with_weasyprint(latex_source)

    def _compile_with_pdflatex(self, latex_source: str) -> bytes:
        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = os.path.join(tmpdir, "document.tex")
            pdf_path = os.path.join(tmpdir, "document.pdf")

            with open(tex_path, "w", encoding="utf-8") as f:
                f.write(latex_source)

            result = subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-output-directory",
                    tmpdir,
                    tex_path,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                raise LaTeXCompilationError(
                    f"pdflatex failed (exit {result.returncode}):\n{result.stdout}\n{result.stderr}"
                )

            with open(pdf_path, "rb") as f:
                return f.read()

    def _compile_with_weasyprint(self, latex_source: str) -> bytes:
        try:
            from weasyprint import HTML  # type: ignore

            # WeasyPrint renders HTML/CSS, not LaTeX — produce a minimal HTML
            # wrapper so the raw LaTeX source is at least readable as a fallback.
            html_content = f"<html><body><pre>{latex_source}</pre></body></html>"
            return HTML(string=html_content).write_pdf()
        except ImportError:
            raise LaTeXCompilationError(
                "Neither pdflatex nor WeasyPrint is available. "
                "Please install one of them to generate PDF training programs."
            )
