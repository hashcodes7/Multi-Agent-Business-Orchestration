We will now run the python enterprise way where environment variable of OS supplies the env file. 

Here we will first create a new environment variable in os called `MABOP_ENV` (name changable)
- run command to set it as os environment ` $env:MABOP_ENV = "dev" `
- run the application `python run.py`

Settings in environment selector file `config.py`

``` python
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_ENV = os.getenv("MABOP_ENV", "dev")
ENV_FILE = f".env.{APP_ENV}"

class Settings(BaseSettings):
    APP_ENV: str = APP_ENV
    ECOMMERCE_API_BASE_URL: str = "https://fakestoreapi.com"
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore"
    )
    
def setenv() -> Settings:
    return Settings()
```

