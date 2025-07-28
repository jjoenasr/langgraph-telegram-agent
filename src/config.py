from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
	app_name: str = 'Awesome API'
	app_version: str = '0.1.0'
	app_description: str = 'Awesome API for awesome things'
	google_api_key: str
	telegram_bot_token: str
	telegram_bot_name: str
	slack_bot_token: str
	slack_team_id: str
	together_api_key: str
	notion_api_token: str
	router_messages: int = 5
	langsmith_api_key: str
	langsmith_tracing: bool = True

	model_config = SettingsConfigDict(env_file=".env")

settings = Settings()