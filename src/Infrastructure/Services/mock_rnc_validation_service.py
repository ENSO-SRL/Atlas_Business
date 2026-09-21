import logging

from src.Domain.Ports.Services.i_rnc_validation_service import IRncValidationService

logger = logging.getLogger(__name__)


class MockRncValidationService(IRncValidationService):
    """
    Implementación mock del servicio de validación RNC.
    Acepta cualquier RNC de 11 dígitos numéricos como válido.
    Reemplazar por DgiiRncValidationService cuando la API esté disponible.
    """

    async def validate(self, rnc: str) -> bool:
        logger.info(f"[MOCK RNC] Validando RNC: {rnc}")
        # Solo validamos el formato (11 dígitos); la API real verificaría existencia en la DGII.
        is_valid = rnc.isdigit() and len(rnc) == 11
        logger.info(f"[MOCK RNC] RNC {rnc} → {'VÁLIDO' if is_valid else 'INVÁLIDO'}")
        return is_valid
