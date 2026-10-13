from backend.candidate_registry import CandidateRegistry, normalize_flag


def test_normalize_flag_only_changes_transport_whitespace():
    assert normalize_flag("  FLAG{a}\n") == "FLAG{a}"
    assert normalize_flag("FLAG{a}  extra") == "FLAG{a}  extra"


def test_candidate_requires_independent_sources():
    registry = CandidateRegistry(quorum=2)
    registry.propose("FLAG{x}", "model-a", method="derived")
    registry.verify("FLAG{x}", "model-a", accepted=True)
    assert registry.verified("FLAG{x}") is None

    registry.propose(" FLAG{x} ", "model-b", method="reproduced")
    registry.verify("FLAG{x}", "model-b", accepted=True, evidence=("same result",))
    verified = registry.verified("FLAG{x}")
    assert verified is not None
    assert verified.accepted_sources == {"model-a", "model-b"}


def test_rejected_verifier_is_recorded():
    registry = CandidateRegistry(quorum=2)
    registry.propose("FLAG{x}", "model-a")
    registry.verify("FLAG{x}", "model-a", accepted=True)
    registry.verify("FLAG{x}", "model-b", accepted=False, evidence=("not reproducible",))
    assert registry.verified("FLAG{x}") is None
    assert registry.records["FLAG{x}"].rejected_sources == {"model-b"}
