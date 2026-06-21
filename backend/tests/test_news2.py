"""
Tests for app.services.news2 -- the real, published NEWS2 clinical
scoring system (Royal College of Physicians).

The first test reproduces a documented worked example from real clinical
trial protocol literature, so this isn't just testing our own logic
against itself -- it's testing our implementation against an independently
published reference case.
"""
from app.services.news2 import calculate_news2


def test_matches_published_clinical_example():
    """
    82-year-old COVID-19 patient, documented NEWS2 worked example:
    RR=26, SpO2=95%, SBP=95, Pulse=109, Temp=39, new confusion.
    Official component scores: 3,1,2,1,1,3 = total 11 (excluding the
    +2 supplemental-oxygen modifier, which this module doesn't implement).
    """
    result = calculate_news2(
        respiration_rate=26,
        spo2=95,
        systolic_bp=95,
        pulse=109,
        temperature=39,
        is_alert=False,
    )
    assert result.component_scores["respiration_rate"] == 3
    assert result.component_scores["spo2"] == 1
    assert result.component_scores["systolic_bp"] == 2
    assert result.component_scores["pulse"] == 1
    assert result.component_scores["temperature"] == 1
    assert result.component_scores["consciousness"] == 3
    assert result.total_score == 11
    assert result.risk_level == "HIGH"
    assert result.triage_level == "P1 - IMMEDIATE"


def test_all_normal_vitals_score_zero():
    result = calculate_news2(
        respiration_rate=16, spo2=98, systolic_bp=120,
        pulse=75, temperature=37.0, is_alert=True,
    )
    assert result.total_score == 0
    assert result.risk_level == "LOW"
    assert result.red_flag is False


def test_single_critical_parameter_triggers_red_flag_override():
    """
    A single severely abnormal parameter (score 3) escalates risk level
    even if every other vital is perfectly normal and the total is low --
    this is NEWS2's actual "red score" safety rule, not our invention.
    """
    result = calculate_news2(
        respiration_rate=16, spo2=88, systolic_bp=120,
        pulse=75, temperature=37.0, is_alert=True,
    )
    assert result.total_score == 3
    assert result.red_flag is True
    assert result.risk_level == "LOW-MEDIUM"  # escalated despite low total


def test_missing_vitals_excluded_not_guessed():
    result = calculate_news2(spo2=94, pulse=85)
    assert result.component_scores["respiration_rate"] is None
    assert result.component_scores["systolic_bp"] is None
    assert result.component_scores["temperature"] is None
    assert result.component_scores["consciousness"] is None
    assert result.component_scores["spo2"] == 1
    assert result.component_scores["pulse"] == 0
    assert result.total_score == 1


def test_no_vitals_at_all_scores_zero_not_error():
    result = calculate_news2()
    assert result.total_score == 0
    assert result.red_flag is False
    assert all(v is None for v in result.component_scores.values())


def test_medium_risk_threshold():
    # total exactly 5, no single param at 3 -- should be MEDIUM, not HIGH
    result = calculate_news2(
        respiration_rate=22,  # score 2
        spo2=95,               # score 1
        systolic_bp=105,       # score 1
        pulse=95,               # score 1
        temperature=37.0,      # score 0
        is_alert=True,          # score 0
    )
    assert result.total_score == 5
    assert result.risk_level == "MEDIUM"
    assert result.triage_level == "P2 - URGENT"


def test_high_risk_threshold():
    result = calculate_news2(
        respiration_rate=22,  # 2
        spo2=93,                # 2
        systolic_bp=105,        # 1
        pulse=95,                # 1
        temperature=38.5,        # 1
        is_alert=True,            # 0
    )
    assert result.total_score == 7
    assert result.risk_level == "HIGH"
