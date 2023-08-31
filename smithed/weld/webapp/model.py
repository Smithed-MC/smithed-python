from pydantic import BaseModel


class WebApp(BaseModel):
    class Footer(BaseModel):
        left: str
        right: str

    title: str
    conflicts: str
    intro: str
    warn: str
    fabric: str
    footer: Footer
