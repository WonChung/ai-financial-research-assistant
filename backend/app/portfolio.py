from dataclasses import dataclass


@dataclass(frozen=True)
class Holding:
    ticker: str
    name: str
    sector: str | None
    weight_percent: float


@dataclass(frozen=True)
class LargestPosition:
    ticker: str
    name: str
    sector: str | None
    weight_percent: float


@dataclass(frozen=True)
class PortfolioRiskSummary:
    concentration_risk_notes: list[str]
    largest_positions: list[LargestPosition]
    sector_concentration_notes: list[str]
    missing_data_warnings: list[str]
    risk_explanation: str
    disclaimer: str


def summarize_portfolio_risk(holdings: list[Holding]) -> PortfolioRiskSummary:
    sorted_holdings = sorted(
        holdings,
        key=lambda holding: holding.weight_percent,
        reverse=True,
    )
    largest_positions = [
        LargestPosition(
            ticker=holding.ticker,
            name=holding.name,
            sector=holding.sector,
            weight_percent=holding.weight_percent,
        )
        for holding in sorted_holdings[:5]
    ]

    concentration_notes = build_concentration_notes(sorted_holdings)
    sector_notes = build_sector_notes(holdings)
    warnings = build_missing_data_warnings(holdings)
    risk_explanation = build_risk_explanation(
        concentration_notes=concentration_notes,
        sector_notes=sector_notes,
        warnings=warnings,
    )

    return PortfolioRiskSummary(
        concentration_risk_notes=concentration_notes,
        largest_positions=largest_positions,
        sector_concentration_notes=sector_notes,
        missing_data_warnings=warnings,
        risk_explanation=risk_explanation,
        disclaimer="For research and education only. This is not financial advice.",
    )


def build_concentration_notes(holdings: list[Holding]) -> list[str]:
    if not holdings:
        return ["No holdings were provided."]

    notes: list[str] = []
    largest = holdings[0]
    top_three_weight = sum(holding.weight_percent for holding in holdings[:3])

    if largest.weight_percent >= 25:
        notes.append(
            f"{largest.ticker} is the largest position at "
            f"{largest.weight_percent:.1f}%, which creates single-position "
            "concentration risk."
        )
    elif largest.weight_percent >= 15:
        notes.append(
            f"{largest.ticker} is the largest position at "
            f"{largest.weight_percent:.1f}%, so portfolio results may be "
            "meaningfully affected by one holding."
        )
    else:
        notes.append(
            f"The largest position is {largest.ticker} at "
            f"{largest.weight_percent:.1f}%, suggesting no single holding "
            "dominates the portfolio."
        )

    if len(holdings) >= 3 and top_three_weight >= 50:
        notes.append(
            f"The top three positions total {top_three_weight:.1f}%, indicating "
            "elevated concentration in a small number of holdings."
        )
    elif len(holdings) >= 3:
        notes.append(
            f"The top three positions total {top_three_weight:.1f}%, which is a "
            "moderate concentration level based on the supplied weights."
        )

    return notes


def build_sector_notes(holdings: list[Holding]) -> list[str]:
    if not holdings or not any(holding.sector for holding in holdings):
        return []

    sector_weights: dict[str, float] = {}
    for holding in holdings:
        if not holding.sector:
            continue

        sector = holding.sector
        sector_weights[sector] = sector_weights.get(sector, 0.0) + holding.weight_percent

    notes: list[str] = []
    for sector, weight in sorted(
        sector_weights.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        if weight >= 40:
            notes.append(
                f"{sector} represents {weight:.1f}% of the portfolio, creating "
                "sector concentration risk."
            )
        elif weight >= 25:
            notes.append(
                f"{sector} represents {weight:.1f}% of the portfolio, making it "
                "a meaningful sector exposure."
            )

    if not notes:
        notes.append("No sector accounts for 25.0% or more of the portfolio.")

    return notes


def build_missing_data_warnings(holdings: list[Holding]) -> list[str]:
    warnings: list[str] = []

    if any(not holding.sector for holding in holdings):
        warnings.append(
            "One or more holdings are missing sector data, so sector concentration "
            "analysis may be incomplete."
        )

    total_weight = sum(holding.weight_percent for holding in holdings)
    if abs(total_weight - 100.0) > 0.5:
        warnings.append(
            f"Holdings sum to {total_weight:.1f}%, not 100.0%, so the summary "
            "reflects only the supplied weights."
        )

    return warnings


def build_risk_explanation(
    *,
    concentration_notes: list[str],
    sector_notes: list[str],
    warnings: list[str],
) -> str:
    explanation = (
        "This summary evaluates risk from position size and, when available, "
        "sector exposure. Larger position weights can make portfolio performance "
        "more sensitive to a small number of companies."
    )
    if sector_notes:
        explanation += (
            " Sector concentration can add risk when many holdings are exposed to "
            "similar business drivers."
        )
    if warnings:
        explanation += " Missing or incomplete data can limit the reliability of the summary."
    return explanation
