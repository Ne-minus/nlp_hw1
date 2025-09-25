# app.py
import reflex as rx
from typing import List
from utils import suggest  # наша фабрика из models.py


class State(rx.State):
    text: str = ""
    n_words: int = 3
    n_order: int = 2
    topk: int = 1
    outputs: List[str] = []

    def _regen(self):
        # перегенерировать подсказки при любом изменении
        outs = suggest(self.text, n_words=self.n_words, n=self.n_order, topk=self.topk)
        self.outputs = outs

    def set_text(self, value: str):
        self.text = value
        self._regen()

    def set_n_words(self, value: int):
        self.n_words = int(value)
        self._regen()

    def set_n_order(self, value: int):
        self.n_order = int(value)
        self._regen()

    def set_topk(self, value: int):
        self.topk = int(value)
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
        rx.hstack(
            rx.vstack(
                rx.text(lambda: f"Длина продолжения: {State.n_words}"),
                rx.slider(
                    min=1,
                    max=10,
                    value=State.n_words,
                    on_change=State.set_n_words,
                    width="260px",
                ),
            ),
            rx.vstack(
                rx.text(lambda: f"Порядок n-грамм: {State.n_order}"),
                rx.slider(
                    min=1,
                    max=5,
                    value=State.n_order,
                    on_change=State.set_n_order,
                    width="260px",
                ),
            ),
            rx.vstack(
                rx.text(lambda: f"Вариантов: {State.topk}"),
                rx.slider(
                    min=1,
                    max=5,
                    value=State.topk,
                    on_change=State.set_topk,
                    width="260px",
                ),
            ),
            spacing="6",
            margin_top="12px",
            wrap="wrap",
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
