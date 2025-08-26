# Protocols / Interfaces
from typing import Protocol, Tuple
from pathlib import Path
from .plan import Plan
from .config import DetectorConfig

class Detector(Protocol):
    def detect(self, root: Path, cfg: DetectorConfig) -> Tuple[Plan, List[str]]:
        """
        Detect plan and return list of diagnostics
        """
        pass