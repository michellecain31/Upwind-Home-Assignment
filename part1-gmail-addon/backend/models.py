# Pydantic Data Models: Defines the request and response schemas for API endpoints.

from pydantic import BaseModel
from typing import List, Optional


# Schema for incoming telemetry data extracted by the Google Apps Script client
class EmailRequest(BaseModel):
    subject: str
    sender: str
    reply_to: Optional[str] = None
    body: str
    urls: List[str] = []


# Schema for an individual analytical indicator evaluation result
class SignalResult(BaseModel):
    name: str
    score: int
    detail: str


# Schema for the aggregate security verdict returned to the client
class ScanResult(BaseModel):
    total_score: int
    verdict: str  # SAFE / SUSPICIOUS / MALICIOUS
    signals: List[SignalResult]