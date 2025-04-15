import subprocess

def convert_docx_to_pdf(docx_path, pdf_path):
    """
    Convert a DOCX file to PDF using LibreOffice in headless mode
    ```
    sudo apt-get install libreoffice
    ```
    make sure to install LibreOffice.
    Args:
        docx_path (str): Path to the DOCX file
        pdf_path (str): Path to save the converted PDF file
    """
    command = ['libreoffice', '--headless', '--convert-to', 'pdf', docx_path, '--outdir', pdf_path]
    subprocess.run(command, check=True)