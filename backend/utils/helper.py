import validators

def is_valid_url(url: str) -> bool:
    return validators.url(url)
