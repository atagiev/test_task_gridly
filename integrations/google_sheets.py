import csv
from functools import cached_property
from pathlib import Path
from typing import Iterator
from urllib.parse import urljoin

import requests

from integrations.integration_utils.http_client import HttpClient
from integrations.integration_utils.sheet_info import TableInfo
from util.constants import Constants
from util.logger import logger


class GoogleSheets(HttpClient):

    def __init__(self, spreadsheet_id: str, token: str = None):
        base_url = Constants.GOOGLE_API_SHEETS_BASE_URL
        self._spreadsheet_id = spreadsheet_id
        super().__init__(base_url, auth=('Bearer', token))

    @cached_property
    def _spreadsheet_tables(self) -> list[TableInfo] | None:
        logger.info(f'Collecting sheets for spreadsheet {self._spreadsheet_id}')
        spreadsheet_info = self.get(self._spreadsheet_id)
        if error := spreadsheet_info.get('error'):
            raise Exception(error)

        sheets = spreadsheet_info.get('sheets')
        if sheets is None:
            logger.error(f'No sheets info found for spreadsheet {self._spreadsheet_id}')
            return

        sheets_info = []
        for sheet in sheets:
            title = sheet['properties']['title']
            sheet_id = sheet['properties']['sheetId']
            sheets_info.append(TableInfo(name=title, sheet_id=sheet_id))

        logger.info(f'Collected sheets for spreadsheet {self._spreadsheet_id}: {sheets_info}')

        return sheets_info

    @cached_property
    def table_names(self) -> list[str]:
        """
        Get sheet names in the spreadsheet
        """
        if self._spreadsheet_tables is None:
            return []
        return [table.name for table in self._spreadsheet_tables]

    def _download_sheet(self, sheet_id: str) -> Path:
        temporary_dir = Path.cwd() / 'tmp'
        temporary_dir.mkdir(exist_ok=True)

        file_name = temporary_dir / f'{sheet_id}.csv'

        headers = {'Authorization': f'{self._auth[0]} {self._auth[1]}'} if self._auth else None
        response = requests.get(
            url=urljoin(Constants.GOOGLE_SHEETS_UI_BASE_URL,
                        f'd/{self._spreadsheet_id}/export?format=csv&gid={sheet_id}'),
            headers=headers)

        with open(file_name, 'wb') as out_file:
            out_file.write(response.content)

        return file_name

    def get_sheet_data(self, sheet_name: str) -> Iterator[list[str]]:
        """
        Get sheet contents as a list of rows
        :param sheet_name: name of the sheet
        :return: iterator of rows
        """
        sheet_id = list(filter(lambda x: x.name == sheet_name, self._spreadsheet_tables))[0].sheet_id
        sheet_file = self._download_sheet(sheet_id)
        with open(sheet_file, newline='', encoding='utf-8') as sheet_content:
            reader = csv.reader(sheet_content, delimiter=',', quotechar='|')
            yield from reader
