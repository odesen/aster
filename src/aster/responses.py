from fastapi.responses import JSONResponse

from aster.schemas import ORJSONModel


class ORJSONModelJSONResponse(JSONResponse):
    def render(self, content: ORJSONModel) -> bytes:
        return content.json().encode()
