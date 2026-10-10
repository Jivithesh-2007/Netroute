"""
Router model representing a node in the network topology.
"""
from typing import Dict, Any, Optional


class Router:
    """Represents a network router node."""

    def __init__(self, router_id: str, name: str, x: float, y: float, is_online: bool = True):
        self.id = router_id
        self.name = name
        self.x = x
        self.y = y
        self.is_online = is_online

    def to_dict(self) -> Dict[str, Any]:
        """Serialize router to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "is_online": self.is_online
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Router':
        """Create Router instance from dictionary."""
        return cls(
            router_id=data["id"],
            name=data["name"],
            x=data["x"],
            y=data["y"],
            is_online=data.get("is_online", True)
        )

    def __repr__(self) -> str:
        status = "Online" if self.is_online else "Offline"
        return f"Router({self.id}, '{self.name}', pos=({self.x}, {self.y}), status={status})"
