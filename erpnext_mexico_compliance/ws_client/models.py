from dataclasses import dataclass
from enum import Enum


@dataclass
class CfdiStatus:
    """Represents the status of a CFDI."""

    class CancellableStatus(Enum):
        """Represents the cancellable status of a CFDI."""

        CANCELLABLE_BY_APPROVAL = "Cancelable con aceptación"
        CANCELLABLE_BY_DIRECT_CALL = "Cancelable sin aceptación"
        NOT_CANCELLABLE = "No cancelable"

    class DocumentStatus(Enum):
        """Represents the status of a CFDI."""

        ACTIVE = "Vigente"
        CANCELLED = "Cancelado"

    class CancellationStatus(Enum):
        """Represents the status of a CFDI cancellation request."""

        CANCELLED_BY_APPROVAL = "Cancelado con aceptación"
        CANCELLED_BY_DIRECT_CALL = "Cancelado sin aceptación"
        CANCELLED_BY_EXPIRATION = "Plazo vencido"
        PENDING = "En proceso"
        REJECTED = "Solicitud rechazada"

    code: str
    is_cancellable: CancellableStatus | None
    status: DocumentStatus | str
    cancellation_status: CancellationStatus | None

    @classmethod
    def from_json(cls, response: dict):
        """
        Creates a CfdiStatus object from a JSON response.

        Args:
            response (dict): The JSON response to parse.

        Returns:
            CfdiStatus: The parsed CfdiStatus object.
        """
        message = response.get("message", {})
        is_cancellable = message.get("is_cancellable", None)
        if is_cancellable:
            is_cancellable = cls.CancellableStatus(is_cancellable)

        try:
            status = cls.DocumentStatus(message.get("status", ""))
        except ValueError:
            status = message.get("status", None)

        cancellation_status = message.get("cancellation_status", None)
        if cancellation_status:
            cancellation_status = cls.CancellationStatus(cancellation_status)

        return cls(
            code=message["code"],
            is_cancellable=is_cancellable,
            status=status,
            cancellation_status=cancellation_status,
        )
