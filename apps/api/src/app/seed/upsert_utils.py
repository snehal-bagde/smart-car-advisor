from sqlalchemy.orm import Session


def get_or_create(db: Session, model: type, lookup: dict, defaults: dict | None = None):
    """Look up `model` by its natural key (`lookup`); insert with `defaults` if missing.

    Never does a blind insert -- this is what makes every seed entity idempotent and
    able to heal partial deletions on rerun.
    """
    instance = db.query(model).filter_by(**lookup).one_or_none()
    if instance is not None:
        return instance, False

    instance = model(**lookup, **(defaults or {}))
    db.add(instance)
    db.flush()
    return instance, True
