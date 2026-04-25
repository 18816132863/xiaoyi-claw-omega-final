"""UI 定位"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class UIElement:
    """UI 元素"""
    element_id: str
    element_type: str  # button, text, input, image
    text: str
    bounds: Dict[str, int]  # x, y, width, height
    clickable: bool = True
    visible: bool = True


class UIGrounding:
    """UI 定位"""
    
    def locate_by_text(self, text: str, elements: List[UIElement]) -> Optional[UIElement]:
        """通过文本定位"""
        for elem in elements:
            if text in elem.text:
                return elem
        return None
    
    def locate_by_type(self, element_type: str, elements: List[UIElement]) -> List[UIElement]:
        """通过类型定位"""
        return [e for e in elements if e.element_type == element_type]
    
    def locate_button(self, text: str, elements: List[UIElement]) -> Optional[UIElement]:
        """定位按钮"""
        for elem in elements:
            if elem.element_type == "button" and text in elem.text:
                return elem
        return None
    
    def locate_input(self, hint: str, elements: List[UIElement]) -> Optional[UIElement]:
        """定位输入框"""
        for elem in elements:
            if elem.element_type == "input" and hint in elem.text:
                return elem
        return None
