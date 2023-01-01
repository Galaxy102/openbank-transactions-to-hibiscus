import csv

import pandas

_DATE_FORMAT_HIBISCUS = "%d.%m.%y"


class HibiscusFormatter:
    @staticmethod
    def format_data_frame(data_frame: pandas.DataFrame) -> str:
        return data_frame.to_csv(
            sep=";",                            # Standard-Separator in Hibiscus
            index=False,                        # Header nicht drucken
            quoting=csv.QUOTE_NONNUMERIC,       # Anführungszeichen wo nötig
            date_format=_DATE_FORMAT_HIBISCUS   # Deutsches Datumsformat
        )
