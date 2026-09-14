import hashlib
from pathlib import Path
from django.conf import settings


def calculate_sha256(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


def isPdfFileExist(file):

    documents_folder = Path(settings.BASE_DIR, "media", "chatbot")

    reference_file = documents_folder / "UCSTgo-list.pdf"

    reference_hash = calculate_sha256(reference_file)

    for pdf_file in documents_folder.glob("*.pdf"):

        if pdf_file == reference_file:
            print("File already existed!")
            return True

        pdf_hash = calculate_sha256(pdf_file)

        if pdf_hash == reference_hash:
            print(f"✅ {pdf_file.name} is IDENTICAL to {reference_file.name}")
            print("File already existed!")
            return True

    print("File is not exist!")

    return False


