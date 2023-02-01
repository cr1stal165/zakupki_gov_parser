from pydantic import BaseSettings


class Settings(BaseSettings):
    companies_list: str

    # base_proxy: str

    class Config:
        env_file = r"C:\Users\login\Desktop\zakupki-gov-ru-parser-master\.env"
        # env_file_encoding = "utf-8"


settings = Settings()
