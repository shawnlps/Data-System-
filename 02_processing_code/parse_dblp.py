import argparse
import csv
import gzip
import html
import xml.sax
from pathlib import Path


PUBLICATION_TYPES = {
    "article",
    "inproceedings",
    "proceedings",
    "book",
    "incollection",
    "phdthesis",
    "mastersthesis",
}

PUBLICATION_COLUMNS = [
    "pub_id",
    "pubkey",
    "pub_type",
    "title",
    "year",
    "journal",
    "booktitle",
    "pages",
    "volume",
    "number",
    "month",
    "publisher",
    "address",
    "isbn",
    "school",
    "chapter",
    "url",
    "ee",
    "crossref",
    "mdate",
    "publtype",
    "cdate",
]

SINGLE_VALUE_FIELDS = {
    "title",
    "year",
    "journal",
    "booktitle",
    "pages",
    "volume",
    "number",
    "month",
    "publisher",
    "address",
    "isbn",
    "school",
    "chapter",
    "url",
    "ee",
    "crossref",
}

TEXT_FIELDS = SINGLE_VALUE_FIELDS | {"author", "editor"}


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(html.unescape(value).split())


def parse_year(value: str) -> str:
    value = normalize_text(value)
    if value.isdigit():
        return value
    for token in value.split():
        digits = "".join(ch for ch in token if ch.isdigit())
        if len(digits) == 4:
            return digits
    return ""


def get_or_create_id(
    name: str,
    mapping: dict[str, int],
    writer: csv.writer,
    stats_key: str,
    stats: dict[str, int],
) -> int:
    existing = mapping.get(name)
    if existing is not None:
        return existing
    new_id = len(mapping) + 1
    mapping[name] = new_id
    writer.writerow([new_id, name])
    stats[stats_key] += 1
    return new_id


class CSVOutput:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.handles: list[object] = []

        self.author_writer = self._open_writer("authors.csv", ["author_id", "name"])
        self.editor_writer = self._open_writer("editors.csv", ["editor_id", "name"])
        self.publication_writer = self._open_writer("publications.csv", PUBLICATION_COLUMNS)
        self.authored_writer = self._open_writer("authored.csv", ["author_id", "pub_id", "author_order"])
        self.edited_writer = self._open_writer("edited.csv", ["editor_id", "pub_id", "editor_order"])

    def _open_writer(self, filename: str, header: list[str]) -> csv.writer:
        fh = (self.output_dir / filename).open("w", encoding="utf-8", newline="")
        self.handles.append(fh)
        writer = csv.writer(fh)
        writer.writerow(header)
        return writer

    def close(self) -> None:
        for handle in self.handles:
            handle.close()


class DBLPHandler(xml.sax.ContentHandler):
    def __init__(self, output: CSVOutput, max_records: int | None = None):
        super().__init__()
        self.output = output
        self.max_records = max_records
        self.author_map: dict[str, int] = {}
        self.editor_map: dict[str, int] = {}
        self.stats = {
            "publications": 0,
            "authors": 0,
            "editors": 0,
            "authored": 0,
            "edited": 0,
        }
        self.current_pub: dict[str, object] | None = None
        self.current_field: str | None = None
        self.current_text: list[str] = []
        self.pub_id = 0

    def startElement(self, name, attrs):
        if name in PUBLICATION_TYPES and self.current_pub is None:
            self.pub_id += 1
            self.current_pub = {
                "pub_id": self.pub_id,
                "pubkey": normalize_text(attrs.get("key", "")),
                "pub_type": name,
                "title": "",
                "year": "",
                "journal": "",
                "booktitle": "",
                "pages": "",
                "volume": "",
                "number": "",
                "month": "",
                "publisher": "",
                "address": "",
                "isbn": "",
                "school": "",
                "chapter": "",
                "url": "",
                "ee": "",
                "crossref": "",
                "mdate": normalize_text(attrs.get("mdate", "")),
                "publtype": normalize_text(attrs.get("publtype", "")),
                "cdate": normalize_text(attrs.get("cdate", "")),
                "authors": [],
                "editors": [],
            }
            return

        if self.current_pub is not None and name in TEXT_FIELDS:
            self.current_field = name
            self.current_text = []

    def characters(self, content):
        if self.current_field is not None:
            self.current_text.append(content)

    def endElement(self, name):
        if self.current_pub is not None and self.current_field == name:
            text = normalize_text("".join(self.current_text))
            if name == "author":
                if text:
                    self.current_pub["authors"].append(text)
            elif name == "editor":
                if text:
                    self.current_pub["editors"].append(text)
            elif name in SINGLE_VALUE_FIELDS and text:
                if name == "year":
                    text = parse_year(text)
                if text and not self.current_pub[name]:
                    self.current_pub[name] = text
            self.current_field = None
            self.current_text = []
            return

        if self.current_pub is not None and name == self.current_pub["pub_type"]:
            pub = self.current_pub
            self.output.publication_writer.writerow([pub[column] for column in PUBLICATION_COLUMNS])
            self.stats["publications"] += 1

            for order, author_name in enumerate(pub["authors"], start=1):
                author_id = get_or_create_id(
                    author_name,
                    self.author_map,
                    self.output.author_writer,
                    "authors",
                    self.stats,
                )
                self.output.authored_writer.writerow([author_id, pub["pub_id"], order])
                self.stats["authored"] += 1

            for order, editor_name in enumerate(pub["editors"], start=1):
                editor_id = get_or_create_id(
                    editor_name,
                    self.editor_map,
                    self.output.editor_writer,
                    "editors",
                    self.stats,
                )
                self.output.edited_writer.writerow([editor_id, pub["pub_id"], order])
                self.stats["edited"] += 1

            self.current_pub = None
            if self.max_records is not None and self.pub_id >= self.max_records:
                raise StopParsing


class StopParsing(Exception):
    pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse dblp XML into CSV files for PostgreSQL loading.")
    parser.add_argument("--input", default="dblp.xml.gz", help="Path to dblp XML or XML.GZ file.")
    parser.add_argument("--output-dir", default="csv_output", help="Directory for generated CSV files.")
    parser.add_argument("--max-records", type=int, default=None, help="Only parse the first N publication records.")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    output = CSVOutput(output_dir)
    handler = DBLPHandler(output=output, max_records=args.max_records)
    parser_obj = xml.sax.make_parser()
    parser_obj.setContentHandler(handler)

    previous_cwd = Path.cwd()
    try:
        # Let the XML parser resolve dblp.dtd next to the XML file.
        import os
        os.chdir(input_path.parent)
        with gzip.open(input_path, "rt", encoding="latin-1") as fh:
            try:
                parser_obj.parse(fh)
            except StopParsing:
                pass
    finally:
        import os
        os.chdir(previous_cwd)
        output.close()

    print(f"Parsed publications: {handler.stats['publications']}")
    print(f"Unique authors: {handler.stats['authors']}")
    print(f"Unique editors: {handler.stats['editors']}")
    print(f"Authored rows: {handler.stats['authored']}")
    print(f"Edited rows: {handler.stats['edited']}")
    print(f"CSV output directory: {output_dir}")


if __name__ == "__main__":
    main()
