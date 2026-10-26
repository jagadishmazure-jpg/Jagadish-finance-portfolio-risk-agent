# Purpose

This repo demonstrates one narrow, well-guarded autonomous workflow:
watching portfolio risk exposures on a loop and briefing a human when a
limit is crossed. It is written for risk analysts, engineers, and
reviewers who want to judge an agent by its guardrails, not its claims.

Who it is NOT for: anyone looking for trading signals, execution, or
live market data. This agent cannot place an order, and that absence is
a design feature, tested in `test_agent_never_executes_trades`.
