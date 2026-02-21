from typing import Annotated

from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.coordinate import Latitude, Longitude


class _UserBase(BaseModel):
    class Address(BaseModel):
        class Geo(BaseModel):
            lattitude: Annotated[Latitude, Field(alias="lat")]
            longitude: Annotated[Longitude, Field(alias="lng")]

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
