"""
Command line interface for calculating present value of options using data from an xlsx file.
"""
import csv
import json
import botocore
import sys
import logging
import boto3
import click
import click_log
from collections import namedtuple
from datetime import datetime
from scipy.stats import norm
import numpy
from options_price.file_reader import FileReader

"""
Display logs in console and exports them to a file.
"""

logging.basicConfig(filename="options_price.txt",
                    level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S',
                    filemode='w')

console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


class OptionsPricingError(Exception):
    """
    Custom exception used by the options price CLI.
    """

class OptionsPricing:
    """
    Performs options pricing with market data from a xlsx file.
    """

    User = namedtuple('Date', 'dictionary price errors')
    OptionsPricingResult = namedtuple('OptionsPricingResult', 'price success message')

    def __init__(self, filename):
        """
        Initialises a new instance of the OptionsPricing class.
        :param filename: xslx file to read data from.
        :param profile_name: AWS named profile.
        """
        self.file_reader = FileReader(filename)
        self.volatility, self.market_data = self.file_reader._read_file()

    def _set_formula_values(self):
        self.risk_free_continuous_compoud = numpy.log(1+self.market_data['Daily Risk Free Rate'][0])
        self.ln_Futures_Strike = numpy.log(self.market_data['Future Price'][0]/self.market_data['Strike'][0])
        self.e_continuous = numpy.exp(-self.market_data['Daily Risk Free Rate'][0] * (self.market_data['Time to Expire'][0] + 2/52))
        
        self.d1_numerator = (self.ln_Futures_Strike + ((self.volatility ** 2)) * (self.market_data['Time to Expire'][0] / 2))
        self.d1_denominator = self.volatility * (self.market_data['Time to Expire'][0] ** (1/2))
        self.d1 = float(self.d1_numerator) / float(self.d1_denominator)
        self.d2 = self.d1 - self.volatility * self.market_data['Time to Expire'][0] ** (1/2)
        self.norm_d1 = norm.cdf(self.d1)
        self.norm_d2 = norm.cdf(self.d2)
        self.discount_factor = numpy.exp(-self.risk_free_continuous_compoud * (self.market_data['Time to Expire'][0] + 2/52))
    
    def _calculate_call_present_value(self):
        self.call_present_value = self.discount_factor * (self.market_data['Future Price'][0] * self.norm_d1 - self.market_data['Strike'][0] * self.norm_d2)
        return self.call_present_value

    def _calculate_put_present_value(self):
        self.put_present_value = self.discount_factor * (self.market_data['Strike'][0] * self.norm_d2 - self.market_data['Future Price'][0] * self.norm_d1) 
        return self.put_present_value
    
    def run(self):
        """
        Runs the options price script
        """

        logger.info('Start processing...')

        self._set_formula_values()
        self._calculate_call_present_value()

        logger.info('Done.')


@click.command()
@click.argument('filename',
                type=click.Path(exists=True))

@click_log.simple_verbosity_option(logger)

def main(filename):
    """
    CLI application to calculate present value of options using market data provided in a xlsx file.
    """
    try:
        
        app = OptionsPricing(filename=filename)
        app.run()
    except Exception as ex:
        logger.critical(str(ex))
        sys.exit(1)


if __name__ == '__main__':
    main()