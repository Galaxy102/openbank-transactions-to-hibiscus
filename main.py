import os.path
from typing import Type

from hibiscus import HibiscusFormatter
from loaders import TransactionLoader


def _guess_loader_from_filename(file_name: str) -> Type[TransactionLoader] | None:
    fname = os.path.basename(file_name)

    Loader = None

    if fname.startswith("Kontotransaktionen"):
        from loaders.openbank import OpenbankTransactionLoader as Loader
    elif fname.startswith("output"):
        from loaders.menuebestellung import MenuebestellungTransactionLoader as Loader
    elif fname.startswith("activity"):
        from loaders.amex import AmexTransactionLoader as Loader
    elif fname.startswith("Meine Hanseatic Bank"):
        from loaders.hanseatic import HanseaticTransactionLoader as Loader

    return Loader


def _get_loader_from_shortcode(shortcode: str) -> Type[TransactionLoader] | None:
    Loader = None
    match shortcode.lower():
        case "a":
            from loaders.amex import AmexTransactionLoader as Loader
        case "h":
            from loaders.hanseatic import HanseaticTransactionLoader as Loader
        case "m":
            from loaders.menuebestellung import MenuebestellungTransactionLoader as Loader
        case "o":
            from loaders.openbank import OpenbankTransactionLoader as Loader
    return Loader


if __name__ == '__main__':
    # Frage Dateinamen zum Kontoauszug im "Excel"-Format ab
    in_file_name = input("Pfad zum Kontoauszug: ")
    out_file_name = in_file_name + ".csv"

    Loader = _guess_loader_from_filename(in_file_name)
    if not Loader:
        print("Could not detect loader to use")
        Loader = _get_loader_from_shortcode(input("[A]mex [H]anseatic [M]enuebestellung [O]penbank: "))

    data_frame = Loader.load_transactions_from_file(file_name=in_file_name)

    # Ausgabe zur Kontrolle
    print(data_frame.to_string())

    # Ausgabe als CSV in einem Hibiscus-lesbaren Format
    csv_records = HibiscusFormatter.format_data_frame(data_frame=data_frame)
    with open(out_file_name, "w") as out_file:
        out_file.write(csv_records)

    print(f"{len(data_frame)} Umsätze nach {out_file_name} geschrieben.")

else:
    print("This script is intended to run as main.")
