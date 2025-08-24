import re

import pandas

from . import TransactionLoader


# Reguläre Ausdrücke zum Parsen des Feldes "Verwendungszweck"
class _OpenbankTransactionRegex:
    @classmethod
    def __init__(cls):
        cls.GEGENKONTO_UEBERWEISUNG = re.compile(
            r"ÜBERWEISUNG (?:VON|AN) ([?\w ]+)\.? VERWENDUNGSZWECK[\w /?:().,'+-]*"
        )

        # Charset aus
        # https://www.hettwer-beratung.de/sepa-spezialwissen/sepa-technische-anforderungen/sepa-verwendungszweck/
        _VERWENDUNGSZWECK_UEBERWEISUNG = re.compile(
            r"ÜBERWEISUNG (?:VON|AN) [?\w ]+\.? VERWENDUNGSZWECK ?([\w /?:().,'+-]*)"
        )
        _VERWENDUNGSZWECK_GELDAUTOMAT = re.compile(
            r"(VERFÜGUNG GELDAUTOMAT AM \d{4}-\d{2}-\d{2}), KARTENNUMMER: \d{16}, GEB[?Ü]HR: [\d,]+"
        )
        _VERWENDUNGSZWECK_KARTENZAHLUNG = re.compile(
            r"KAUF GETÄTIGT IN ([\w .,*']+) KARTEN : \d{16} AM \d{4}-\d{2}-\d{2}"
        )
        _VERWENDUNGSZWECK_ZINSEN = re.compile(
            r"^(ZINSEN|KEST|SOLZ)( [A-Z]{2}\d{2}[A-Z\d]{11,30})?$"
        )

        cls.VERWENDUNGSZWECK = re.compile(
            f"^(?:"
            f"{_VERWENDUNGSZWECK_UEBERWEISUNG.pattern}|"
            f"{_VERWENDUNGSZWECK_GELDAUTOMAT.pattern}|"
            f"{_VERWENDUNGSZWECK_KARTENZAHLUNG.pattern}|"
            f"{_VERWENDUNGSZWECK_ZINSEN.pattern}"
            f")$"
        )


OpenbankTransactionRegex = _OpenbankTransactionRegex()


class OpenbankTransactionHeaderFields:
    DATUM = "Transaktionsdat"
    VALUTA = "Wertstellungsdat"
    VERWENDUNGSZWECK = "Verwendungszweck"
    BETRAG = "Betrag"
    SALDO = "Saldo"

    CUSTOM_GEGENKONTO = "Gegenkonto"
    CUSTOM_HELPER = "Helper"


class OpenbankTransactionLoader(TransactionLoader):

    @staticmethod
    def load_transactions_from_file(file_name: str) -> pandas.DataFrame:
        # Die Excel-Datei ist eigentlich eine HTML-Datei
        sheet: pandas.DataFrame = pandas.read_excel(file_name, skiprows=15, header=0, thousands=".", decimal=",")
        # Die letzte Zeile wird fehlerhaft eingelesen
        sheet = sheet[[
            OpenbankTransactionHeaderFields.DATUM,
            OpenbankTransactionHeaderFields.VALUTA,
            OpenbankTransactionHeaderFields.VERWENDUNGSZWECK,
            OpenbankTransactionHeaderFields.BETRAG,
            OpenbankTransactionHeaderFields.SALDO,
        ]]
        # Parsen der Datumsfelder
        sheet[OpenbankTransactionHeaderFields.DATUM] = pandas.to_datetime(
            sheet[OpenbankTransactionHeaderFields.DATUM],
            format="%d%m%Y"
        )
        sheet[OpenbankTransactionHeaderFields.VALUTA] = pandas.to_datetime(
            sheet[OpenbankTransactionHeaderFields.VALUTA],
            format="%d%m%Y"
        )
        # Anlegen einer Hilfsdatenreihe
        sheet[OpenbankTransactionHeaderFields.CUSTOM_HELPER] = sheet[OpenbankTransactionHeaderFields.VERWENDUNGSZWECK]
        # Extraktion der Gegenkonten
        sheet[OpenbankTransactionHeaderFields.CUSTOM_GEGENKONTO] = \
            sheet[OpenbankTransactionHeaderFields.CUSTOM_HELPER].str.extract(
                OpenbankTransactionRegex.GEGENKONTO_UEBERWEISUNG,
                expand=True
            )

        # Extraktion der Verwendungszwecke
        vzw_series_frame: pandas.DataFrame = sheet[OpenbankTransactionHeaderFields.CUSTOM_HELPER].str.extract(
            OpenbankTransactionRegex.VERWENDUNGSZWECK,
            expand=False
        )
        vzw_series_collected = vzw_series_frame.pop(vzw_series_frame.keys()[0])
        while vzw_series_frame.shape[1]:
            combine_with = vzw_series_frame.pop(vzw_series_frame.keys()[0])
            vzw_series_collected = vzw_series_collected.combine_first(combine_with)
        sheet[OpenbankTransactionHeaderFields.VERWENDUNGSZWECK] = vzw_series_collected

        # Hilfsdatenreihe löschen
        sheet.pop(OpenbankTransactionHeaderFields.CUSTOM_HELPER)

        # Ausgabe muss umgedreht werden (neueste zuletzt)
        sheet = sheet[::-1]

        return sheet
