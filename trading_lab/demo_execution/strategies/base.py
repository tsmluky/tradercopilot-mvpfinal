from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel
from core.schemas import Signal

class StrategyConfigInRuntime(BaseModel):
    tokens: List[str]
    params: Optional[Dict] = None

class Strategy(ABC):
    id: str
    name: str
    version: str
    default_timeframe: str
    default_params: Dict = {}

    @abstractmethod
    def run(self, config: StrategyConfigInRuntime, market_data_service) -> List[Signal]:
        pass
