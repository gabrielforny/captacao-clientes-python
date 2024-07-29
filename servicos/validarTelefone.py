import re

class ValidarTelefone:
    def is_valid_phone(phone):
        pattern = r"\(\d{2}\) \d{4,5}-\d{4}"
        return re.match(pattern, phone) is not None