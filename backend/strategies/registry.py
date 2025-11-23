# backend/strategies/registry.py
"""
Strategy Registry - Catálogo de estrategias disponibles.

Este módulo mantiene el registro de todas las estrategias que pueden
ejecutarse en el backend, tanto built-in como de trading_lab.
"""

from typing import Dict, List, Optional, Type
from .base import Strategy, StrategyMetadata


class StrategyRegistry:
    """
    Registro centralizado de estrategias disponibles.
    
    Permite:
    - Descubrir qué estrategias están disponibles
    - Instanciar estrategias by ID
    - Listar estrategias activas
    """
    
    def __init__(self):
        self._strategies: Dict[str, Type[Strategy]] = {}
    
    def register(self, strategy_class: Type[Strategy]) -> None:
        """
        Registra una clase de estrategia.
        
        Args:
            strategy_class: Clase que hereda de Strategy
        """
        # Instanciar temporalmente para obtener metadata
        temp_instance = strategy_class()
        meta = temp_instance.metadata()
        
        if meta.id in self._strategies:
            print(f"⚠️  Warning: Overwriting strategy '{meta.id}'")
        
        self._strategies[meta.id] = strategy_class
        print(f"✅ Registered strategy: {meta.id} - {meta.name}")
    
    def get(self, strategy_id: str, config: Optional[dict] = None) -> Optional[Strategy]:
        """
        Obtiene una instancia de estrategia por ID.
        
        Args:
            strategy_id: ID de la estrategia
            config: Configuración opcional
            
        Returns:
            Instancia de la estrategia o None si no existe
        """
        strategy_class = self._strategies.get(strategy_id)
        if not strategy_class:
            return None
        
        # Instanciar con config si aplica
        try:
            if config:
                return strategy_class(config=config)
            else:
                return strategy_class()
        except TypeError:
            # La estrategia no acepta config
            return strategy_class()
    
    def list_all(self) -> List[StrategyMetadata]:
        """
        Lista metadatos de todas las estrategias registradas.
        
        Returns:
            Lista de StrategyMetadata
        """
        metadatas = []
        for strategy_class in self._strategies.values():
            instance = strategy_class()
            metadatas.append(instance.metadata())
        return metadatas
    
    def list_enabled(self) -> List[StrategyMetadata]:
        """
        Lista solo estrategias habilitadas.
        
        Returns:
            Lista de StrategyMetadata de estrategias enabled=True
        """
        return [m for m in self.list_all() if m.enabled]


# Instancia global del registry
registry = StrategyRegistry()


def get_registry() -> StrategyRegistry:
    """Helper para obtener el registry global."""
    return registry
