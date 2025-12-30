from fastapi import Request

def parse_media(request: Request, media):
    base = str(request.base_url).rstrip("/")

    photos = []
    if getattr(media, "photos", None):
        photos = [f"{base}/{p}" for p in media.photos.split("|")]

    logo = f"{base}/{media.logo}" if getattr(media, "logo", None) else None

    return {
        "logo": logo,
        "photos": photos
    }

