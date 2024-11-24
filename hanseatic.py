from hibiscus import HibiscusFormatter
from hanseatic import HanseaticTransactionLoader


if __name__ == '__main__':
    # Frage Dateinamen zum Kontoauszug im "Website, complete"-Format ab
    in_file_name = input("Pfad zum Kontoauszug: ")
    out_file_name = in_file_name + ".csv"

    data_frame = HanseaticTransactionLoader.load_transactions_from_html(file_name=in_file_name)

    # Ausgabe zur Kontrolle
    print(data_frame.to_string())

    # Ausgabe als CSV in einem Hibiscus-lesbaren Format
    csv_records = HibiscusFormatter.format_data_frame(data_frame=data_frame)
    with open(out_file_name, "w") as out_file:
        out_file.write(csv_records)

    print(f"{len(data_frame)} Umsätze nach {out_file_name} geschrieben.")

else:
    print("This script is intended to run as main.")
