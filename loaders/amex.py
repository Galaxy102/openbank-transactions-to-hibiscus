from enum import StrEnum

import numpy
import pandas

from . import TransactionLoader


class AmexTransactionHeaderFields(StrEnum):
    VALUTA = "Datum"
    VERWENDUNGSZWECK = "Erscheint auf Ihrer Abrechnung als"
    BETRAG = "Betrag"
    E2E_ID = "Betreff"
    ADRESSE = "Adresse"


class AmexTransactionLoader(TransactionLoader):
    @staticmethod
    def load_transactions_from_file(file_name: str) -> pandas.DataFrame:

        sheet: pandas.DataFrame = pandas.read_csv(file_name, sep=",", decimal=",", usecols=[x for x in AmexTransactionHeaderFields])

        sheet[AmexTransactionHeaderFields.VALUTA] = pandas.to_datetime(
            sheet[AmexTransactionHeaderFields.VALUTA],
            dayfirst=True
        )

        # Beträge müssen invertiert werden
        sheet[AmexTransactionHeaderFields.BETRAG] *= -1

        # Adressen können Newlines enthalten
        sheet[AmexTransactionHeaderFields.ADRESSE] = sheet[AmexTransactionHeaderFields.ADRESSE].astype(dtype=str).apply(lambda x: x.replace("\n", " ").replace("\"", "") if x != "nan" else numpy.nan)

        # Betreff ist immer doppelt gequotet
        sheet[AmexTransactionHeaderFields.E2E_ID] = sheet[AmexTransactionHeaderFields.E2E_ID].astype(dtype=str).apply(lambda x: x.replace("'", ""))

        # Ausgabe muss umgedreht werden (neueste zuletzt)
        sheet = sheet[::-1]
        return sheet
