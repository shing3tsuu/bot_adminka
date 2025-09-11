from pydantic import BaseModel, Field


class UserRequestDTO(BaseModel):
    tg_id: int
    tg_username: str
    surname: Field(..., min_length=2, max_length=30)
    name: Field(..., min_length=2, max_length=30)
    patronymic: Field(..., min_length=2, max_length=30)
    number: Field(..., min_length=11, max_length=15)
    is_admin: bool = Field(..., default=False)

class UserDTO(UserRequestDTO):
    id: int

class PostRequestDTO(BaseModel):
    name: Field(..., min_length=2, max_length=100)
    text: Field(..., min_length=2, max_length=1000)
    image_link: str | None
    is_checked: bool = Field(..., default=False)

    sender_id: int

class PostDTO(PostRequestDTO):
    id: int