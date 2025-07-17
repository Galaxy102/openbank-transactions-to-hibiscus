from enum import StrEnum

import pandas

from . import TransactionLoader


class N26TransactionHeaderFields(StrEnum):
    BOOKING = "Booking Date"
    VALUTA = "Value Date"
    GEGENKONTO = "Partner Name"
    GEGENKONTO_IBAN = "Partner Iban"
    TYP = "Type"
    VERWENDUNGSZWECK = "Payment Reference"
    BETRAG = "Amount (EUR)"


class N26TransactionLoader(TransactionLoader):
    @staticmethod
    def load_transactions_from_file(file_name: str) -> pandas.DataFrame:

        sheet: pandas.DataFrame = pandas.read_csv(file_name, sep=",", decimal=",", usecols=[x for x in N26TransactionHeaderFields])

        sheet[N26TransactionHeaderFields.BOOKING] = pandas.to_datetime(
            sheet[N26TransactionHeaderFields.BOOKING]
        )

        sheet[N26TransactionHeaderFields.VALUTA] = pandas.to_datetime(
            sheet[N26TransactionHeaderFields.VALUTA]
        )

        return sheet
