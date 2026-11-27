#### ASSUMPTIONS
# Default-free contractual payments.
#
# A flat SOFR-derived risk-free rate.
#
# Constant historical volatility.
#
# A constant distribution-yield approximation.
#
# Optimal issuer exercise on the specified dates.

import matplotlib
matplotlib.use("QtAgg")
import pandas as pd
import matplotlib.pyplot as plt

### NO CALL TREE VALUE
import numpy as np
from src.certificate import (
    final_fixing_date,
    redemption_date,
)
from src.market_data import (
    valuation_date,
    spot_price,
    risk_free_rate,
    distribution_yield,
    volatility, steps_per_day,
)
from src.pricing import price_non_callable_tree


tree_result = price_non_callable_tree(
    spot_price=spot_price,
    valuation_date=valuation_date,
    final_fixing_date=final_fixing_date,
    redemption_date=redemption_date,
    risk_free_rate=risk_free_rate,
    distribution_yield=distribution_yield,
    volatility=volatility,
    steps_per_day=2,
)

print(f"No-call tree value: USD {tree_result['price']:.2f}")
print(f"Tree steps: {tree_result['n_steps']}")


### NO CALL TREE VALUE AND CALL TREE VALUE
from src.certificate import (
    CALL_OBSERVATION_DATES,
    CALL_EARLY_REDEMPTION_DATES,
    DENOMINATION,
    EARLY_REDEMPTION_COUPON,
)
from src.pricing import (
    price_non_callable_tree,
    price_callable_tree,
)

tree_inputs = {
    "spot_price": spot_price,
    "valuation_date": valuation_date,
    "final_fixing_date": final_fixing_date,
    "redemption_date": redemption_date,
    "risk_free_rate": risk_free_rate,
    "distribution_yield": distribution_yield,
    "volatility": volatility,
    "steps_per_day": 2,
}

no_call_result = price_non_callable_tree(**tree_inputs)

callable_result = price_callable_tree(
    **tree_inputs,
    call_observation_dates=CALL_OBSERVATION_DATES,
    call_payment_dates=CALL_EARLY_REDEMPTION_DATES,
    early_redemption_amount=(
            DENOMINATION + EARLY_REDEMPTION_COUPON
    ),
)

issuer_call_value = (
    no_call_result["price"] - callable_result["price"]
)

print(f"No-call value: USD {no_call_result['price']:.2f}")
print(f"Callable value: USD {callable_result['price']:.2f}")
print(f"Issuer call-right value: USD {issuer_call_value:.2f}")


### TEST OF DIFFERENT RESOLUTIONS - CONVERGENCE

rows = []

for steps_per_day in [1, 2, 3, 4, 6, 8]:
    current_inputs = {
        **tree_inputs,
        "steps_per_day": steps_per_day,
    }

    no_call_result = price_non_callable_tree(**current_inputs)

    callable_result = price_callable_tree(
        **current_inputs,
        call_observation_dates=CALL_OBSERVATION_DATES,
        call_payment_dates=CALL_EARLY_REDEMPTION_DATES,
        early_redemption_amount=(
            DENOMINATION + EARLY_REDEMPTION_COUPON
        ),
    )

    no_call_value = no_call_result["price"]
    callable_value = callable_result["price"]

    assert callable_value <= no_call_value + 1e-10

    rows.append({
        "steps_per_day": steps_per_day,
        "n_steps": no_call_result["n_steps"],
        "no_call_value": no_call_value,
        "callable_value": callable_value,
        "issuer_call_value": no_call_value - callable_value,
    })

convergence = pd.DataFrame(rows)

print(convergence)


convergence["no_call_change"] = (
    convergence["no_call_value"].diff()
)

convergence["callable_change"] = (
    convergence["callable_value"].diff()
)

convergence["call_right_change"] = (
    convergence["issuer_call_value"].diff()
)

print(convergence.round(4))

fig, axes = plt.subplots(1, 2, figsize=(13, 4))

axes[0].plot(
    convergence["n_steps"],
    convergence["no_call_value"],
    marker="o",
    label="Non-callable",
)

axes[0].plot(
    convergence["n_steps"],
    convergence["callable_value"],
    marker="o",
    label="Callable",
)

axes[0].set_title("Certificate values versus tree resolution")
axes[0].set_xlabel("Number of tree steps")
axes[0].set_ylabel("Present value (USD)")
axes[0].legend()
axes[0].grid(alpha=0.3)

axes[1].plot(
    convergence["n_steps"],
    convergence["issuer_call_value"],
    marker="o",
    color="darkorange",
)

axes[1].set_title("Issuer call-right value versus tree resolution")
axes[1].set_xlabel("Number of tree steps")
axes[1].set_ylabel("Present value (USD)")
axes[1].grid(alpha=0.3)

fig.tight_layout()
plt.show()