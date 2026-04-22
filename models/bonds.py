"""
Precificação de Títulos de Renda Fixa (Bonds)
"""

from dataclasses import dataclass
from typing import List


@dataclass
class BondResult:
    price: float
    duration: float          # Duration de Macaulay (anos)
    modified_duration: float # Duration Modificada
    convexity: float
    ytm: float               # Yield to Maturity usado

    def __str__(self):
        return (
            f"  Preço:              R$ {self.price:.4f}\n"
            f"  Duration Macaulay:  {self.duration:.4f} anos\n"
            f"  Duration Modificada:{self.modified_duration:.4f}\n"
            f"  Convexidade:        {self.convexity:.4f}\n"
            f"  YTM usado:          {self.ytm * 100:.2f}%"
        )


def price_bond(
    face_value: float,    # Valor de face
    coupon_rate: float,   # Taxa de cupom anual
    ytm: float,           # Yield to Maturity (taxa de desconto)
    periods: int,         # Número de períodos (semestres ou anos)
    frequency: int = 2,   # Pagamentos por ano (2 = semestral)
) -> BondResult:
    """
    Precifica um bond com cupons periódicos e calcula Duration e Convexidade.
    """
    coupon = face_value * coupon_rate / frequency
    r = ytm / frequency  # taxa por período

    price = 0.0
    duration_num = 0.0
    convexity_num = 0.0

    for t in range(1, periods + 1):
        cf = coupon if t < periods else coupon + face_value
        pv = cf / (1 + r) ** t
        price += pv
        duration_num += t * pv
        convexity_num += t * (t + 1) * pv

    mac_duration = (duration_num / price) / frequency
    mod_duration = mac_duration / (1 + r)
    convexity = convexity_num / (price * (1 + r) ** 2 * frequency**2)

    return BondResult(
        price=price,
        duration=mac_duration,
        modified_duration=mod_duration,
        convexity=convexity,
        ytm=ytm,
    )


def bond_yield(
    market_price: float,
    face_value: float,
    coupon_rate: float,
    periods: int,
    frequency: int = 2,
    tol: float = 1e-8,
    max_iter: int = 1000,
) -> float:
    """
    Calcula o YTM de um bond a partir do preço de mercado (bissecção).
    """
    low, high = 0.0001, 5.0

    for _ in range(max_iter):
        mid = (low + high) / 2
        result = price_bond(face_value, coupon_rate, mid, periods, frequency)
        if abs(result.price - market_price) < tol:
            return mid
        if result.price > market_price:
            low = mid
        else:
            high = mid

    return (low + high) / 2
