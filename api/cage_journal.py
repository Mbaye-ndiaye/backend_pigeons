"""Journal des événements cage (affectations / retraits / saisies manuelles)."""

from __future__ import annotations


def log_cage_transitions(cage, old_pigeon_id: int | None, old_couple_id: int | None) -> None:
    """Compare l’état actuel de `cage` avec les FK précédentes et crée les `CageEvent` pertinents."""
    from .models import CageEvent

    new_p = cage.pigeon_id
    new_c = cage.couple_id

    if old_pigeon_id != new_p:
        if old_pigeon_id is not None:
            CageEvent.objects.create(
                cage=cage,
                kind=CageEvent.Kind.PIGEON_REMOVED,
                meta={"pigeon_id": old_pigeon_id},
            )
        if new_p is not None and new_p != old_pigeon_id:
            CageEvent.objects.create(
                cage=cage,
                kind=CageEvent.Kind.PIGEON_ASSIGNED,
                meta={"pigeon_id": new_p},
            )

    if old_couple_id != new_c:
        if old_couple_id is not None:
            CageEvent.objects.create(
                cage=cage,
                kind=CageEvent.Kind.COUPLE_REMOVED,
                meta={"couple_id": old_couple_id},
            )
        if new_c is not None and new_c != old_couple_id:
            CageEvent.objects.create(
                cage=cage,
                kind=CageEvent.Kind.COUPLE_ASSIGNED,
                meta={"couple_id": new_c},
            )
