from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, List, Union


class WidgetType(Enum):
    SLIDER = "slider",
    DROPDOWN = "dropdown"


@dataclass    
class FunctionParameter:
    name: str
    widget_type: WidgetType
    data_type: str
    min_value: Union[int, float] = None
    max_value: Union[int, float] = None
    increment: Union[int, float] = None
    options: List[str] = None


@dataclass
class SegmenterFunction:
    display_name: str
    function: str
    module: str
    parameters: Dict[str, List[FunctionParameter]] = None
