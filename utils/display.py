"""
Utilitários: formatação e exibição de resultados
"""

from typing import List, Optional


def print_header(title: str, width: int = 55):
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def print_section(title: str, width: int = 55):
    print(f"\n{'─' * width}")
    print(f"  {title}")
    print(f"{'─' * width}")


def sensitivity_matrix(
    table: dict,
    wacc_range: List[float],
    growth_range: List[float],
    title: str = "Sensibilidade: WACC vs Crescimento Terminal",
):
    """Imprime uma tabela de sensibilidade formatada no terminal."""
    print_section(title)
    col_w = 10

    # Header
    header = f"{'WACC \\ g':>10}" + "".join(f"{g*100:>{col_w}.1f}%" for g in growth_range)
    print(header)
    print("-" * len(header))

    for w in wacc_range:
        row = f"{w*100:>9.1f}%"
        for g in growth_range:
            val = table.get((w, g))
            if val is None:
                row += f"{'  N/A':>{col_w}}"
            else:
                row += f"{val:>{col_w}.2f}"
        print(row)
