"""
pricing_project/main.py
========================
CLI interativo para pricing financeiro.
Módulos: Opções (Black-Scholes), Bonds e Valuation (DCF).
"""

import math
import sys
from models import black_scholes, implied_volatility, OptionType
from models import price_bond, bond_yield
from models import dcf, sensitivity_table
from utils.display import print_header, print_section, sensitivity_matrix

# ─────────────────────────────────────────────
# HELPERS DE INPUT
# ─────────────────────────────────────────────

def ask(prompt: str, tipo=float, default=None):
    """Lê um valor do usuário com validação e suporte a default."""
    sufixo = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"  {prompt}{sufixo}: ").strip()
        if raw == "" and default is not None:
            return tipo(default)
        try:
            return tipo(raw)
        except ValueError:
            print(f"  ⚠  Valor inválido. Esperado: {tipo.__name__}")


def ask_percent(prompt: str, default=None):
    """Lê uma porcentagem e retorna como decimal (ex: 12 → 0.12)."""
    val = ask(f"{prompt} (%)", float, default)
    return val / 100.0


def ask_choice(prompt: str, opcoes: list) -> str:
    """Menu de escolha numerada."""
    for i, op in enumerate(opcoes, 1):
        print(f"  [{i}] {op}")
    while True:
        raw = input(f"  {prompt}: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(opcoes):
            return opcoes[int(raw) - 1]
        print(f"  ⚠  Digite um número entre 1 e {len(opcoes)}.")


def pausar():
    input("\n  ↩  Pressione Enter para continuar...")


def limpar():
    print("\n" * 2)


# ─────────────────────────────────────────────
# MÓDULO 1 — OPÇÕES
# ─────────────────────────────────────────────

def menu_opcoes():
    while True:
        limpar()
        print_header("OPÇÕES — BLACK-SCHOLES")
        opcao = ask_choice("Escolha", [
            "Precificar opção (Call / Put)",
            "Calcular volatilidade implícita",
            "Voltar ao menu principal",
        ])

        if opcao == "Voltar ao menu principal":
            break

        elif opcao == "Precificar opção (Call / Put)":
            limpar()
            print_section("Parâmetros da Opção")
            S     = ask("Preço atual do ativo (S)", float, 100)
            K     = ask("Strike / Preço de exercício (K)", float, 105)
            T     = ask("Tempo até vencimento em anos (ex: 0.5 = 6 meses)", float, 0.5)
            r     = ask_percent("Taxa livre de risco anual", 12)
            sigma = ask_percent("Volatilidade anual (sigma)", 25)

            tipo_str = ask_choice("Tipo da opção", ["Call", "Put"])
            tipo = OptionType.CALL if tipo_str == "Call" else OptionType.PUT

            resultado = black_scholes(S, K, T, r, sigma, option_type=tipo)

            print_section(f"Resultado — {tipo_str} Europeia")
            print(resultado)

            # Paridade Put-Call
            if tipo == OptionType.CALL:
                put_res = black_scholes(S, K, T, r, sigma, option_type=OptionType.PUT)
                lhs = resultado.price - put_res.price
                rhs = S - K * math.exp(-r * T)
                print_section("Paridade Put-Call")
                print(f"  C - P       = {lhs:.4f}")
                print(f"  S - PV(K)   = {rhs:.4f}")
                print(f"  Diferença   = {abs(lhs - rhs):.2e}  ✓")

            pausar()

        elif opcao == "Calcular volatilidade implícita":
            limpar()
            print_section("Volatilidade Implícita (Newton-Raphson)")
            preco_mkt = ask("Preço de mercado da opção", float, 6.50)
            S = ask("Preço atual do ativo (S)", float, 100)
            K = ask("Strike (K)", float, 105)
            T = ask("Tempo até vencimento em anos", float, 0.5)
            r = ask_percent("Taxa livre de risco anual", 12)
            tipo_str = ask_choice("Tipo da opção", ["Call", "Put"])
            tipo = OptionType.CALL if tipo_str == "Call" else OptionType.PUT

            iv = implied_volatility(preco_mkt, S, K, T, r, option_type=tipo)

            print_section("Resultado")
            print(f"  Preço de mercado : R$ {preco_mkt:.4f}")
            print(f"  Vol. Implícita   : {iv * 100:.4f}%")
            pausar()


# ─────────────────────────────────────────────
# MÓDULO 2 — BONDS
# ─────────────────────────────────────────────

def menu_bonds():
    while True:
        limpar()
        print_header("BONDS — RENDA FIXA")
        opcao = ask_choice("Escolha", [
            "Precificar bond (YTM → Preço)",
            "Calcular YTM (Preço → YTM)",
            "Análise de sensibilidade (±taxa)",
            "Voltar ao menu principal",
        ])

        if opcao == "Voltar ao menu principal":
            break

        elif opcao == "Precificar bond (YTM → Preço)":
            limpar()
            print_section("Parâmetros do Título")
            face    = ask("Valor de face", float, 1000)
            coupon  = ask_percent("Taxa de cupom anual", 6)
            ytm     = ask_percent("YTM (yield to maturity) anual", 8)
            anos    = ask("Prazo em anos", int, 5)
            freq    = ask_choice("Frequência de cupom", ["Semestral (2x/ano)", "Anual (1x/ano)"])
            f       = 2 if "Semestral" in freq else 1
            periods = anos * f

            resultado = price_bond(face, coupon, ytm, periods, frequency=f)

            print_section("Resultado")
            print(resultado)

            if resultado.price > face:
                print(f"\n  → Título acima do par (prêmio): cupom > YTM")
            elif resultado.price < face:
                print(f"\n  → Título abaixo do par (desconto): cupom < YTM")
            else:
                print(f"\n  → Título ao par: cupom = YTM")
            pausar()

        elif opcao == "Calcular YTM (Preço → YTM)":
            limpar()
            print_section("Calcular YTM pelo Preço de Mercado")
            mkt    = ask("Preço de mercado", float, 950)
            face   = ask("Valor de face", float, 1000)
            coupon = ask_percent("Taxa de cupom anual", 6)
            anos   = ask("Prazo em anos", int, 5)
            freq   = ask_choice("Frequência de cupom", ["Semestral (2x/ano)", "Anual (1x/ano)"])
            f      = 2 if "Semestral" in freq else 1
            periods = anos * f

            ytm = bond_yield(mkt, face, coupon, periods, frequency=f)

            print_section("Resultado")
            print(f"  Preço de mercado : R$ {mkt:.2f}")
            print(f"  YTM calculado    : {ytm * 100:.4f}% a.a.")
            pausar()

        elif opcao == "Análise de sensibilidade (±taxa)":
            limpar()
            print_section("Sensibilidade a Variações de Taxa")
            face   = ask("Valor de face", float, 1000)
            coupon = ask_percent("Taxa de cupom anual", 6)
            ytm    = ask_percent("YTM base anual", 8)
            anos   = ask("Prazo em anos", int, 5)
            freq   = ask_choice("Frequência de cupom", ["Semestral (2x/ano)", "Anual (1x/ano)"])
            f      = 2 if "Semestral" in freq else 1
            periods = anos * f
            delta  = ask_percent("Variação de taxa (ex: 1 = ±1%)", 1)

            base = price_bond(face, coupon, ytm, periods, frequency=f)

            print_section("Resultado")
            print(f"  YTM base  : {ytm*100:.2f}%  → Preço: R$ {base.price:.4f}")
            for sinal, label in [(1, f"+{delta*100:.1f}%"), (-1, f"-{delta*100:.1f}%")]:
                b = price_bond(face, coupon, ytm + sinal * delta, periods, frequency=f)
                chg = b.price - base.price
                pct = chg / base.price * 100
                print(f"  YTM {label:<6}: R$ {b.price:.4f}  (Δ {chg:+.4f} / {pct:+.2f}%)")
            pausar()


# ─────────────────────────────────────────────
# MÓDULO 3 — DCF
# ─────────────────────────────────────────────

def menu_dcf():
    while True:
        limpar()
        print_header("VALUATION — DCF")
        opcao = ask_choice("Escolha", [
            "Calcular valor intrínseco",
            "Tabela de sensibilidade (WACC × g)",
            "Voltar ao menu principal",
        ])

        if opcao == "Voltar ao menu principal":
            break

        elif opcao == "Calcular valor intrínseco":
            limpar()
            print_section("Fluxos de Caixa Livres (FCF)")
            n = ask("Número de anos de projeção", int, 5)
            fcf = []
            for i in range(1, n + 1):
                v = ask(f"FCF Ano {i} (R$ MM)", float)
                fcf.append(v)

            print_section("Parâmetros de Desconto")
            wacc     = ask_percent("WACC anual", 12)
            g        = ask_percent("Crescimento terminal (g)", 4)
            net_debt = ask("Dívida líquida (R$ MM)", float, 0)
            shares   = ask("Número de ações (MM)", float, 1)

            resultado = dcf(fcf, wacc, g, net_debt, shares)

            print_section("Resultado")
            print(resultado)
            pausar()

        elif opcao == "Tabela de sensibilidade (WACC × g)":
            limpar()
            print_section("Configuração — Tabela de Sensibilidade")
            n = ask("Número de anos de projeção", int, 5)
            fcf = []
            for i in range(1, n + 1):
                v = ask(f"FCF Ano {i} (R$ MM)", float)
                fcf.append(v)

            net_debt = ask("Dívida líquida (R$ MM)", float, 0)
            shares   = ask("Número de ações (MM)", float, 1)

            print_section("Faixas para Sensibilidade")
            wacc_min  = ask_percent("WACC mínimo", 10)
            wacc_max  = ask_percent("WACC máximo", 14)
            wacc_step = ask_percent("Passo do WACC", 1)
            g_min     = ask_percent("g mínimo", 2)
            g_max     = ask_percent("g máximo", 6)
            g_step    = ask_percent("Passo do g", 1)

            def frange(start, stop, step):
                vals = []
                v = start
                while v <= stop + 1e-9:
                    vals.append(round(v, 4))
                    v += step
                return vals

            wacc_range   = frange(wacc_min, wacc_max, wacc_step)
            growth_range = frange(g_min, g_max, g_step)

            table = sensitivity_table(fcf, wacc_range, growth_range, net_debt, shares)
            sensitivity_matrix(table, wacc_range, growth_range,
                               title="Preço por Ação (R$) — WACC × g")
            pausar()


# ─────────────────────────────────────────────
# MENU PRINCIPAL
# ─────────────────────────────────────────────

def main():
    print_header("PRICING FINANCEIRO — CLI INTERATIVO", width=55)
    print("  Modelos: Black-Scholes · Bonds · DCF")
    print("  Digite Ctrl+C a qualquer momento para sair.\n")

    while True:
        print_section("MENU PRINCIPAL")
        opcao = ask_choice("Escolha o módulo", [
            "Opções (Black-Scholes)",
            "Bonds (Renda Fixa)",
            "Valuation (DCF)",
            "Sair",
        ])

        if opcao == "Opções (Black-Scholes)":
            menu_opcoes()
        elif opcao == "Bonds (Renda Fixa)":
            menu_bonds()
        elif opcao == "Valuation (DCF)":
            menu_dcf()
        elif opcao == "Sair":
            print("\n  Até logo!\n")
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Interrompido. Até logo!\n")
        sys.exit(0)
