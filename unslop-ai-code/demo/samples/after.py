from dataclasses import dataclass


@dataclass(frozen=True)
class LineItem:
    price_cents: int
    quantity: int


def order_total(items: list[LineItem], discount: float, tax_rate: float) -> int:
    if not 0 <= discount <= 1:
        raise ValueError(f"discount must be a fraction in [0, 1], got {discount}")
    subtotal = sum(item.price_cents * item.quantity for item in items)
    discounted = round(subtotal * (1 - discount))
    return round(discounted * (1 + tax_rate))
