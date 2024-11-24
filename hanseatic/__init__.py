from dataclasses import dataclass
from datetime import datetime
from typing import Literal, List

import pandas
from bs4 import BeautifulSoup, Tag


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


class HanseaticTransactionLoader:
    @staticmethod
    def load_transactions_from_html(file_name: str) -> pandas.DataFrame:

        with open(file_name) as fp:
            soup = BeautifulSoup(fp, 'html.parser')

        transactions: List[TransactionData] = []
        transactions_by_month = [e.parent for e in soup.find_all(attrs={"data-test-id": "accounting-month"})]
        for transaction_month in transactions_by_month:
            for transaction in transaction_month.find_all("div", recursive=False):
                transaction: Tag
                transaction_type_tag = transaction.find("h6")
                receiver_tag = transaction_type_tag.next_sibling
                reason_tag = receiver_tag.next_sibling
                date_tag = reason_tag.next_sibling
                amount_tag = transaction.find(attrs={"data-test-id": "transaction-amount"})
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
