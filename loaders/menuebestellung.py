import pandas

from . import TransactionLoader


class KantineTransactionHeaderFields:
    BON_NR = "Bericht-Nr."
    VALUTA = "Datum"
    VERWENDUNGSZWECK = "Beschreibung"
    BETRAG = "Betrag"
    GEGENKONTO = "Gegenkonto"


class MenuebestellungTransactionLoader(TransactionLoader):
    @staticmethod
    def load_transactions_from_file(file_name: str) -> pandas.DataFrame:

        sheet: pandas.DataFrame = pandas.read_csv(file_name, sep=";", decimal=",")

        sheet[KantineTransactionHeaderFields.VALUTA] = pandas.to_datetime(
            sheet[KantineTransactionHeaderFields.VALUTA]
        )

        sheet[KantineTransactionHeaderFields.GEGENKONTO] = "Kantine"

        # Ausgabe muss umgedreht werden (neueste zuletzt)
        sheet = sheet[::-1]
        return sheet
