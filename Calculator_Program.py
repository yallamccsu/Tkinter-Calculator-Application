import tkinter as tk
from tkinter import StringVar
from typing import Callable, List, Tuple, Optional, Dict, Any
from functools import reduce, partial
from enum import Enum, auto
import math
import re
import sys


class TokenType(Enum):
    NUMBER = auto()
    OPERATOR = auto()
    DECIMAL = auto()
    CLEAR = auto()
    EQUALS = auto()


OPERATOR_PRECEDENCE: Dict[str, int] = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
}

BUTTON_SCHEMA: List[Tuple[str, int, int, int, TokenType]] = [
    ('Clear', 0, 0, 4, TokenType.CLEAR),
    ('/',    1, 0, 1, TokenType.OPERATOR),
    ('7',    1, 1, 1, TokenType.NUMBER),
    ('8',    1, 2, 1, TokenType.NUMBER),
    ('9',    1, 3, 1, TokenType.NUMBER),
    ('*',    2, 0, 1, TokenType.OPERATOR),
    ('4',    2, 1, 1, TokenType.NUMBER),
    ('5',    2, 2, 1, TokenType.NUMBER),
    ('6',    2, 3, 1, TokenType.NUMBER),
    ('-',    3, 0, 1, TokenType.OPERATOR),
    ('1',    3, 1, 1, TokenType.NUMBER),
    ('2',    3, 2, 1, TokenType.NUMBER),
    ('3',    3, 3, 1, TokenType.NUMBER),
    ('+',    4, 0, 1, TokenType.OPERATOR),
    ('0',    4, 1, 2, TokenType.NUMBER),
    ('.',    4, 3, 1, TokenType.DECIMAL),
    ('=',    5, 0, 4, TokenType.EQUALS),
]

COLOR_MAP: Dict[TokenType, str] = {
    TokenType.NUMBER:   '#dcdcdc',
    TokenType.OPERATOR: '#ff9f00',
    TokenType.DECIMAL:  '#ff9f00',
    TokenType.CLEAR:    '#ff5c5c',
    TokenType.EQUALS:   '#ff9f00',
}

FONT_DISPLAY = ('Arial', 20, 'bold')
FONT_BUTTON  = ('Arial', 16, 'bold')


def _sanitize_expression(expr: str) -> str:
    # strip anything that isnt a digit operator or decimal
    allowed = re.compile(r'[0-9+\-*/\. ]+')
    tokens = allowed.findall(expr)
    return ''.join(tokens).strip()


def _is_expression_balanced(expr: str) -> bool:
    ops = set('+-*/')
    if not expr:
        return False
    if expr[-1] in ops:
        return False
    if expr[0] in ops and expr[0] != '-':
        return False
    return True


def _safe_evaluate(expr: str) -> Optional[str]:
    sanitized = _sanitize_expression(expr)
    if not _is_expression_balanced(sanitized):
        return None
    try:
        # kept eval but wrapped in strict sanitization pipeline
        raw_result = eval(sanitized, {"__builtins__": {}}, {})
        if isinstance(raw_result, float):
            if math.isinf(raw_result) or math.isnan(raw_result):
                return None
            # trim unnecessary trailing zeros
            return f"{raw_result:.10f}".rstrip('0').rstrip('.')
        return str(raw_result)
    except Exception:
        return None


def _classify_token(text: str) -> TokenType:
    lookup = {entry[0]: entry[4] for entry in BUTTON_SCHEMA}
    return lookup.get(text, TokenType.NUMBER)


class ExpressionEngine:
    def __init__(self):
        self._buffer: List[str] = []
        self._last_result: Optional[str] = None
        self._history: List[Tuple[str, str]] = []

    def append(self, token: str):
        self._buffer.append(str(token))

    def clear(self):
        self._buffer.clear()

    def get_expression(self) -> str:
        return ''.join(self._buffer)

    def evaluate(self) -> str:
        expr = self.get_expression()
        result = _safe_evaluate(expr)
        if result is None:
            self.clear()
            return 'Error'
        self._history.append((expr, result))
        self._last_result = result
        self.clear()
        return result

    def get_history(self) -> List[Tuple[str, str]]:
        return list(self._history)

    def history_depth(self) -> int:
        return len(self._history)


class ButtonFactory:
    @staticmethod
    def build(
        parent: tk.Frame,
        text: str,
        token_type: TokenType,
        colspan: int,
        command: Callable,
    ) -> tk.Button:
        bg = COLOR_MAP.get(token_type, '#dcdcdc')
        return tk.Button(
            parent,
            text=text,
            fg='black',
            width=10 * colspan,
            height=3,
            bd=0,
            bg=bg,
            cursor='hand2',
            font=FONT_BUTTON,
            command=command,
        )


class CalculatorApp:
    def __init__(self):
        self.engine = ExpressionEngine()
        self.input_text = StringVar()

        self.main_window = tk.Tk()
        self.main_window.geometry('350x400')
        self.main_window.title('My_Calculator')
        self.main_window.resizable(False, False)

        self._build_display()
        self._build_buttons()

        self.main_window.mainloop()

    def _build_display(self):
        input_frame = tk.Frame(
            self.main_window,
            width=350, height=50,
            bd=0,
            highlightbackground='black',
            highlightcolor='black',
            highlightthickness=1,
        )
        input_frame.pack(side='top')

        input_field = tk.Entry(
            input_frame,
            font=FONT_DISPLAY,
            textvariable=self.input_text,
            width=50,
            bg='#f4f4f4',
            bd=0,
            justify='right',
        )
        input_field.pack(ipady=15)

    def _build_buttons(self):
        btns_frame = tk.Frame(self.main_window, width=350, height=350, bg='#f2f2f2')
        btns_frame.pack()

        for text, row, col, colspan, token_type in BUTTON_SCHEMA:
            cmd = self._resolve_command(text, token_type)
            btn = ButtonFactory.build(btns_frame, text, token_type, colspan, cmd)
            btn.grid(row=row, column=col, columnspan=colspan, padx=5, pady=5)

    def _resolve_command(self, text: str, token_type: TokenType) -> Callable:
        # routes each button to the right handler based on its type
        dispatch: Dict[TokenType, Callable] = {
            TokenType.CLEAR:    self._handle_clear,
            TokenType.EQUALS:   self._handle_equals,
            TokenType.NUMBER:   partial(self._handle_input, text),
            TokenType.OPERATOR: partial(self._handle_input, text),
            TokenType.DECIMAL:  partial(self._handle_input, text),
        }
        return dispatch.get(token_type, lambda: None)

    def _handle_input(self, token: str):
        self.engine.append(token)
        self.input_text.set(self.engine.get_expression())

    def _handle_clear(self):
        self.engine.clear()
        self.input_text.set('')

    def _handle_equals(self):
        result = self.engine.evaluate()
        self.input_text.set(result)


if __name__ == '__main__':
    CalculatorApp()
