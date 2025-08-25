from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path    

class BaseFetcher(ABC):
    @abstractmethod
    def fetch(self, owner: str, repo: str, ref: Optional[str] = None) -> Path:
        """
        Fetch repository and return path to local copy
        """
        pass