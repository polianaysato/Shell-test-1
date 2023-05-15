"""
Helper module for reading data from an Excel spreadsheet.
"""
import pandas as pd
import math


class FileReader:
    """
    Utilities methods for processing xlsx files.
    """
    SHEET_NAME = 'Volatility'
    SUMMARY_SHEET_NAME = 'Summary'
    MAX_NUM_DAILY_DATA_REFERENCE = 'B9'
    ALL = 'ALL'
    MAXIMUM_DAILY_DATA_PER_SHEET = 366

    def __init__(self, path):
        """
        Initialises a new instance of the file reader.
        :param path: Path of the spreadsheet containing data.
        """
        self.workbook = pd.read_excel(path, sheet_name=['Volatility', 'Summary'])

    def _read_file(self, sheet_name='Volatility'):
        """
        Reads data from an xls file.
        :param sheet_name: The name of the sheet to read from.
        :return: pandas data frame
        """
        self.volatility = self._calculate_volatility()
        self.mkt_data = self._get_market_data()
        self._cast_datetime_to_date()
        self._calculate_time_delta()

        return self.volatility, self.mkt_data

    def _calculate_volatility(self):
        """
        Calculates the volatility in annual basis.
        :return: float
        """

        self.workbook['Return'] = self.workbook['Volatility']['Price'].pct_change()
        self.std_deviation = self.workbook['Return'].std()
        self.std_deviation = self.std_deviation * math.sqrt(252)
        return self.std_deviation

    def _get_market_data(self):
        self.workbook['Summary']['Daily Risk Free Rate'] = self._calculate_compoud_daily_rate()
        self.market_data = self.workbook['Summary'].to_dict()
        return self.market_data

    def _calculate_compoud_daily_rate(self):
        self.daily_compoud_rate = (self.workbook['Summary']['Risk Free Rate'] / 365 + 1) ** 365 - 1
        return self.daily_compoud_rate

    def _cast_datetime_to_date(self):
        self.market_data['Expiry Date'][0] = self.market_data['Expiry Date'][0].date()
        self.market_data['Current Date'][0] = self.market_data['Current Date'][0].date()
        self.market_data['Prompt Date'][0] = self.market_data['Prompt Date'][0].date()

    def _calculate_time_delta(self):
        self.workbook['Summary']['Time to Expire'] = (self.market_data['Expiry Date'][0] - self.market_data['Current Date'][0]) 
        self.workbook['Summary']['Time to Prompt'] = (self.market_data['Prompt Date'][0] - self.market_data['Current Date'][0]) 
        self.workbook['Summary']['Time to Expire'] = self.workbook['Summary']['Time to Expire'].dt.days / 365
        self.workbook['Summary']['Time to Prompt'] = self.workbook['Summary']['Time to Prompt'].dt.days / 365
        self.mkt_data = self.workbook['Summary'].to_dict()
    