from pydantic import BaseSettings


class Settings(BaseSettings):
    companies_list: str
    minio_host: str
    minio_port: str
    minio_access_key: str
    minio_secret_key: str

    # base_proxy: str

    class Config:
        env_file = r"C:\Users\login\Desktop\zakupki-gov-ru-parser-master\.env"
        # env_file_encoding = "utf-8"


settings = Settings()
