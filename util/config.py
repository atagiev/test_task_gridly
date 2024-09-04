import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    google_api_token = os.environ.get('GOOGLE_API_TOKEN')
    google_spreadsheet_id = os.environ.get('GOOGLE_SPREADSHEET_ID')
    table_names = os.environ.get('TABLE_NAMES', '')

    gridly_database_id = os.environ.get('GRIDLY_DATABASE_ID')
    gridly_api_token = os.environ.get('GRIDLY_API_TOKEN')

    @property
    def tables_to_sync(self) -> list[str]:
        return self.table_names.split(',')


config = Config()
