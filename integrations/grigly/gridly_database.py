from functools import cached_property

from integrations.grigly.gridly_table import GridlyTable
from integrations.integration_utils.http_client import HttpClient
from integrations.integration_utils.sheet_info import TableInfo
from util.constants import Constants
from util.logger import logger


class GridlyDatabase(HttpClient):
    def __init__(self, token: str, database_id: str):
        self._token = token
        self._base_url = Constants.GRIDLY_API_URL
        self._database_id = database_id
        super().__init__(self._base_url, ('ApiKey', token))

    @cached_property
    def database_grids(self) -> list[TableInfo]:
        logger.info(f'Collecting tables for database {self._database_id}')
        tables = self.get('grids', params={'dbId': self._database_id})
        if isinstance(tables, dict) and (error := tables.get('error')):
            logger.error(f'No tables found for database {self._database_id}, error {error}')
            return []

        tables_info = [TableInfo(name=table['name'], sheet_id=table['id']) for table in tables]

        logger.info(f'Collected tables for database {self._database_id}: {tables_info}')

        return tables_info

    def _get_view_id(self, view_name: str, grid_id: str) -> str | None:
        views = self.get('views', params={'gridId': grid_id})
        if views is None:
            logger.error(f'No views found for grid {grid_id}')
            return

        views_info = [TableInfo(name=view['name'], sheet_id=view['id']) for view in views]

        logger.info(f'Collected views for grid {grid_id}: {views_info}')

        filtered_views = list(filter(lambda view: view.name == view_name, views_info))
        assert filtered_views, f'View {view_name} not found among {views_info}'

        view_id = filtered_views[0].sheet_id
        return view_id

    def get_table(self, grid_name: str, view_name='Default view') -> GridlyTable | None:
        if grid_name not in [grid.name for grid in self.database_grids]:
            logger.error(f'Table {grid_name} not found in gridly')
            return None
        filtered_grids = list(filter(lambda table: table.name == grid_name, self.database_grids))
        assert filtered_grids, f'Table {grid_name} not found in gridly'
        grid_id = filtered_grids[0].sheet_id
        view_id = self._get_view_id(view_name, grid_id)
        return GridlyTable(token=self._token, view_id=view_id, grid_id=grid_id)
