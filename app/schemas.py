import pydantic
from typing import Optional
from pydantic import BaseModel



class Person(BaseModel):
    personid: int
    firstname: str
    lastname: str
    tgusername: Optional[str]


class Wallet(BaseModel):
    walletid: int
    walletaddress: str
    alias: str
    walletownerid: int    

