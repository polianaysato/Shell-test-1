"""
Command line interface for calculating present value of options using data from an xlsx file.
"""

from datetime import datetime
from scipy.stats import norm
import numpy
from file_reader import FileReader

"""
Display logs in console and exports them to a file.
"""


class OptionsPricingError(Exception):
    """
    Custom exception used by the options price CLI.
    """

class OptionsPricing:
    """
    Performs options pricing with market data from a xlsx file.
    """

    def __init__(self, filename):
        """
        Initialises a new instance of the OptionsPricing class.
        :param filename: xslx file to read data from.
        :param profile_name: AWS named profile.
        """
        self.file_reader = FileReader(filename)
        self.volatility, self.market_data = self.file_reader._read_file()
        self.formula_values = self._set_formula_values()

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
        formula_values = {
            "risk_free_continuous_compound": self.risk_free_continuous_compoud,
            "ln_Futures_Strike": self.ln_Futures_Strike,
            "e_continuous": self.e_continuous,
            "norm_d1": norm.cdf(self.d1),
            "norm_d2": norm.cdf(self.d2),
            "discount_factor": self.discount_factor
        }
        return formula_values
    
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
        if self.market_data['Type'] == 'Call':
            return self._calculate_call_present_value()
        else:
            return self._calculate_put_present_value()