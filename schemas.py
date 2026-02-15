from pydantic import BaseModel, EmailStr


class CompanyBase(BaseModel):
    name: str
    email: EmailStr
    website: str


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    pass


class CompanyOut(CompanyBase):
    id: int

    class Config:
        from_attributes = True