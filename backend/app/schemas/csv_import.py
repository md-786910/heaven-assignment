from pydantic import BaseModel
from typing import List, Optional


class CSVImportRow(BaseModel):
    row_number: int
    success: bool
    issue_id: Optional[int] = None
    errors: List[str] = []


class CSVImportResult(BaseModel):
    total_rows: int
    successful: int
    failed: int
    results: List[CSVImportRow]
