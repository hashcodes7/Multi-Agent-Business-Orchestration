We will dynamically load env file .prod or .dev using   
`python (filename) -prod` or `python (filename) -dev`

### Make A dynamic loader file
``` python
import sys
from pydantic_settings import BaseSettings, SettingsConfigDict
k
class Settings(BaseSettings):
    APP_ENV: str = "dev"
    ECOMMERCE_API_BASE_URL: str = "https://fakestoreapi.com"
    model_config = SettingsConfigDict(extra="ignore")

def setenv() -> Settings:
    # Step 1: if -prod flag is passed
    if "-prod" in sys.argv:
        env_file = ".env.prod"
    # Step 2: Default to development environment
    else:
        env_file = ".env.dev"
    # Step 3: Load and return configuration
    settings = Settings(_env_file=env_file)
    return settings
 
```

#### What we are doing here
- everytime app loads it loads the setting using setenv. 
- setenv method returns setting object (implemented above as a class) and sets the env file variable by detecting the flag
- The flag detection happens using `sys.argv`
- so sys.argv gets parsed as a prod or dev file, then makes a Settings object using the env file mentioned, returns the settings object, which goes back in main method.


for this we initialize this setting in main method of root file
``` python
def main():
    settings = get_settings()
```

finally we implement the env files as `.env.dev` or `.env.prod`
``` python
APP_ENV=dev
ECOMMERCE_API_BASE_URL=https://fakestoreapi.com
```

### Conclusion
Now We will just change the environment using flag
##### For adding/removing environment variable
We will just add the field in the setting class and add the variable in the .env file


