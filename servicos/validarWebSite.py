import re

class ValidarWebSite:
    def is_valid_website(url):
        pattern = r".*\.(com|br)$"
        if re.match(pattern, url) and "whatsapp.com" not in url.lower():
            return True
        return False