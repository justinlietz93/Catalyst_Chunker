from catalyst.boundary.adapters.docling.docling_document_parser import DoclingDocumentParser
from catalyst.operation.commands.chunk_source import chunk_observed_source
from catalyst.projection.views.audit_view import AuditProjection


class FakeDocument:
    def __init__(self, markdown: str) -> None:
        self.markdown = markdown

    def export_to_markdown(self) -> str:
        return self.markdown


class FakeResult:
    def __init__(self, markdown: str) -> None:
        self.document = FakeDocument(markdown)


class FakeConverter:
    def __init__(self, markdown: str) -> None:
        self.markdown = markdown

    def convert(self, path: str) -> FakeResult:
        return FakeResult(self.markdown)


def _parse(markdown: str):
    parser = DoclingDocumentParser(converter=FakeConverter(markdown))
    return parser.parse(b"%PDF fixture", location="fixture.pdf")


def test_repeated_pdf_headers_are_boundary_evidence_not_markdown_headings() -> None:
    parsed = _parse("# Running Header\n\nBody A.\n\n# Running Header\n\nBody B.")

    repeated_headers = parsed.evidence.by_kind("pdf_page_header")
    markdown_headings = parsed.evidence.by_kind("markdown_heading")
    result = chunk_observed_source(parsed.source, parsed.evidence)
    audit = AuditProjection(
        graph=result.graph,
        invariant_ledger=result.invariant_ledger,
        accepted_candidate_set_id=result.selection.accepted.candidate_set_id,
        rejections=result.selection.rejections,
    ).record()

    assert len(repeated_headers) == 2
    assert not markdown_headings
    assert result.invariant_ledger.passed
    assert audit["schema_version"] == "catalyst.audit.v1"
    assert audit["coverage"]["lost_spans"] == 0


def test_table_split_across_pages_preserves_repeated_headers() -> None:
    parsed = _parse(
        "| Col A | Col B |\n"
        "|---|---|\n"
        "| 1 | 2 |\n\n"
        "# Page Header\n\n"
        "| Col A | Col B |\n"
        "|---|---|\n"
        "| 3 | 4 |\n"
    )

    table_rows = parsed.evidence.by_kind("table_row")
    header_rows = [row for row in table_rows if row.payload["row_role"] == "header"]
    result = chunk_observed_source(parsed.source, parsed.evidence)

    assert len(header_rows) == 2
    assert result.invariant_ledger.passed
    assert result.graph.chunks[0].source_id == parsed.source.source_id


def test_ocr_hyphenation_artifacts_are_observed_without_loss() -> None:
    parsed = _parse("The cata-\nlyst source keeps this artifact visible.")
    result = chunk_observed_source(parsed.source, parsed.evidence)

    assert parsed.evidence.by_kind("ocr_hyphenation")
    assert result.invariant_ledger.passed
    assert "cata-\nlyst" in result.graph.chunks[0].text
