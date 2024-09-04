import json
from functools import cached_property

from integrations.integration_utils.http_client import HttpClient
from util.constants import Constants
from util.logger import logger
from util.table_row import TableRow


class GridlyTable(HttpClient):
    def __init__(self, token: str, view_id: str, grid_id: str):
        self._token = token
        self._base_url = Constants.GRIDLY_API_URL
        self._view_id = view_id
        self._grid_id = grid_id
        super().__init__(self._base_url, ('ApiKey', token))

    def get_row_by_key(self, primary_key, primary_key_name: str = 'Record ID'):
        query = {'_recordId': {"=": primary_key}}
        query_string = json.dumps(query)

        result = self.get(f'views/{self._view_id}/records', params={'query': query_string})

        if len(result) == 0:
            return None

        result = result[0]

        keys = [primary_key_name] + [self.column_id_to_name[cell['columnId']] for cell in result['cells']]
        data = [result['id']] + [cell['value'] for cell in result['cells']]

        row = TableRow(keys=keys, data=data)
        return row

    @cached_property
    def table_columns(self):
        response = self.get(f'grids/{self._grid_id}')
        columns = response.get('columns', [])
        return columns

    @cached_property
    def column_name_to_id(self):

        columns_dict = {}

        for column in self.table_columns:
            columns_dict[column['name']] = column['id']

        return columns_dict

    @cached_property
    def column_id_to_name(self):
        columns_dict = {}

        for column in self.table_columns:
            columns_dict[column['id']] = column['name']

        return columns_dict

    def _prepare_row_request(self, row: TableRow) -> str:
        data = {
            'id': row.primary_key,
            'cells': [],
        }

        for key, value in row.to_dict().items():
            if (column_id := self.column_name_to_id.get(key)) is not None:
                data['cells'].append({
                    "columnId": column_id,
                    "value": value
                })
            else:
                logger.warning(f'Unknown column {key}')
        return json.dumps([data])

    def create_row(self, row: TableRow):
        self.post(f'views/{self._view_id}/records', data=self._prepare_row_request(row),
                  headers={'Content-Type': 'application/json'})

    def update_row(self, row: TableRow):
        self.patch(f'views/{self._view_id}/records', data=self._prepare_row_request(row),
                   headers={'Content-Type': 'application/json'})
