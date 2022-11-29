from base64 import urlsafe_b64encode, urlsafe_b64decode

def base64UrlEncode(data):
    return urlsafe_b64encode(data.encode("utf-8")).rstrip(b'=').decode("utf-8")