from pydantic_settings import BaseSettings


class PostgresConfig(BaseSettings):
    db_name: str = "example"
    db_user: str = "example"
    db_password: str = "example"
    db_host: str = "localhost"
    db_port: str = "5432"


pg_config = PostgresConfig()
