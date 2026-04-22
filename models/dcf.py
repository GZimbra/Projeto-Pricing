"""
Valuation por Fluxo de Caixa Descontado (DCF)
"""

from dataclasses import dataclass
from typing import List


@dataclass
class DCFResult:
    intrinsic_value: float
    pv_explicit: float       # PV dos fluxos explícitos
    pv_terminal: float       # PV do valor terminal
    terminal_value: float
    implied_multiple: float  # EV / último FCF

    def __str__(self):
        return (
            f"  Valor Intrínseco:   R$ {self.intrinsic_value:,.2f}\n"
            f"  PV Fluxos Expl.:   R$ {self.pv_explicit:,.2f}\n"
            f"  PV Valor Terminal: R$ {self.pv_terminal:,.2f}\n"
            f"  Valor Terminal:    R$ {self.terminal_value:,.2f}\n"
            f"  Múltiplo Implícito:{self.implied_multiple:.1f}x"
        )


def dcf(
    free_cash_flows: List[float],  # FCF projetados (ano 1 até N)
    wacc: float,                   # Custo médio ponderado de capital
    terminal_growth: float,        # Taxa de crescimento na perpetuidade
    net_debt: float = 0.0,         # Dívida líquida (para equity value)
    shares: float = 1.0,           # Número de ações (para preço por ação)
) -> DCFResult:
    """
    Valuation DCF com valor terminal pelo modelo de Gordon.
    Retorna valor da empresa (EV) e, se shares fornecido, preço por ação.
    """
    if wacc <= terminal_growth:
        raise ValueError("WACC deve ser maior que a taxa de crescimento terminal.")

    pv_explicit = sum(
        cf / (1 + wacc) ** t
        for t, cf in enumerate(free_cash_flows, start=1)
    )

    # Valor terminal pelo modelo de Gordon (perpetuidade crescente)
    last_fcf = free_cash_flows[-1]
    n = len(free_cash_flows)
    terminal_value = last_fcf * (1 + terminal_growth) / (wacc - terminal_growth)
    pv_terminal = terminal_value / (1 + wacc) ** n

    enterprise_value = pv_explicit + pv_terminal
    equity_value = enterprise_value - net_debt
    price_per_share = equity_value / shares if shares > 0 else 0

    return DCFResult(
        intrinsic_value=price_per_share,
        pv_explicit=pv_explicit,
        pv_terminal=pv_terminal,
        terminal_value=terminal_value,
        implied_multiple=enterprise_value / last_fcf if last_fcf else 0,
    )


def sensitivity_table(
    free_cash_flows: List[float],
    wacc_range: List[float],
    growth_range: List[float],
    net_debt: float = 0.0,
    shares: float = 1.0,
) -> dict:
    """
    Tabela de sensibilidade: WACC vs. Taxa de Crescimento Terminal.
    Retorna dict {(wacc, g): valor_intrínseco}.
    """
    table = {}
    for w in wacc_range:
        for g in growth_range:
            if w <= g:
                table[(w, g)] = None
                continue
            result = dcf(free_cash_flows, w, g, net_debt, shares)
            table[(w, g)] = result.intrinsic_value
    return table
