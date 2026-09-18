class SlotAlreadyBookedInfraError(Exception):
    """
    Lanzada cuando el exclusion constraint GiST de la tabla booking es violado.
    Debe ser capturada en la capa de presentación (FastAPI exception handler)
    y convertida a SlotNoLongerAvailableError (Application) → 409 Conflict.
    """
    pass
