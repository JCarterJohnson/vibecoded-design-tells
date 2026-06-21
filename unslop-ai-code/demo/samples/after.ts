interface LineItem {
  priceCents: number;
  quantity: number;
}

export function orderTotal(items: LineItem[], discount: number, taxRate: number): number {
  if (discount < 0 || discount > 1) {
    throw new RangeError(`discount must be a fraction in [0, 1], got ${discount}`);
  }
  const subtotal = items.reduce((sum, item) => sum + item.priceCents * item.quantity, 0);
  const discounted = Math.round(subtotal * (1 - discount));
  return Math.round(discounted * (1 + taxRate));
}
