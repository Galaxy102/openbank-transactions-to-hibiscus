from dataclasses import dataclass
from datetime import datetime
from typing import Literal, List

import pandas
from bs4 import BeautifulSoup, Tag

from . import TransactionLoader


@dataclass
class TransactionData:
    transaction_type: Literal["Kartenumsatz", "Lastschrifteinzug"]
    receiver: str
    reason: str
    date: datetime
    amount: float


class HanseaticTransactionHeaderFields:
    BUCHUNGSART = "Buchungsart"
    VALUTA = "Wertstellungsdat"
    VERWENDUNGSZWECK = "Verwendungszweck"
    BETRAG = "Betrag"
    GEGENKONTO = "Gegenkonto"


class HanseaticTransactionLoader(TransactionLoader):
    @staticmethod
    def load_transactions_from_file(file_name: str) -> pandas.DataFrame:

        with open(file_name) as fp:
            soup = BeautifulSoup(fp, 'html.parser')

        transactions: List[TransactionData] = []
        transactions_by_month = [e.parent for e in soup.find_all(attrs={"data-test-id": "accounting-month"})]
        for transaction_month in transactions_by_month:
            for transaction in transaction_month.find_all("div", recursive=False):
                transaction: Tag
                transaction_type_tag = transaction.find("div", class_="h6")
                amount_tag = transaction.find(attrs={"data-test-id": "transaction-amount"}).find("span", attrs={"aria-hidden": "true"})
                details = transaction.find("div", class_="overflow-hidden")
                receiver_tag = details.contents[0].find("span", attrs={"aria-hidden": "true"})
                reason_tag = details.contents[1].find("span", attrs={"aria-hidden": "true"})
                date_tag = details.contents[2].find("span", attrs={"aria-hidden": "true"})
                data = TransactionData(
                    transaction_type=transaction_type_tag.text.strip(),
                    receiver=receiver_tag.text.strip(),
                    reason=reason_tag.text.strip(),
                    date=datetime.strptime(date_tag.text.strip(), "%d.%m.%Y"),
                    amount=float(amount_tag.text.strip().replace(".", "").replace(",", ".").split("\xa0")[0])
                )
                transactions.append(data)

        out = pandas.DataFrame(transactions)
        out = out.rename(columns={
            "transaction_type": HanseaticTransactionHeaderFields.BUCHUNGSART,
            "receiver": HanseaticTransactionHeaderFields.GEGENKONTO,
            "reason": HanseaticTransactionHeaderFields.VERWENDUNGSZWECK,
            "date": HanseaticTransactionHeaderFields.VALUTA,
            "amount": HanseaticTransactionHeaderFields.BETRAG
        })
        # Ausgabe muss umgedreht werden (neueste zuletzt)
        out = out[::-1]
        return out
