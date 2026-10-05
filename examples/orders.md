# Orders

A small order model: lines, discounts and totals.

## Install

### From source

Clone the repository and run `make install`.

### As a package

Not on PyPI yet.

## Usage

### Adding lines

Create an `Order` and call `add` with a SKU, a quantity
and a unit price.

### Discounts

Ten or more of one SKU gives ten percent off that line.
Discounts are computed per line, never on the total.

### Totals

`total` is the subtotal minus discounts, plus tax.

## Design

### Line

One SKU, a quantity and a unit price. Nothing else.

### Order

A list of lines and the rules that price them.

# Appendix

## Changelog

First version.
