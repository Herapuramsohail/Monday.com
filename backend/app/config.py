import os

class Settings:
    APP_NAME: str = "Monday.com AI Business Intelligence Agent"
    DEBUG: bool = True
    
    MONDAY_API_TOKEN: str = os.getenv("MONDAY_API_TOKEN", "")
    MONDAY_DEAL_BOARD_ID: str = os.getenv("MONDAY_DEAL_BOARD_ID", "")
    MONDAY_WORK_BOARD_ID: str = os.getenv("MONDAY_WORK_BOARD_ID", "")
    MONDAY_API_URL: str = "https://api.monday.com/v2"
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    DEAL_FUNNEL_CSV: str = os.path.join(DATA_DIR, "deal_funnel.csv")
    WORK_ORDER_CSV: str = os.path.join(DATA_DIR, "work_order_tracker.csv")

settings = Settings()
