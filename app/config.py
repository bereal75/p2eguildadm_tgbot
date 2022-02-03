import os
from pydantic import BaseSettings



class Settings(BaseSettings):
    tg_api_key: str
    guild_name: str
    p2eguildadm_api_host: str
    p2eguildadm_api_port: str

    class Config:
        env_file = ".env"


settings = Settings()