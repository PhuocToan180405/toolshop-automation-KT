Feature: Shopping cart calculations
  As a shopper
  I want my cart to calculate line totals and total price correctly
  So that I know how much I need to pay before checking out

  Background:
    Given I am on the home page

  Scenario Outline: Adding a product calculates line total and cart total correctly
    When I search for "<product>"
    And I open the product "<product>"
    And I add it to the cart with quantity <quantity>
    And I go to the cart
    Then the cart item "<product>" has line price matching unit price times quantity <quantity>
    And the cart total equals the line price

    Examples:
      | product            | quantity |
      | Combination Pliers | 1        |
      | Claw Hammer        | 3        |
