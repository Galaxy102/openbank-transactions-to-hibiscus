import abc

import pandas


class TransactionLoader(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def load_transactions_from_file(file_name: str) -> pandas.DataFrame:
        """
        Load transactions from file
        :param file_name: The file to load (e.g. CSV or HTML)
        :return: DataFrame with fields to use in Hibiscus. The DataFrame adheres to the following conventions:
        - Transactions are sorted oldest to newest (newest last)
        - Dates are parsed as dates
        - There is some kind of
            * Transaction Date
            * Transaction Sum (where positive is incoming and negative is outgoing)
            * Transaction Description
        - Additional fields are welcome:
            * Balance
            * Payment reference
        """
        pass
