import _pydatetime
import datetime
from dataclasses import dataclass
from enum import StrEnum
from typing import Generator

import pandas

from . import TransactionLoader


class ParqetTransactionHeaderFields(StrEnum):
    DATETIME = "datetime"
    DATE = "date"
    AMOUNT = "amount"
    ASSETTYPE = "assettype"
    HOLDINGNAME = "holdingname"
    WKN = "wkn"
    IDENTIFIER = "identifier"
    PRICE = "price"
    SHARES = "shares"
    TAX = "tax"
    NOTES = "notes"
    FEE = "fee"
    TYPE = "type"

class ParqetTransactionType(StrEnum):
    TRANSFER_CASH_IN = "Einzahlung"
    TRANSFER_CASH_OUT = "Auszahlung"
    TRANSFER_ASSET_IN = "Einlieferung"
    TRANSFER_ASSET_OUT = "Auslieferung"
    BUY = "Kauf"
    SELL = "Verkauf"
    AUX_TAX = "Steuern"
    AUX_FEE = "Gebühr"


@dataclass
class TransactionDataAccount:
    date: _pydatetime.date
    amount: float
    vzw: str
    type: str

@dataclass
class TransactionDataOrder:
    date: _pydatetime.date
    holding_name: str
    isin: str
    wkn: str
    transaction_type: ParqetTransactionType
    shares: float
    price: float
    amount: float
    tax: float
    fee: float

class ParqetTransactionLoader(TransactionLoader):

    @staticmethod
    def __get_transaction_type(transaction_type: str, asset_type: str) -> ParqetTransactionType:
        match asset_type:
            case "Cash":
                match transaction_type:
                    case "TransferIn":
                        return ParqetTransactionType.TRANSFER_CASH_IN
                    case "TransferOut":
                        return ParqetTransactionType.TRANSFER_CASH_OUT
                raise ValueError(f"Unbekannter Cash-Transaktionstyp: {transaction_type}")
            case "Security":
                match transaction_type:
                    case "TransferIn":
                        return ParqetTransactionType.TRANSFER_ASSET_IN
                    case "TransferOut":
                        return ParqetTransactionType.TRANSFER_ASSET_OUT
                    case "Buy":
                        return ParqetTransactionType.BUY
                    case "Sell":
                        return ParqetTransactionType.SELL
                raise ValueError(f"Unbekannter Security-Transaktionstyp: {transaction_type}")
            case _:
                raise ValueError(f"Unbekannter Asset-Typ: {asset_type}")

    @staticmethod
    def __make_vzw(transaction_type: ParqetTransactionType, holding_name: str, wkn: str, isin: str, notes: str, price: float, shares: float, aux_transaction_type: ParqetTransactionType | None = None) -> str:
        result = ""
        if aux_transaction_type:
            result += f"{aux_transaction_type} zu "
        match transaction_type:
            case ParqetTransactionType.TRANSFER_CASH_IN:
               result += f"{transaction_type}: {notes}"
            case ParqetTransactionType.TRANSFER_CASH_OUT:
                result += f"{transaction_type}: {notes}"
            case ParqetTransactionType.BUY:
                result += f"{transaction_type}: {holding_name} ({wkn}, {isin})\n{shares:.4f}x {price:.4f} €"
            case ParqetTransactionType.SELL:
                result += f"{transaction_type}: {holding_name} ({wkn}, {isin})\n{shares:.4f}x {price:.4f} €"
            case _:
                raise ValueError(f"Unbekannter Transaktionstyp: {transaction_type}")

        return result


    @staticmethod
    def __map_and_inject_entries_for_account(data: pandas.DataFrame) -> Generator[TransactionDataAccount]:
        for _, row in data.iterrows():
            transaction_type = ParqetTransactionLoader.__get_transaction_type(transaction_type=row[ParqetTransactionHeaderFields.TYPE], asset_type=row[ParqetTransactionHeaderFields.ASSETTYPE])
            if transaction_type in [ParqetTransactionType.TRANSFER_ASSET_OUT, ParqetTransactionType.TRANSFER_ASSET_IN]:
                # These transactions do not occur on the current account
                continue
            yield TransactionDataAccount(
                date=row[ParqetTransactionHeaderFields.DATE],
                amount=row[ParqetTransactionHeaderFields.AMOUNT] if transaction_type in [ParqetTransactionType.TRANSFER_CASH_IN, ParqetTransactionType.SELL] else -row["amount"],
                vzw=ParqetTransactionLoader.__make_vzw(
                    transaction_type=transaction_type,
                    holding_name=row[ParqetTransactionHeaderFields.HOLDINGNAME],
                    wkn=row[ParqetTransactionHeaderFields.WKN],
                    isin=row[ParqetTransactionHeaderFields.IDENTIFIER],
                    price=row[ParqetTransactionHeaderFields.PRICE],
                    shares=row[ParqetTransactionHeaderFields.SHARES],
                    notes=row[ParqetTransactionHeaderFields.NOTES],
                ),
                type=transaction_type,
            )
            if row["tax"]:
                yield TransactionDataAccount(
                    date=row[ParqetTransactionHeaderFields.DATE],
                    amount=-row[ParqetTransactionHeaderFields.TAX],
                    vzw=ParqetTransactionLoader.__make_vzw(
                        transaction_type=transaction_type,
                        holding_name=row[ParqetTransactionHeaderFields.HOLDINGNAME],
                        wkn=row[ParqetTransactionHeaderFields.WKN],
                        isin=row[ParqetTransactionHeaderFields.IDENTIFIER],
                        price=row[ParqetTransactionHeaderFields.PRICE],
                        shares=row[ParqetTransactionHeaderFields.SHARES],
                        notes=row[ParqetTransactionHeaderFields.NOTES],
                        aux_transaction_type=ParqetTransactionType.AUX_TAX,
                    ),
                    type=transaction_type,
                )
            if row["fee"]:
                yield TransactionDataAccount(
                    date=row[ParqetTransactionHeaderFields.DATE],
                    amount=-row[ParqetTransactionHeaderFields.FEE],
                    vzw=ParqetTransactionLoader.__make_vzw(
                        transaction_type=transaction_type,
                        holding_name=row[ParqetTransactionHeaderFields.HOLDINGNAME],
                        wkn=row[ParqetTransactionHeaderFields.WKN],
                        isin=row[ParqetTransactionHeaderFields.IDENTIFIER],
                        price=row[ParqetTransactionHeaderFields.PRICE],
                        shares=row[ParqetTransactionHeaderFields.SHARES],
                        notes=row[ParqetTransactionHeaderFields.NOTES],
                        aux_transaction_type=ParqetTransactionType.AUX_FEE,
                    ),
                    type=transaction_type,
                )

    @staticmethod
    def __map_entries_for_orders(data: pandas.DataFrame) -> Generator[TransactionDataOrder]:
        for _, row in data.iterrows():
            transaction_type = ParqetTransactionLoader.__get_transaction_type(transaction_type=row[ParqetTransactionHeaderFields.TYPE], asset_type=row[ParqetTransactionHeaderFields.ASSETTYPE])
            if transaction_type in [ParqetTransactionType.TRANSFER_CASH_IN, ParqetTransactionType.TRANSFER_CASH_OUT]:
                # These transactions do not occur on the order book
                continue
            yield TransactionDataOrder(
                date=row[ParqetTransactionHeaderFields.DATE],
                holding_name=row[ParqetTransactionHeaderFields.HOLDINGNAME],
                isin=row[ParqetTransactionHeaderFields.IDENTIFIER],
                wkn=row[ParqetTransactionHeaderFields.WKN],
                transaction_type=transaction_type,
                shares=row[ParqetTransactionHeaderFields.SHARES],
                price=row[ParqetTransactionHeaderFields.PRICE],
                amount=row[ParqetTransactionHeaderFields.AMOUNT],
                tax=row[ParqetTransactionHeaderFields.TAX],
                fee=row[ParqetTransactionHeaderFields.FEE],
            )



    @staticmethod
    def load_transactions_from_file(file_name: str) -> list[pandas.DataFrame]:

        sheet: pandas.DataFrame = pandas.read_csv(file_name, sep=";", decimal=",")

        # Ausgabe muss umgedreht werden (neueste zuletzt)
        sheet = sheet[::-1]
        sheet[ParqetTransactionHeaderFields.DATE] = pandas.to_datetime(sheet[ParqetTransactionHeaderFields.DATE])

        result_account = pandas.DataFrame(list(ParqetTransactionLoader.__map_and_inject_entries_for_account(data=sheet)))
        result_orders = pandas.DataFrame(list(ParqetTransactionLoader.__map_entries_for_orders(data=sheet)))

        return [result_account, result_orders]
