from pydantic import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    postgres_password: str
    database_name: str
    postgres_user: str
    development_mode: str


    class Config:
        env_file = ".env"


settings = Settings()
