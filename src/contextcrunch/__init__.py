from contextcrunch.crunch import crunch, compress
from contextcrunch.types import CompressionResult, Change, ProtectedSpan, Segment
from contextcrunch.config import (
    CompressionLevel,
    ContextCrunchError,
    EmptyInputError,
    InputTooLargeError,
    TargetTokensUnreachableError,
)

__version__ = "0.1.0"

__all__ = [
    "crunch",
    "compress",
    "CompressionResult",
    "Change",
    "ProtectedSpan",
    "Segment",
    "CompressionLevel",
    "ContextCrunchError",
    "EmptyInputError",
    "InputTooLargeError",
    "TargetTokensUnreachableError",
]
