from pydantic import SecretStr
from pydantic_settings import  BaseSettings, SettingsConfigDict

class Setting(BaseSettings):
    data_url: str
    redis_url: str
    bot_token: SecretStr
    model_config = SettingsConfigDict(env_file='database/.env', env_file_encoding='utf-8')

config = Setting()