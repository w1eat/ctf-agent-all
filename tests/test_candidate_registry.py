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


def test_inconclusive_verification_is_neither_rejection_nor_quorum_vote():
    registry = CandidateRegistry(quorum=2)
    registry.propose("FLAG{x}", "model-a")
    registry.verify("FLAG{x}", "model-a", accepted=True)
    registry.verify("FLAG{x}", "model-b", accepted=None, evidence=("request timed out",))
    record = registry.records["FLAG{x}"]
    assert record.inconclusive_sources == {"model-b"}
    assert record.rejected_sources == set()
    assert record.verification_count == 1
    assert registry.verified("FLAG{x}") is None
    assert registry.snapshot()[0]["inconclusive_sources"] == ["model-b"]


def test_verifier_outcome_can_recover_without_contradictory_votes():
    registry = CandidateRegistry(quorum=1)
    registry.propose("FLAG{x}", "model-a")
    record = registry.verify("FLAG{x}", "model-b", accepted=False)
    assert record.rejected
    registry.verify("FLAG{x}", "model-b", accepted=None)
    assert not record.rejected
    registry.verify("FLAG{x}", "model-b", accepted=True)
    assert registry.verified("FLAG{x}") is record
    assert not record.inconclusive_sources
    assert not record.rejected_sources
    registry.verify("FLAG{x}", "model-b", accepted=False)
    assert not record.accepted_sources
    assert record.rejected
    assert registry.verified("FLAG{x}") is None
