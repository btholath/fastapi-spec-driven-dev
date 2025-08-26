Feature: Annuity Premium Calculation
  As a financial advisor
  I want to calculate annuity premiums via an API
  So that I can provide accurate quotes to clients

  Scenario: Calculate premium for a fixed annuity
    Given a logged-in user
    When they submit an annuity request with principal $10000, term 5 years, and rate 3%
    Then the API returns a premium of $2124.60