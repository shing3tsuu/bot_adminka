from pydantic import BaseModel, Field


class UserRequestDTO(BaseModel):
    tg_id: int
    tg_username: str
    surname: str | None
    name: str | None
    patronymic: str | None
    number: str | None
    is_admin: bool

class UserDTO(UserRequestDTO):
    id: int

class PostRequestDTO(BaseModel):
    name: str
    text: str
    image_link: str | None
    is_checked: bool

    sender_id: int

class PostDTO(PostRequestDTO):
    id: int