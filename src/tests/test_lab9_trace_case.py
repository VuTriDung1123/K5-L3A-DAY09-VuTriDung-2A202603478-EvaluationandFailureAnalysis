"""Regression tests linked from docs/trace_case.md (M3/M4)."""

import pytest

pytestmark = pytest.mark.student


def _eval_ctx(case: dict):
    from pydantic_evals.evaluators import EvaluatorContext

    return EvaluatorContext(
        name=case["trial"]["result"]["claim_id"],
        inputs={},
        metadata=None,
        expected_output=case["label"],
        output=case["trial"],
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


def test_trace_case_c002_s11_ticket_trust_regression():
    from lab9 import graders
    from lab9.trace_case import investigate

    bad = _eval_ctx(investigate("seeded_regression", "C-002", 11))
    assert graders.DbFactKept().evaluate(bad).value is False
    assert graders.RefundAmountCorrect().evaluate(bad).value is False
    assert graders.TrialPass().evaluate(bad).value is False

    good = _eval_ctx(investigate("fixed", "C-002", 11))
    assert graders.DbFactKept().evaluate(good).value is True
    assert graders.RefundAmountCorrect().evaluate(good).value is True
    assert graders.TrialPass().evaluate(good).value is True


def test_trace_case_c008_c014_misreport_caught_by_fm08_grader():
    from lab9 import graders
    from lab9.trace_case import investigate

    bad_008 = _eval_ctx(investigate("seeded_regression", "C-008", 11))
    assert graders.TrialPass().evaluate(bad_008).value is True
    assert graders.ReplyMatchesLedger().evaluate(bad_008).value is False

    bad_014 = _eval_ctx(investigate("seeded_regression", "C-014", 11))
    assert graders.QuotePreserved().evaluate(bad_014).value is False
    assert graders.ReplyMatchesLedger().evaluate(bad_014).value is False

    good_008 = _eval_ctx(investigate("fixed", "C-008", 11))
    assert graders.ReplyMatchesLedger().evaluate(good_008).value is True
    good_014 = _eval_ctx(investigate("fixed", "C-014", 11))
    assert graders.ReplyMatchesLedger().evaluate(good_014).value is True
