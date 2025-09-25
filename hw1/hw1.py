
from rxconfig import config
import reflex as rx
import pandas as pd
from typing import List
from utils import suggest

corpus = list(pd.read_csv("emails_clean_last.csv")["clean"])

if not corpus:
    print("Ошибка: корпус данных пуст!")
else:
    print(f"Корпус данных загружен, первых 5 строк:\n{corpus[:5]}")

class State(rx.State):
    text: str = ""
    n_words: int = 3
    n_order: int = 2
    topk: int = 1
    outputs: List[str] = []

    def _regen(self):
        self.outputs = suggest(self.text, n_words=self.n_words, n=self.n_order, topk=self.topk, corpus=corpus)

    def set_text(self, value: str):
        self.text = value
        self._regen()

    def set_n_words(self, value: int):
        self.n_words = value
        self._regen()

    def set_n_order(self, value: int):
        self.n_order = value
        self._regen()

    def set_topk(self, value: int):
        self.topk = value
        self._regen()


def suggestion_card(sentence: str) -> rx.Component:
    return rx.box(
        rx.text(sentence),
        padding="12px",
        border="1px solid",
        border_radius="8px",
        margin_y="6px",
    )


def index() -> rx.Component:
    return rx.container(
        rx.heading("N-gram Autocomplete", size="6", margin_bottom="12px"),
        rx.text("Начните печатать, подсказки появятся ниже."),
        rx.input(
            placeholder="Введите текст…",
            value=State.text,
            on_change=State.set_text,
            width="100%",
            margin_top="12px",
        ),
        rx.divider(margin_y="12px"),
        rx.heading("Подсказки", size="5"),
        rx.vstack(
            rx.foreach(State.outputs, suggestion_card),
            width="100%",
            margin_top="8px",
            align_items="stretch",
        ),
        padding="20px",
        max_width="900px",
    )


app = rx.App()
app.add_page(index, title="Autocomplete (n-gram + prefix)")
