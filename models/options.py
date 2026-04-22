"""
Black-Scholes Option Pricing Model
"""

import math
from scipy.stats import norm
from dataclasses import dataclass
from enum import Enum


class OptionType(Enum):
    CALL = "call"
    PUT = "put"


@dataclass
class OptionResult:
    price: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float

    def __str__(self):
        return (
            f"  Preço:  R$ {self.price:.4f}\n"
            f"  Delta:  {self.delta:.4f}\n"
            f"  Gamma:  {self.gamma:.4f}\n"
            f"  Theta:  {self.theta:.4f}\n"
            f"  Vega:   {self.vega:.4f}\n"
            f"  Rho:    {self.rho:.4f}"
        )


def black_scholes(
    S: float,       # Preço atual do ativo
    K: float,       # Strike (preço de exercício)
    T: float,       # Tempo até vencimento (em anos)
    r: float,       # Taxa livre de risco (anual)
    sigma: float,   # Volatilidade (anual)
    option_type: OptionType = OptionType.CALL,
) -> OptionResult:
    """
    Precifica uma opção europeia usando o modelo Black-Scholes.
    Retorna preço e as Greeks principais.
    """
    if T <= 0:
        intrinsic = max(S - K, 0) if option_type == OptionType.CALL else max(K - S, 0)
        return OptionResult(price=intrinsic, delta=0, gamma=0, theta=0, vega=0, rho=0)

    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)

    if option_type == OptionType.CALL:
        price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
        delta = norm.cdf(d1)
        rho = K * T * math.exp(-r * T) * norm.cdf(d2) / 100
    else:
        price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        delta = norm.cdf(d1) - 1
        rho = -K * T * math.exp(-r * T) * norm.cdf(-d2) / 100

    gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
    theta = (
        -S * norm.pdf(d1) * sigma / (2 * math.sqrt(T))
        - r * K * math.exp(-r * T) * (norm.cdf(d2) if option_type == OptionType.CALL else norm.cdf(-d2))
    ) / 365
    vega = S * norm.pdf(d1) * math.sqrt(T) / 100

    return OptionResult(price=price, delta=delta, gamma=gamma, theta=theta, vega=vega, rho=rho)


def implied_volatility(
    market_price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    option_type: OptionType = OptionType.CALL,
    tol: float = 1e-6,
    max_iter: int = 200,
) -> float:
    """
    Calcula a volatilidade implícita via método de Newton-Raphson.
    """
    sigma = 0.3  # chute inicial

    for _ in range(max_iter):
        result = black_scholes(S, K, T, r, sigma, option_type)
        diff = result.price - market_price
        if abs(diff) < tol:
            return sigma
        vega = result.vega * 100  # desfaz o /100 do cálculo
        if abs(vega) < 1e-10:
            break
        sigma -= diff / vega

    return sigma
