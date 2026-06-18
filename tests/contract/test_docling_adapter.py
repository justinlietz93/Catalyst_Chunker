from catalyst.boundary.adapters.docling.docling_document_parser import DoclingDocumentParser
from catalyst.boundary.ports.document_parser_port import DocumentParserPort


class FakeDoclingDocument:
    def __init__(self, text: str) -> None:
        self._text = text

    def export_to_markdown(self) -> str:
        return self._text


class FakeDoclingResult:
    def __init__(self, text: str) -> None:
        self.document = FakeDoclingDocument(text)


class FakeDoclingConverter:
    def __init__(self, text: str) -> None:
        self.text = text
        self.converted_path: str | None = None

    def convert(self, path: str) -> FakeDoclingResult:
        self.converted_path = path
        return FakeDoclingResult(self.text)


def test_docling_adapter_satisfies_document_parser_port() -> None:
    converter = FakeDoclingConverter("# Title\n\nBody text.")
    parser = DoclingDocumentParser(converter=converter)

    parsed = parser.parse(b"%PDF fixture", location="fixture.pdf")

    assert isinstance(parser, DocumentParserPort)
    assert converter.converted_path is not None
    assert parsed.source.source_kind == "document"
    assert parsed.source.metadata["document_parser"] == "docling"
    assert parsed.evidence.source_id == parsed.source.source_id
    assert parsed.evidence.by_kind("markdown_heading")


def test_docling_adapter_does_not_leak_provider_objects() -> None:
    parser = DoclingDocumentParser(converter=FakeDoclingConverter("# Title\n\nBody text."))

    parsed = parser.parse(b"%PDF fixture", location="fixture.pdf")
    payload_values = [
        value
        for observation in parsed.evidence.observations
        for value in observation.payload.values()
    ]

    assert all(not isinstance(value, FakeDoclingDocument) for value in payload_values)
    assert all(not isinstance(value, FakeDoclingResult) for value in payload_values)
