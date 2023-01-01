# openbank-transactions-to-hibiscus
Ein Python-Skript, um Openbank Transaction Statements in deutscher Sprache für den CSV-Import in Hibiscus aufzubereiten

## E-V-A oder Hau-Zu

1. Hol dir deinen Kontoauszug aus dem Openbank-Kundenportal.  
   Klicke hierzu auf deiner Transaktionsübersicht oben rechts den Download-Knopf und exportiere in eine "Excel-Datei".
2. Starte dieses Skript mit `pipenv run python3 main.py`.
3. Gebe den Pfad zu deinem heruntergeladenen Kontoauszug ein (Copy-Paste funktioniert).
4. Du erhältst ein CSV-Dokument, welches du in Hibiscus mit den folgenden Einstellungen einlesen kannst:  

| Spalte |      Zweck       |
|:------:|:----------------:|
|   1    |      Datum       |
|   2    |      Valuta      |
|   3    | Verwendungszweck |
|   4    |      Betrag      |
|   5    |      Saldo       |
|   6    |    Gegenkonto    |

## Disclaimer

Ich habe das Skript ausschließlich unter Linux mit Python 3.10 getestet.
Pipenv muss separat installiert werden (im einfachsten Fall mit `pip install pipenv`).

Ich übernehme keine Haftung für die entstandenen Daten!
