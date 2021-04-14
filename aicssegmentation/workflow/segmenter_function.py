from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Union


class WidgetType(Enum):
    SLIDER = "slider"
    DROPDOWN = "drop-down"

    @staticmethod
    def from_str(value: str):
        if value is not None:
            value = value.lower()
        if value == WidgetType.SLIDER.value:
            return WidgetType.SLIDER
        if value == WidgetType.DROPDOWN.value:
            return WidgetType.DROPDOWN
        raise NotImplementedError()
            

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
    name: str
    display_name: str
    function: str
    module: str
    parameters: Dict[str, List[FunctionParameter]] = None
