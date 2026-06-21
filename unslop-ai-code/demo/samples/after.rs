pub struct LineItem {
    pub price_cents: u64,
    pub quantity: u64,
}

pub fn order_total(items: &[LineItem], discount: f64, tax_rate: f64) -> Result<u64, String> {
    if !(0.0..=1.0).contains(&discount) {
        return Err(format!("discount must be a fraction in [0, 1], got {discount}"));
    }
    let subtotal: u64 = items.iter().map(|item| item.price_cents * item.quantity).sum();
    let discounted = (subtotal as f64 * (1.0 - discount)).round();
    Ok((discounted * (1.0 + tax_rate)).round() as u64)
}
