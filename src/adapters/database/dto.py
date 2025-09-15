from pydantic import BaseModel, Field
from datetime import datetime


class UserRequestDTO(BaseModel):
    tg_id: int # tg_id of user
    tg_username: str # name from telegram user profile
    surname: str | None # surname of user
    name: str | None # name of user
    patronymic: str | None # patronymic of user
    number: str | None # telephone number of user
    is_admin: bool # is user admin or not

class UserDTO(UserRequestDTO):
    id: int

class PostRequestDTO(BaseModel):
    name: str # name of post
    text: str # content (text) of post
    media_link: str | None # link to image of post (if exists), the image itself is stored in memory
    media_type: str | None # type of media (image, video)
    is_publish_now: bool # is post published now or not (after moderation)
    publish_date: datetime | None # date of publishing post (if user choose publish then)
    is_checked: bool # is post moderated by admin or not
    is_paid: bool # is post paid or not
    payment_id: str | None = None
    is_published: bool = False # is post published or not

    sender_id: int # id of user who sent post

class PostDTO(PostRequestDTO):
    id: int
