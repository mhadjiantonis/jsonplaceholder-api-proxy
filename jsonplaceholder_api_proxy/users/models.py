from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


class _UserBase(BaseModel):
    class Address(BaseModel):
        class Geo(BaseModel):
            lattitude: Annotated[float, Field(alias="lat", ge=-90, le=90)]
            longitude: Annotated[float, Field(alias="lng", ge=-180, le=180)]

        street: str
        suite: str
        city: str
        zipcode: str
        geo: Geo

    class Company(BaseModel):
        name: str
        catch_phrase: Annotated[str, Field(alias="catchPhrase")]
        business_slogan: Annotated[str, Field(alias="bs")]

    name: str
    username: str
    email: EmailStr
    phone: str
    address: Address
    company: Company


class UserRead(_UserBase):
    id: Annotated[int, Field(gt=0)]


class UserCreate(_UserBase):
    pass
