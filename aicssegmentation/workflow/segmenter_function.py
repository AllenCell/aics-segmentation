from enum import Enum
from dataclasses import dataclass
from typing import Any, List


class WidgetType(Enum):
    SLIDER = "slider",
    DROPDOWN = "dropdown"


@dataclass    
class FunctionParameter:
    name: str
    widget_type: WidgetType
    data_type: str
    min_value: Any
    max_value: Any


@dataclass
class SegmenterFunction:
    display_name: str
    function: str
    module: str
    parameters: List[FunctionParameter] = None
