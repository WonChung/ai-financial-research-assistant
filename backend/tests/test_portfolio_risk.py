from fastapi.testclient import TestClient

from app.main import app


def test_portfolio_risk_summary_returns_concentration_and_sector_notes() -> None:
    client = TestClient(app)

    response = client.post(
        "/portfolio/risk-summary",
        json={
            "holdings": [
                {
                    "ticker": "AAPL",
                    "name": "Apple",
                    "sector": "Technology",
                    "weight_percent": 30,
                },
                {
                    "ticker": "MSFT",
                    "name": "Microsoft",
                    "sector": "Technology",
                    "weight_percent": 25,
                },
                {
                    "ticker": "JPM",
                    "name": "JPMorgan Chase",
                    "sector": "Financials",
                    "weight_percent": 20,
                },
                {
                    "ticker": "JNJ",
                    "name": "Johnson & Johnson",
                    "sector": "Health Care",
                    "weight_percent": 15,
                },
                {
                    "ticker": "PG",
                    "name": "Procter & Gamble",
                    "sector": "Consumer Staples",
                    "weight_percent": 10,
                },
            ]
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["largest_positions"][0] == {
        "ticker": "AAPL",
        "name": "Apple",
        "sector": "Technology",
        "weight_percent": 30.0,
    }
    assert len(data["largest_positions"]) == 5
    assert any("AAPL" in note for note in data["concentration_risk_notes"])
    assert data["sector_concentration_notes"] == [
        "Technology represents 55.0% of the portfolio, creating sector concentration risk."
    ]
    assert data["missing_data_warnings"] == []
    assert "buy" not in data["risk_explanation"].lower()
    assert "sell" not in data["risk_explanation"].lower()
    assert data["disclaimer"] == (
        "For research and education only. This is not financial advice."
    )


def test_portfolio_risk_summary_warns_about_missing_sector_and_weight_total() -> None:
    client = TestClient(app)

    response = client.post(
        "/portfolio/risk-summary",
        json={
            "holdings": [
                {
                    "ticker": "AAPL",
                    "name": "Apple",
                    "weight_percent": 40,
                },
                {
                    "ticker": "MSFT",
                    "name": "Microsoft",
                    "sector": "Technology",
                    "weight_percent": 20,
                },
            ]
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["sector_concentration_notes"] == [
        "No sector accounts for 25.0% or more of the portfolio."
    ]
    assert data["missing_data_warnings"] == [
        "One or more holdings are missing sector data, so sector concentration analysis may be incomplete.",
        "Holdings sum to 60.0%, not 100.0%, so the summary reflects only the supplied weights.",
    ]


def test_portfolio_risk_summary_rejects_empty_holdings() -> None:
    client = TestClient(app)

    response = client.post("/portfolio/risk-summary", json={"holdings": []})

    assert response.status_code == 400
    assert response.json() == {"detail": "At least one holding is required."}


def test_portfolio_risk_summary_rejects_invalid_weight() -> None:
    client = TestClient(app)

    response = client.post(
        "/portfolio/risk-summary",
        json={
            "holdings": [
                {
                    "ticker": "AAPL",
                    "name": "Apple",
                    "sector": "Technology",
                    "weight_percent": 0,
                }
            ]
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "holding 1 weight_percent must be greater than 0."
    }
