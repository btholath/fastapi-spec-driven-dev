def calculate_premium(principal: float, term_years: int, annual_rate: float) -> float:
    r = annual_rate / 100  # Convert percentage to decimal
    n = term_years
    if r == 0:
        return principal  # No interest case
    premium = principal * (r / (1 - (1 + r) ** -n))
    return round(premium, 2)