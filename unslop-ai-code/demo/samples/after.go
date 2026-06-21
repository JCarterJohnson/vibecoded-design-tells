package checkout

import (
	"errors"
	"math"
)

type LineItem struct {
	PriceCents int
	Quantity   int
}

func OrderTotal(items []LineItem, discount, taxRate float64) (int, error) {
	if discount < 0 || discount > 1 {
		return 0, errors.New("discount must be a fraction in [0, 1]")
	}
	subtotal := 0
	for _, item := range items {
		subtotal += item.PriceCents * item.Quantity
	}
	discounted := math.Round(float64(subtotal) * (1 - discount))
	return int(math.Round(discounted * (1 + taxRate))), nil
}
