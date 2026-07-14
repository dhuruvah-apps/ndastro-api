"""Unit tests for ndastro_api.services.muhurta_range.

All ephemeris and external calls are patched so the tests run offline and
deterministically.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from ndastro_api.services.muhurta_range import (
    _EventCriteria,
    _build_reasons,
    _calculate_favorable_horas,
    _calculate_tara_bala,
    _compute_score,
    _compute_timing_windows_cached,
    _enrich_timing,
    _evaluate_date_cached,
    _is_combust,
    _summarize,
    EventType,
    TimeWindowSummary,
    search_auspicious_dates,
)


@pytest.fixture(autouse=True)
def _clear_evaluate_cache() -> None:
    """Clear lru_caches before and after every test."""
    _evaluate_date_cached.cache_clear()
    _compute_timing_windows_cached.cache_clear()
    yield
    _evaluate_date_cached.cache_clear()
    _compute_timing_windows_cached.cache_clear()
from ndastro_api.services.panchanga import (
    PanchangaActivitySupport,
    PanchangaResult,
    TithiResult,
    VaraResult,
)


# ---------------------------------------------------------------------------
# Helpers to build minimal mock panchanga objects
# ---------------------------------------------------------------------------

def _make_tithi(number: int = 2, name: str = "Dwitiya", paksha: str = "shukla") -> TithiResult:
    return TithiResult(
        number=number,
        name=name,
        paksha=paksha,
        phase_degrees=12.0,
        start_degree=(number - 1) * 12.0,
        end_degree=number * 12.0,
    )


def _make_panchanga(tithi_number: int = 2, vara_number: int = 5, paksha: str = "shukla") -> PanchangaResult:
    from ndastro_api.services.panchanga import KaranaResult
    tithi = _make_tithi(tithi_number, paksha=paksha)
    vara = VaraResult(number=vara_number, name={1: "Sunday", 2: "Monday", 3: "Tuesday", 4: "Wednesday", 5: "Thursday", 6: "Friday", 7: "Saturday"}[vara_number])
    karana = KaranaResult(number=1, name="Bava", start_degree=0.0, end_degree=6.0)
    return PanchangaResult(tithi=tithi, karana=karana, vara=vara, yoga_name="Siddhi", yoga_number=16)


def _make_panchanga_data(tithi_number: int = 2, vara_number: int = 5, paksha: str = "shukla", muhurta_rating: float | None = 8.0):
    from ndastro_api.services.panchanga import PanchangaDataResult
    p = _make_panchanga(tithi_number, vara_number, paksha)
    return PanchangaDataResult(
        panchanga=p,
        tithi_data=None,
        karana_data=None,
        vara_data=None,
        yoga_data=None,
        muhurta_rating=muhurta_rating,
    )


def _make_activity_support(
    *,
    tithi_support: bool = False,
    karana_support: bool = False,
    vara_support: bool = False,
    yoga_support: bool = False,
    inauspicious_flags: list[str] | None = None,
) -> PanchangaActivitySupport:
    return PanchangaActivitySupport(
        activity="marriage",
        tithi_support=tithi_support,
        karana_support=karana_support,
        vara_support=vara_support,
        yoga_support=yoga_support,
        inauspicious_flags=inauspicious_flags or [],
    )


# ---------------------------------------------------------------------------
# _compute_score
# ---------------------------------------------------------------------------

class TestComputeScore:
    def test_uses_base_when_no_criteria(self) -> None:
        pdata = _make_panchanga_data(muhurta_rating=7.0)
        assert _compute_score(pdata, nakshatra=1, criteria=None) == 7.0

    def test_falls_back_to_5_when_rating_is_none(self) -> None:
        pdata = _make_panchanga_data(muhurta_rating=None)
        assert _compute_score(pdata, nakshatra=99, criteria=None) == 5.0

    def test_adds_good_tithi_bonus(self) -> None:
        # Tithi 2 is in MARRIAGE good_tithis
        pdata = _make_panchanga_data(tithi_number=2, vara_number=3, muhurta_rating=7.0)  # Tue = bad vara for marriage
        from ndastro_api.services.muhurta_range import _EVENT_CRITERIA
        criteria = _EVENT_CRITERIA[EventType.MARRIAGE]
        score = _compute_score(pdata, nakshatra=1, criteria=criteria)
        # base 7 + tithi +2 + vara -2 + nak 0 + paksha +0.5 = 7.5
        assert score == pytest.approx(7.5)

    def test_penalises_bad_tithi(self) -> None:
        # Tithi 4 is Rikta — bad for marriage
        pdata = _make_panchanga_data(tithi_number=4, vara_number=5, muhurta_rating=8.0, paksha="shukla")
        from ndastro_api.services.muhurta_range import _EVENT_CRITERIA
        criteria = _EVENT_CRITERIA[EventType.MARRIAGE]
        score = _compute_score(pdata, nakshatra=1, criteria=criteria)
        # base 8 + tithi -2 + vara +2 + nak 0 + paksha +0.5 = 8.5
        assert score == pytest.approx(8.5)

    def test_adds_good_nakshatra_bonus(self) -> None:
        # Nakshatra 4 (Rohini) is good for HOUSE_WARMING
        pdata = _make_panchanga_data(tithi_number=2, vara_number=5, muhurta_rating=7.0)
        from ndastro_api.services.muhurta_range import _EVENT_CRITERIA
        criteria = _EVENT_CRITERIA[EventType.HOUSE_WARMING]
        score = _compute_score(pdata, nakshatra=4, criteria=criteria)
        # base 7 + tithi +2 + vara +2 + nak +2 + paksha +0.5 = 13.5
        assert score == pytest.approx(13.5)

    def test_score_floored_at_zero(self) -> None:
        pdata = _make_panchanga_data(tithi_number=4, vara_number=7, muhurta_rating=0.0, paksha="krishna")
        from ndastro_api.services.muhurta_range import _EVENT_CRITERIA
        criteria = _EVENT_CRITERIA[EventType.MARRIAGE]
        score = _compute_score(pdata, nakshatra=1, criteria=criteria)
        assert score >= 0.0

    def test_krishna_paksha_no_bonus(self) -> None:
        pdata = _make_panchanga_data(tithi_number=2, vara_number=5, muhurta_rating=8.0, paksha="krishna")
        from ndastro_api.services.muhurta_range import _EVENT_CRITERIA
        criteria = _EVENT_CRITERIA[EventType.MARRIAGE]
        score_shukla = _compute_score(_make_panchanga_data(tithi_number=2, vara_number=5, muhurta_rating=8.0, paksha="shukla"), nakshatra=1, criteria=criteria)
        score_krishna = _compute_score(pdata, nakshatra=1, criteria=criteria)
        assert score_shukla - score_krishna == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# _build_reasons
# ---------------------------------------------------------------------------

class TestBuildReasons:
    def _criteria(self) -> _EventCriteria:
        from ndastro_api.services.muhurta_range import _EVENT_CRITERIA
        return _EVENT_CRITERIA[EventType.MARRIAGE]

    def test_good_tithi_generates_reason(self) -> None:
        pdata = _make_panchanga_data(tithi_number=2, vara_number=2)
        support = _make_activity_support()
        reasons, cautions = _build_reasons(pdata, support, nakshatra=1, criteria=self._criteria(), activity_key="marriage")
        assert any("Tithi" in r and "auspicious" in r for r in reasons)
        assert not any("inauspicious" in c for c in cautions if "Tithi" in c)

    def test_bad_tithi_generates_caution(self) -> None:
        pdata = _make_panchanga_data(tithi_number=6, vara_number=2)  # Tithi 6 in bad list for marriage
        support = _make_activity_support()
        reasons, cautions = _build_reasons(pdata, support, nakshatra=1, criteria=self._criteria(), activity_key="marriage")
        assert any("inauspicious" in c for c in cautions)

    def test_good_vara_generates_reason(self) -> None:
        pdata = _make_panchanga_data(tithi_number=2, vara_number=5)  # Thursday = good for marriage
        support = _make_activity_support()
        reasons, cautions = _build_reasons(pdata, support, nakshatra=1, criteria=self._criteria(), activity_key="marriage")
        assert any("Vara" in r and "favorable" in r for r in reasons)

    def test_bad_vara_generates_caution(self) -> None:
        pdata = _make_panchanga_data(tithi_number=2, vara_number=7)  # Saturday = bad for marriage
        support = _make_activity_support()
        reasons, cautions = _build_reasons(pdata, support, nakshatra=1, criteria=self._criteria(), activity_key="marriage")
        assert any("Vara" in c and "unfavorable" in c for c in cautions)

    def test_good_nakshatra_generates_reason(self) -> None:
        pdata = _make_panchanga_data(tithi_number=2, vara_number=5)
        support = _make_activity_support()
        reasons, cautions = _build_reasons(pdata, support, nakshatra=4, criteria=self._criteria(), activity_key="marriage")
        assert any("Nakshatra 4" in r for r in reasons)

    def test_shukla_paksha_generates_reason(self) -> None:
        pdata = _make_panchanga_data(paksha="shukla")
        support = _make_activity_support()
        reasons, _ = _build_reasons(pdata, support, nakshatra=1, criteria=self._criteria(), activity_key="marriage")
        assert any("Shukla Paksha" in r for r in reasons)

    def test_krishna_paksha_generates_caution(self) -> None:
        pdata = _make_panchanga_data(paksha="krishna")
        support = _make_activity_support()
        _, cautions = _build_reasons(pdata, support, nakshatra=1, criteria=self._criteria(), activity_key="marriage")
        assert any("Krishna Paksha" in c for c in cautions)

    def test_rikta_tithi_caution(self) -> None:
        for rikta in (4, 9, 14):
            pdata = _make_panchanga_data(tithi_number=rikta)
            support = _make_activity_support()
            _, cautions = _build_reasons(pdata, support, nakshatra=1, criteria=self._criteria(), activity_key="marriage")
            assert any("Rikta" in c for c in cautions)

    def test_inauspicious_flag_propagates(self) -> None:
        pdata = _make_panchanga_data()
        support = _make_activity_support(inauspicious_flags=["tithi"])
        _, cautions = _build_reasons(pdata, support, nakshatra=1, criteria=self._criteria(), activity_key="marriage")
        assert any("Tithi element is inauspicious" in c for c in cautions)


# ---------------------------------------------------------------------------
# _summarize
# ---------------------------------------------------------------------------

class TestSummarize:
    def test_returns_none_for_none(self) -> None:
        assert _summarize(None) is None

    def test_returns_none_when_start_missing(self) -> None:
        tw = SimpleNamespace(end=datetime(2026, 7, 1, 8, 0, tzinfo=UTC), name="test")
        assert _summarize(tw) is None

    def test_maps_fields(self) -> None:
        start = datetime(2026, 7, 1, 6, 0, tzinfo=UTC)
        end = datetime(2026, 7, 1, 7, 30, tzinfo=UTC)
        tw = SimpleNamespace(name="rahu_kalam", start=start, end=end)
        result = _summarize(tw)
        assert isinstance(result, TimeWindowSummary)
        assert result.name == "rahu_kalam"
        assert result.duration_minutes == pytest.approx(90.0)


# ---------------------------------------------------------------------------
# search_auspicious_dates — validation
# ---------------------------------------------------------------------------

class TestSearchAuspiciousDatesValidation:
    def test_raises_when_end_before_start(self) -> None:
        with pytest.raises(ValueError, match="end_date must be on or after start_date"):
            search_auspicious_dates(
                start_date=date(2026, 8, 1),
                end_date=date(2026, 7, 1),
                lat=12.97,
                lon=77.59,
                ayanamsa_system="lahiri",
                event=EventType.MARRIAGE,
            )

    def test_raises_when_range_exceeds_365_days(self) -> None:
        with pytest.raises(ValueError, match="365 days"):
            search_auspicious_dates(
                start_date=date(2026, 1, 1),
                end_date=date(2027, 6, 1),  # > 365 days
                lat=12.97,
                lon=77.59,
                ayanamsa_system="lahiri",
                event=EventType.MARRIAGE,
            )

    def test_same_day_range_is_valid(self) -> None:
        with patch("ndastro_api.services.muhurta_range._evaluate_date_cached", return_value=None):
            result = search_auspicious_dates(
                start_date=date(2026, 8, 1),
                end_date=date(2026, 8, 1),
                lat=12.97,
                lon=77.59,
                ayanamsa_system="lahiri",
                event=EventType.MARRIAGE,
            )
        assert result == ()


# ---------------------------------------------------------------------------
# search_auspicious_dates — ordering and filtering
# ---------------------------------------------------------------------------

def _make_result(score: float, d: str = "2026-08-01") -> object:
    """Build a minimal AuspiciousDateResult-like object for sorting tests."""
    from ndastro_api.services.muhurta_range import AuspiciousDateResult
    return AuspiciousDateResult(
        date=d, event="marriage", score=score,
        tithi_number=2, tithi_name="Dwitiya", paksha="shukla",
        vara_number=5, vara_name="Thursday",
        nakshatra=4, yoga_name="Siddhi", yoga_number=16,
        muhurta_rating=8.0,
        tithi_support=True, karana_support=False, vara_support=True, yoga_support=False,
        inauspicious_flags=[], supporting_reasons=[], caution_reasons=[],
        abhijit_muhurta=None, rahu_kalam=None, yamagandam=None, gulika=None,
        sunrise=None, sunset=None,
    )


class TestSearchAuspiciousDatesOrdering:
    def _patch_evaluate(self, scores: list[float]) -> list:
        results = [_make_result(s, f"2026-08-0{i+1}") for i, s in enumerate(scores)]
        return results

    def test_results_sorted_by_score_descending(self) -> None:
        results = self._patch_evaluate([5.0, 12.0, 8.0])
        side_effects = results + [None]  # extra None to stop loop if needed

        with patch("ndastro_api.services.muhurta_range._evaluate_date_cached", side_effect=side_effects):
            output = search_auspicious_dates(
                start_date=date(2026, 8, 1),
                end_date=date(2026, 8, 3),
                lat=12.97, lon=77.59,
                ayanamsa_system="lahiri",
                event=EventType.MARRIAGE,
            )

        assert [r.score for r in output] == [12.0, 8.0, 5.0]

    def test_min_score_filters_out_low_results(self) -> None:
        results = self._patch_evaluate([5.0, 12.0, 8.0])
        with patch("ndastro_api.services.muhurta_range._evaluate_date_cached", side_effect=results):
            output = search_auspicious_dates(
                start_date=date(2026, 8, 1),
                end_date=date(2026, 8, 3),
                lat=12.97, lon=77.59,
                ayanamsa_system="lahiri",
                event=EventType.MARRIAGE,
                min_score=8.0,
            )
        assert all(r.score >= 8.0 for r in output)
        assert len(output) == 2

    def test_limit_caps_results(self) -> None:
        results = [_make_result(float(i), f"2026-08-{i:02d}") for i in range(1, 11)]
        with patch("ndastro_api.services.muhurta_range._evaluate_date_cached", side_effect=results):
            output = search_auspicious_dates(
                start_date=date(2026, 8, 1),
                end_date=date(2026, 8, 10),
                lat=12.97, lon=77.59,
                ayanamsa_system="lahiri",
                event=EventType.MARRIAGE,
                limit=3,
            )
        assert len(output) == 3

    def test_none_results_from_evaluate_are_skipped(self) -> None:
        good = _make_result(10.0, "2026-08-01")
        with patch("ndastro_api.services.muhurta_range._evaluate_date_cached", side_effect=[None, good, None]):
            output = search_auspicious_dates(
                start_date=date(2026, 8, 1),
                end_date=date(2026, 8, 3),
                lat=12.97, lon=77.59,
                ayanamsa_system="lahiri",
                event=EventType.MARRIAGE,
            )
        assert len(output) == 1
        assert output[0].score == 10.0


# ---------------------------------------------------------------------------
# Event criteria completeness
# ---------------------------------------------------------------------------

class TestEventCriteriaCoverage:
    def test_all_event_types_have_criteria(self) -> None:
        from ndastro_api.services.muhurta_range import _EVENT_CRITERIA
        for event in EventType:
            assert event in _EVENT_CRITERIA, f"Missing criteria for {event}"

    def test_good_and_bad_tithis_do_not_overlap(self) -> None:
        from ndastro_api.services.muhurta_range import _EVENT_CRITERIA
        for event, criteria in _EVENT_CRITERIA.items():
            overlap = criteria.good_tithis & criteria.bad_tithis
            assert not overlap, f"{event}: good/bad tithi overlap: {overlap}"

    def test_good_and_bad_varas_do_not_overlap(self) -> None:
        from ndastro_api.services.muhurta_range import _EVENT_CRITERIA
        for event, criteria in _EVENT_CRITERIA.items():
            overlap = criteria.good_varas & criteria.bad_varas
            assert not overlap, f"{event}: good/bad vara overlap: {overlap}"

    def test_tithi_numbers_in_valid_range(self) -> None:
        from ndastro_api.services.muhurta_range import _EVENT_CRITERIA
        for event, criteria in _EVENT_CRITERIA.items():
            all_tithis = criteria.good_tithis | criteria.bad_tithis
            assert all(1 <= t <= 30 for t in all_tithis), f"{event}: tithi out of range"

    def test_vara_numbers_in_valid_range(self) -> None:
        from ndastro_api.services.muhurta_range import _EVENT_CRITERIA
        for event, criteria in _EVENT_CRITERIA.items():
            all_varas = criteria.good_varas | criteria.bad_varas
            assert all(1 <= v <= 7 for v in all_varas), f"{event}: vara out of range"

    def test_nakshatra_numbers_in_valid_range(self) -> None:
        from ndastro_api.services.muhurta_range import _EVENT_CRITERIA
        for event, criteria in _EVENT_CRITERIA.items():
            assert all(1 <= n <= 27 for n in criteria.good_nakshatras), f"{event}: nakshatra out of range"


# ---------------------------------------------------------------------------
# _calculate_tara_bala
# ---------------------------------------------------------------------------

class TestCalculateTaraBala:
    def test_same_nakshatra_is_janma_tara(self) -> None:
        result = _calculate_tara_bala(7, 7)
        assert result.tara_number == 1
        assert result.tara_name == "Janma"
        assert result.is_auspicious is False

    def test_second_nakshatra_is_sampat(self) -> None:
        result = _calculate_tara_bala(1, 2)  # count=2, tara=2
        assert result.tara_number == 2
        assert result.tara_name == "Sampat"
        assert result.is_auspicious is True

    def test_third_nakshatra_is_vipat_inauspicious(self) -> None:
        result = _calculate_tara_bala(1, 3)
        assert result.tara_number == 3
        assert result.is_auspicious is False

    def test_wraps_around_27(self) -> None:
        # janma=25, current=2: count = ((2-25)%27)+1 = (4%27)+1 = 5 → tara 5 = Pratyak
        result = _calculate_tara_bala(25, 2)
        assert result.tara_number == 5

    def test_all_9_tara_numbers_covered(self) -> None:
        seen = set()
        for current in range(1, 28):
            r = _calculate_tara_bala(1, current)
            seen.add(r.tara_number)
        assert seen == set(range(1, 10))


# ---------------------------------------------------------------------------
# _calculate_favorable_horas
# ---------------------------------------------------------------------------

class TestCalculateFavorableHoras:
    def test_returns_empty_when_no_sunrise(self) -> None:
        from ndastro_api.services.muhurta_range import _calculate_favorable_horas
        from datetime import date
        result = _calculate_favorable_horas(date(2026, 8, 1), None, "marriage")
        assert result == []

    def test_returns_only_favorable_lords(self) -> None:
        from datetime import date
        # Thursday 2026-08-06, sunrise at 06:00 UTC
        sunrise = "2026-08-06T06:00:00+00:00"
        result = _calculate_favorable_horas(date(2026, 8, 6), sunrise, "marriage")
        # marriage lords: JU, VE, ME
        for h in result:
            assert h.lord_code in {"JU", "VE", "ME"}

    def test_24_total_horas_per_day(self) -> None:
        from datetime import date
        sunrise = "2026-08-06T06:00:00+00:00"
        # business_start has 2 lords (ME, JU) → each appears ~3 times = ~6-7 total
        result = _calculate_favorable_horas(date(2026, 8, 6), sunrise, "business_start")
        # hora_numbers must be between 1 and 24
        assert all(1 <= h.hora_number <= 24 for h in result)
        # all horas must be 60 minutes
        assert all(h.duration_minutes == 60.0 for h in result)

    def test_unknown_event_returns_empty(self) -> None:
        from datetime import date
        result = _calculate_favorable_horas(date(2026, 8, 6), "2026-08-06T06:00:00+00:00", "unknown_event")
        assert result == []


# ---------------------------------------------------------------------------
# _is_combust
# ---------------------------------------------------------------------------

class TestIsCombust:
    def test_planet_within_threshold_is_combust(self) -> None:
        # Sun at 0°, Jupiter at 10° — within 11° threshold
        assert _is_combust(0.0, 10.0, 11.0) is True

    def test_planet_at_exact_threshold_is_combust(self) -> None:
        assert _is_combust(0.0, 11.0, 11.0) is True

    def test_planet_just_outside_threshold_is_not_combust(self) -> None:
        assert _is_combust(0.0, 11.5, 11.0) is False

    def test_arc_measured_on_shorter_side(self) -> None:
        # Sun at 350°, planet at 5° — arc = 15°, not 345°
        assert _is_combust(350.0, 5.0, 16.0) is True
        assert _is_combust(350.0, 5.0, 14.0) is False

    def test_venus_combust_threshold(self) -> None:
        # Venus threshold = 8°
        assert _is_combust(100.0, 107.9, 8.0) is True
        assert _is_combust(100.0, 108.5, 8.0) is False


# ---------------------------------------------------------------------------
# Combustion score penalty (_compute_score extended signature)
# ---------------------------------------------------------------------------

class TestCombustionScorePenalty:
    def _f2_criteria(self) -> _EventCriteria:
        from ndastro_api.services.muhurta_range import _EVENT_CRITERIA
        return _EVENT_CRITERIA[EventType.MARRIAGE]

    def test_no_penalty_when_no_combustion(self) -> None:
        pdata = _make_panchanga_data(tithi_number=2, vara_number=5, muhurta_rating=8.0)
        score_base = _compute_score(pdata, 4, self._f2_criteria(), False, False, EventType.MARRIAGE)
        score_none = _compute_score(pdata, 4, self._f2_criteria())
        assert score_base == pytest.approx(score_none)

    def test_jupiter_combust_reduces_score_for_f2_event(self) -> None:
        pdata = _make_panchanga_data(tithi_number=2, vara_number=5, muhurta_rating=8.0)
        score_clean = _compute_score(pdata, 4, self._f2_criteria(), False, False, EventType.MARRIAGE)
        score_combust = _compute_score(pdata, 4, self._f2_criteria(), True, False, EventType.MARRIAGE)
        assert score_clean - score_combust == pytest.approx(1.0)

    def test_venus_combust_reduces_score_for_f2_event(self) -> None:
        pdata = _make_panchanga_data(tithi_number=2, vara_number=5, muhurta_rating=8.0)
        score_clean = _compute_score(pdata, 4, self._f2_criteria(), False, False, EventType.MARRIAGE)
        score_combust = _compute_score(pdata, 4, self._f2_criteria(), False, True, EventType.MARRIAGE)
        assert score_clean - score_combust == pytest.approx(1.0)

    def test_both_combust_reduces_score_by_two(self) -> None:
        pdata = _make_panchanga_data(tithi_number=2, vara_number=5, muhurta_rating=8.0)
        score_clean = _compute_score(pdata, 4, self._f2_criteria(), False, False, EventType.MARRIAGE)
        score_combust = _compute_score(pdata, 4, self._f2_criteria(), True, True, EventType.MARRIAGE)
        assert score_clean - score_combust == pytest.approx(2.0)

    def test_combust_has_no_penalty_for_non_f2_event(self) -> None:
        from ndastro_api.services.muhurta_range import _EVENT_CRITERIA
        criteria = _EVENT_CRITERIA[EventType.CONSTRUCTION]  # F1 event
        pdata = _make_panchanga_data(tithi_number=2, vara_number=4, muhurta_rating=8.0)
        score_clean = _compute_score(pdata, 4, criteria, False, False, EventType.CONSTRUCTION)
        score_combust = _compute_score(pdata, 4, criteria, True, True, EventType.CONSTRUCTION)
        assert score_clean == pytest.approx(score_combust)


# ---------------------------------------------------------------------------
# Disha Shool detection (_enrich_timing)
# ---------------------------------------------------------------------------

def _make_full_result(event: str = "travel", moon_rashi: int = 3) -> object:
    from ndastro_api.core.models.muhurta import AuspiciousDateResult
    return AuspiciousDateResult(
        date="2026-08-06", event=event, score=10.0,
        tithi_number=2, tithi_name="Dwitiya", paksha="shukla",
        vara_number=5, vara_name="Thursday",
        nakshatra=4, yoga_name="Siddhi", yoga_number=16,
        muhurta_rating=8.0, moon_rashi=moon_rashi,
        tithi_support=True, karana_support=False, vara_support=True, yoga_support=False,
        inauspicious_flags=[], supporting_reasons=[], caution_reasons=[],
        abhijit_muhurta=None, rahu_kalam=None, yamagandam=None, gulika=None,
        sunrise=None, sunset=None,
    )


class TestDishaShoool:
    """Disha Shool tests go through _enrich_timing."""

    def _tw(self, sunrise: str = "2026-08-06T06:00:00+00:00"):
        from ndastro_api.services.muhurta_range import _TimingWindows
        return _TimingWindows(
            abhijit_muhurta=None, rahu_kalam=None, yamagandam=None,
            gulika=None, amrita_kala=(), sunrise=sunrise, sunset=None,
        )

    def test_no_conflict_when_direction_is_safe(self) -> None:
        # 2026-08-06 is Thursday (weekday=3) → Disha Shool = East
        result = _make_full_result("travel")
        with patch("ndastro_api.services.muhurta_range._compute_timing_windows_cached", return_value=self._tw()):
            enriched = _enrich_timing(result, 12.97, 77.59, travel_direction="north")
        assert enriched.disha_shool_direction == "east"
        assert enriched.disha_shool_conflict is False

    def test_conflict_when_travelling_toward_shool_direction(self) -> None:
        result = _make_full_result("travel")
        with patch("ndastro_api.services.muhurta_range._compute_timing_windows_cached", return_value=self._tw()):
            enriched = _enrich_timing(result, 12.97, 77.59, travel_direction="east")
        assert enriched.disha_shool_conflict is True
        assert any("Disha Shool" in c for c in enriched.caution_reasons)

    def test_disha_shool_not_set_for_non_travel_event(self) -> None:
        result = _make_full_result("marriage")
        with patch("ndastro_api.services.muhurta_range._compute_timing_windows_cached", return_value=self._tw()):
            enriched = _enrich_timing(result, 12.97, 77.59, travel_direction="east")
        assert enriched.disha_shool_direction is None
        assert enriched.disha_shool_conflict is None


# ---------------------------------------------------------------------------
# Moon body-part surgery rule (_enrich_timing)
# ---------------------------------------------------------------------------

class TestMoonBodyPartSurgery:
    def _tw(self):
        from ndastro_api.services.muhurta_range import _TimingWindows
        return _TimingWindows(
            abhijit_muhurta=None, rahu_kalam=None, yamagandam=None,
            gulika=None, amrita_kala=(), sunrise=None, sunset=None,
        )

    def test_caution_when_moon_in_surgery_rashi(self) -> None:
        # moon_rashi=5 → Leo → heart
        result = _make_full_result("surgery", moon_rashi=5)
        with patch("ndastro_api.services.muhurta_range._compute_timing_windows_cached", return_value=self._tw()):
            enriched = _enrich_timing(result, 12.97, 77.59, surgery_body_part="heart")
        assert enriched.moon_body_part == "heart"
        assert any("heart" in c for c in enriched.caution_reasons)

    def test_no_caution_when_moon_in_different_rashi(self) -> None:
        # moon_rashi=1 → Aries → head, operating on heart
        result = _make_full_result("surgery", moon_rashi=1)
        with patch("ndastro_api.services.muhurta_range._compute_timing_windows_cached", return_value=self._tw()):
            enriched = _enrich_timing(result, 12.97, 77.59, surgery_body_part="heart")
        assert enriched.moon_body_part is None

    def test_not_triggered_for_non_surgery_event(self) -> None:
        result = _make_full_result("marriage", moon_rashi=5)
        with patch("ndastro_api.services.muhurta_range._compute_timing_windows_cached", return_value=self._tw()):
            enriched = _enrich_timing(result, 12.97, 77.59, surgery_body_part="heart")
        assert enriched.moon_body_part is None


# ---------------------------------------------------------------------------
# Lagna windows — single-day vs multi-day
# ---------------------------------------------------------------------------

class TestLagnaWindows:
    def test_lagna_windows_populated_for_single_day(self) -> None:
        from ndastro_api.core.models.muhurta import LagnaWindow
        mock_lagna = (
            LagnaWindow(sign_number=5, sign_name="Leo", is_favorable=True,
                        start="2026-08-06T07:00:00+00:00", end="2026-08-06T09:00:00+00:00",
                        duration_minutes=120.0),
        )
        mock_result = _make_result(10.0, "2026-08-06")
        with patch("ndastro_api.services.muhurta_range._evaluate_date_cached", return_value=mock_result), \
             patch("ndastro_api.services.muhurta_range._enrich_timing", side_effect=lambda r, *a, **kw: r), \
             patch("ndastro_api.services.muhurta_range._compute_lagna_windows", return_value=mock_lagna):
            results = search_auspicious_dates(
                start_date=date(2026, 8, 6),
                end_date=date(2026, 8, 6),
                lat=12.97, lon=77.59,
                ayanamsa_system="lahiri",
                event=EventType.MARRIAGE,
            )
        assert len(results) == 1
        assert results[0].lagna_windows == mock_lagna

    def test_lagna_windows_empty_for_multi_day(self) -> None:
        results_mock = [_make_result(10.0, "2026-08-06"), _make_result(9.0, "2026-08-07")]
        with patch("ndastro_api.services.muhurta_range._evaluate_date_cached", side_effect=results_mock), \
             patch("ndastro_api.services.muhurta_range._enrich_timing", side_effect=lambda r, *a, **kw: r), \
             patch("ndastro_api.services.muhurta_range._compute_lagna_windows") as mock_lagna_fn:
            search_auspicious_dates(
                start_date=date(2026, 8, 6),
                end_date=date(2026, 8, 7),
                lat=12.97, lon=77.59,
                ayanamsa_system="lahiri",
                event=EventType.MARRIAGE,
            )
        mock_lagna_fn.assert_not_called()
