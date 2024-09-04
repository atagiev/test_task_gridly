from integrations.google_sheets import GoogleSheets
from integrations.grigly.gridly_database import GridlyDatabase
from util.config import config
from util.logger import logger
from util.stats import Stats
from util.table_row import TableRow


def main():
    google_sheets = GoogleSheets(config.google_spreadsheet_id, config.google_api_token)

    gridly_database = GridlyDatabase(token=config.gridly_api_token, database_id=config.gridly_database_id)

    tables = config.tables_to_sync

    assert all(table in google_sheets.table_names for table in tables), 'Some tables not found in Google Sheets'

    stats = Stats()

    for table in tables:
        logger.info(f'Processing table {table}')

        gridly_table = gridly_database.get_table(grid_name=table)
        if gridly_table is None:
            logger.error(f'Table {table} not found in Gridly')
            continue

        sheet_data_google = google_sheets.get_sheet_data(table)

        iterator = iter(sheet_data_google)
        keys = next(iterator)

        for row_data in iterator:
            row = TableRow(keys, row_data)

            gridly_row = gridly_table.get_row_by_key(row.primary_key)
            if gridly_row is None:
                stats.add_row(table)
                gridly_table.create_row(row)
            elif row != gridly_row:
                stats.update_row(table)
                gridly_table.update_row(row)

    stats.display_stats()


if __name__ == '__main__':
    main()
