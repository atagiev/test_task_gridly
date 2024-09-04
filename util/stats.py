from collections import defaultdict

from util.logger import logger


class Stats:
    """
    Count statistics of added and updater rows in gridly
    """
    def __init__(self):
        self._processed_tables = defaultdict(lambda: defaultdict(int))

    def add_row(self, table: str):
        self._processed_tables[table]['Added'] += 1

    def update_row(self, table: str):
        self._processed_tables[table]['Updated'] += 1

    def display_stats(self):
        logger.info('Stats:')
        for table in self._processed_tables:
            logger.info(f'\tTable {table}:')
            for key, value in self._processed_tables[table].items():
                logger.info(f'\t\t{key}: {value}')
