import re
from django.core.files.storage import FileSystemStorage


class UnicodePreservingStorage(FileSystemStorage):
    """
    Custom storage that preserves Unicode combining characters in filenames.

    Django's default get_valid_name() uses re.sub(r"(?u)[^\\w\\s.-]", "", s)
    which strips Unicode Mark characters (Mc, Mn) — this removes Myanmar
    vowel signs (ါ, ေ, ိ, etc.) and tone marks, leaving only base consonants.

    This override removes only truly dangerous filesystem characters while
    preserving all Unicode letters, marks, digits, dots, hyphens, and underscores.
    """

    def get_valid_name(self, name):
        s = str(name).strip().replace(' ', '_')
        # Remove only filesystem-unsafe characters (null bytes, control chars, path separators, etc.)
        # Preserves all Unicode letters AND combining marks (Myanmar vowel signs, tone marks)
        s = re.sub(r'[\x00-\x1f<>:"/\\|?*]', '', s)
        # Remove leading/trailing dots and spaces (Windows safety)
        s = s.strip('. ')
        return s or 'unnamed'
