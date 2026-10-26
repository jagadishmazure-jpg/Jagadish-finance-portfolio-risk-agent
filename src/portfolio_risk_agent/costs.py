"""Cost / budget inputs. Negatives are rejected, not clamped or ignored.

A negative cost or budget is a data error (or a sign-flip bug that could
hide spend); silently turning it into zero would corrupt every total
built on it. NaN, infinities, booleans, and non-numbers are rejected too.
"""
from __future__ import annotations

import math


def validate_cost(value, name: str = "cost") -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a number")
    if math.isnan(value) or math.isinf(value):
        raise ValueError(f"{name} must be finite")
    if value < 0:
        raise ValueError(f"{name} must not be negative, got {value}")
    return float(value)


class BudgetExceeded(Exception):
    pass


class RunBudget:
    def __init__(self, total: float):
        self.total = validate_cost(total, "budget total")
        self.spent = 0.0

    def add(self, cost: float) -> float:
        cost = validate_cost(cost, "cost")
        if self.spent + cost > self.total:
            raise BudgetExceeded(f"run cost {self.spent + cost} exceeds budget {self.total}")
        self.spent += cost
        return self.spent

    def estimate(self, steps: int, cost_per_step: float) -> float:
        if isinstance(steps, bool) or not isinstance(steps, int) or steps < 0:
            raise ValueError("steps must be a non-negative integer")
        return steps * validate_cost(cost_per_step, "cost_per_step")
