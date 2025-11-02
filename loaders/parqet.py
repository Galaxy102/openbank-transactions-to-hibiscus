import pandas

from . import TransactionLoader


class ParqetTransactionHeaderFields:
    TYPE = "type"


_PARQET_DEPOTVIEWER_TYPE_RENAME_MAP = {
    "TransferOut": "Auslieferungen",
    "TransferIn": "Einlieferung",
    "Buy": "Kauf",
    "Sell": "Verkauf",
}


class ParqetTransactionLoader(TransactionLoader):
    @staticmethod
    def load_transactions_from_file(file_name: str) -> pandas.DataFrame:

        sheet: pandas.DataFrame = pandas.read_csv(file_name, sep=";", decimal=",")

        sheet[ParqetTransactionHeaderFields.TYPE] = sheet[ParqetTransactionHeaderFields.TYPE].apply(_PARQET_DEPOTVIEWER_TYPE_RENAME_MAP.get)

        # Ausgabe muss umgedreht werden (neueste zuletzt)
        sheet = sheet[::-1]
        return sheet
