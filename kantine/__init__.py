import pandas


class KantineTransactionHeaderFields:
    BON_NR = "Bericht-Nr."
    VALUTA = "Datum"
    VERWENDUNGSZWECK = "Beschreibung"
    BETRAG = "Betrag"
    GEGENKONTO = "Gegenkonto"


class KantineTransactionLoader:
    @staticmethod
    def load_transactions_from_csv(file_name: str) -> pandas.DataFrame:

        sheet: pandas.DataFrame = pandas.read_csv(file_name, sep=";", decimal=",")

        sheet[KantineTransactionHeaderFields.VALUTA] = pandas.to_datetime(
            sheet[KantineTransactionHeaderFields.VALUTA],
            dayfirst=True
        )

        sheet[KantineTransactionHeaderFields.GEGENKONTO] = "Robotron Kantine"

        # Ausgabe muss umgedreht werden (neueste zuletzt)
        sheet = sheet[::-1]
        return sheet
