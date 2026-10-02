"""A small order model, used for the curate demo."""

from dataclasses import dataclass, field

TAX_RATE = 0.25


@dataclass
class Line:
    sku: str
    quantity: int
    unit_price: float


@dataclass
class Order:
    lines: list[Line] = field(default_factory=list)

    def add(self, sku: str, quantity: int, unit_price: float) -> None:
        self.lines.append(Line(sku, quantity, unit_price))

    def subtotal(self) -> float:
        return sum(line.quantity * line.unit_price for line in self.lines)

    def discounts(self) -> float:
        total = 0.0
        for line in self.lines:
            if line.quantity >= 10:
                total += line.quantity * line.unit_price * 0.1
        return total

    @property
    def total(self) -> float:
        net = self.subtotal() - self.discounts()
        return round(net * (1 + TAX_RATE), 2)

    @classmethod
    def from_rows(cls, rows: list[str]) -> "Order":
        order = cls()
        for row in rows:
            line = parse_line(row)
            order.add(line.sku, line.quantity, line.unit_price)
        return order


def parse_line(text: str) -> Line:
    sku, quantity, price = text.split(",")
    return Line(sku.strip(), int(quantity), float(price))
