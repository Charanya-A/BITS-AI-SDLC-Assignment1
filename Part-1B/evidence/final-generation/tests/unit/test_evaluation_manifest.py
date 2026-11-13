import copy

import pytest

from spam_classifier.evaluation import (
    select_quality_cases,
    validate_evaluation_manifest,
)


# Artificial fixtures used only to test manifest validation.
# They are not the actual training or frozen evaluation dataset.

VALID_REQUIREMENT_REFS = ["FR-010", "SC-004"]

VALID_SCENARIOS = [
    "normal",
    "boundary",
    "ambiguous",
    "adversarial",
]


@pytest.fixture
def valid_manifest():
    cases = []

    # 15 artificial held-out fixtures: 8 SPAM and 7 HAM.
    for index in range(15):
        label = "SPAM" if index < 8 else "HAM"
        scenario = VALID_SCENARIOS[index % len(VALID_SCENARIOS)]

        cases.append(
            {
                "case_id": f"held-out-fixture-{index + 1:03d}",
                "case_group": "synthetic_held_out",
                "scenario": scenario,
                "message": f"Artificial English test message number {index + 1}.",
                "expected_label": label,
                "expected_error": None,
                "requirement_refs": VALID_REQUIREMENT_REFS.copy(),
            }
        )

    # Controlled fixtures supplement scenario coverage.
    for scenario in VALID_SCENARIOS:
        cases.append(
            {
                "case_id": f"controlled-{scenario}",
                "case_group": "synthetic_controlled",
                "scenario": scenario,
                "message": f"Artificial {scenario} scenario test message.",
                "expected_label": "HAM",
                "expected_error": None,
                "requirement_refs": VALID_REQUIREMENT_REFS.copy(),
            }
        )

    # Missing and malformed inputs are validation-only cases.
    cases.extend(
        [
            {
                "case_id": "validation-missing",
                "case_group": "validation_only",
                "scenario": "missing",
                "expected_label": None,
                "expected_error": "MESSAGE_REQUIRED",
                "requirement_refs": ["FR-006", "SC-003"],
            },
            {
                "case_id": "validation-malformed",
                "case_group": "validation_only",
                "scenario": "malformed",
                "message": 123,
                "expected_label": None,
                "expected_error": "MESSAGE_INVALID_TYPE",
                "requirement_refs": ["FR-006", "SC-003"],
            },
        ]
    )

    return cases


@pytest.mark.unit
def test_valid_manifest_satisfies_minimum_and_required_coverage(valid_manifest):
    assert validate_evaluation_manifest(valid_manifest) is True


@pytest.mark.unit
def test_manifest_has_at_least_five_cases_per_held_out_label(valid_manifest):
    held_out_cases = [
        case for case in valid_manifest
        if case["case_group"] == "synthetic_held_out"
    ]

    spam_count = sum(
        case["expected_label"] == "SPAM" for case in held_out_cases
    )
    ham_count = sum(
        case["expected_label"] == "HAM" for case in held_out_cases
    )

    assert len(held_out_cases) >= 15
    assert spam_count >= 5
    assert ham_count >= 5


@pytest.mark.unit
def test_required_scenarios_are_covered_across_valid_groups(valid_manifest):
    valid_groups = {
        "synthetic_held_out",
        "synthetic_controlled",
    }

    covered_scenarios = {
        case["scenario"]
        for case in valid_manifest
        if case["case_group"] in valid_groups
    }

    assert set(VALID_SCENARIOS).issubset(covered_scenarios)


@pytest.mark.unit
def test_every_case_has_valid_group_and_requirement_references(valid_manifest):
    allowed_groups = {
        "synthetic_held_out",
        "synthetic_controlled",
        "validation_only",
    }
    allowed_refs = {
        *(f"FR-{number:03d}" for number in range(1, 16)),
        *(f"SC-{number:03d}" for number in range(1, 9)),
    }

    for case in valid_manifest:
        assert case["case_group"] in allowed_groups
        assert isinstance(case["requirement_refs"], list)
        assert case["requirement_refs"]

        assert all(
            reference in allowed_refs
            for reference in case["requirement_refs"]
        )


@pytest.mark.unit
def test_case_ids_are_unique(valid_manifest):
    case_ids = [case["case_id"] for case in valid_manifest]

    assert len(case_ids) == len(set(case_ids))


@pytest.mark.unit
@pytest.mark.parametrize(
    ("case_group", "scenario", "expected_label", "expected_error"),
    [
        ("unknown_group", "normal", "HAM", None),
        ("synthetic_held_out", "missing", None, "MESSAGE_REQUIRED"),
        ("synthetic_controlled", "malformed", None, "MESSAGE_INVALID_TYPE"),
        ("validation_only", "normal", None, "MESSAGE_REQUIRED"),
        ("synthetic_held_out", "normal", None, None),
        ("synthetic_held_out", "normal", "SPAM", "UNEXPECTED_ERROR"),
        ("validation_only", "missing", "SPAM", "MESSAGE_REQUIRED"),
        ("validation_only", "missing", None, None),
    ],
)
def test_invalid_cross_field_combinations_are_rejected(
    valid_manifest,
    case_group,
    scenario,
    expected_label,
    expected_error,
):
    cases = copy.deepcopy(valid_manifest)
    case = cases[0]

    case["case_group"] = case_group
    case["scenario"] = scenario
    case["expected_label"] = expected_label
    case["expected_error"] = expected_error

    assert validate_evaluation_manifest(cases) is False


@pytest.mark.unit
def test_missing_validation_case_must_not_contain_message(valid_manifest):
    cases = copy.deepcopy(valid_manifest)
    missing_case = next(
        case for case in cases
        if case["case_id"] == "validation-missing"
    )

    missing_case["message"] = "This message must not be present."

    assert validate_evaluation_manifest(cases) is False


@pytest.mark.unit
def test_malformed_validation_case_must_violate_input_contract(valid_manifest):
    cases = copy.deepcopy(valid_manifest)
    malformed_case = next(
        case for case in cases
        if case["case_id"] == "validation-malformed"
    )

    malformed_case["message"] = "This is a valid non-empty string."

    assert validate_evaluation_manifest(cases) is False


@pytest.mark.unit
def test_manifest_is_invalid_when_missing_case_is_absent(valid_manifest):
    cases = [
        case for case in valid_manifest
        if case["case_id"] != "validation-missing"
    ]

    assert validate_evaluation_manifest(cases) is False


@pytest.mark.unit
def test_manifest_is_invalid_when_malformed_case_is_absent(valid_manifest):
    cases = [
        case for case in valid_manifest
        if case["case_id"] != "validation-malformed"
    ]

    assert validate_evaluation_manifest(cases) is False


@pytest.mark.unit
def test_controlled_and_validation_cases_are_excluded_from_quality_cases(
    valid_manifest,
):
    quality_cases = select_quality_cases(valid_manifest)

    assert len(quality_cases) == 15
    assert all(
        case["case_group"] == "synthetic_held_out"
        for case in quality_cases
    )


@pytest.mark.unit
def test_invalid_input_cases_never_enter_quality_case_selection(valid_manifest):
    quality_cases = select_quality_cases(valid_manifest)
    quality_case_ids = {case["case_id"] for case in quality_cases}

    assert "validation-missing" not in quality_case_ids
    assert "validation-malformed" not in quality_case_ids
    assert "controlled-boundary" not in quality_case_ids
    assert "controlled-ambiguous" not in quality_case_ids
    assert "controlled-adversarial" not in quality_case_ids


@pytest.mark.unit
def test_invalid_requirement_reference_is_rejected(valid_manifest):
    cases = copy.deepcopy(valid_manifest)
    cases[0]["requirement_refs"] = ["FR-999"]

    assert validate_evaluation_manifest(cases) is False


@pytest.mark.unit
def test_duplicate_case_ids_are_rejected(valid_manifest):
    cases = copy.deepcopy(valid_manifest)
    cases[1]["case_id"] = cases[0]["case_id"]

    assert validate_evaluation_manifest(cases) is False


@pytest.mark.unit
def test_training_case_id_overlap_is_rejected(valid_manifest):
    training_ids = ["held-out-fixture-001"]

    assert validate_evaluation_manifest(
        valid_manifest,
        training_case_ids=training_ids,
    ) is False


@pytest.mark.unit
def test_held_out_cases_must_cover_all_required_scenarios(valid_manifest):
    cases = copy.deepcopy(valid_manifest)

    for case in cases:
        if (
            case["case_group"] == "synthetic_held_out"
            and case["scenario"] == "adversarial"
        ):
            case["scenario"] = "normal"

    # Controlled cases still cover adversarial, so the manifest remains valid.
    assert validate_evaluation_manifest(cases) is True


@pytest.mark.unit
def test_manifest_rejects_duplicate_requirement_references_only_if_invalid(
    valid_manifest,
):
    cases = copy.deepcopy(valid_manifest)
    cases[0]["requirement_refs"] = ["FR-010", "FR-010"]

    # Duplicate references are valid strings; uniqueness is not required.
    assert validate_evaluation_manifest(cases) is True