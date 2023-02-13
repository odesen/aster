from fastapi import Response


class AsterResponse(Response):
    media_type = "application/json"
