To start, run the command `pip install -r requirements.txt` and then `python main.py`.

The application expects the following environment variables (can be set in the .env file at the root of the repository):

`GOOGLE_API_TOKEN` - token to access Google Sheets

`GOOGLE_SPREADSHEET_ID` - table ID in Google Sheets

`TABLE_NAMES` - names of tables to be synchronized, separated by comma.

`GRIDLY_DATABASE_ID` - database ID in gridly service

`GRIDLY_API_TOKEN` - Gridly access token.


