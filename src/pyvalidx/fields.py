'''
Field validation functions
'''

from pydantic import Field
from collections.abc import Callable
from typing import Any, Optional, Dict


def field_validated(
    *validators: Callable[[Any, Optional[Dict[str, Any]]], bool], **kwargs: Any
) -> Any:
    '''
    Creates a Pydantic field with custom validators.

    Args:
        *validators (Callable[[Any, Optional[Dict[str, Any]]], bool]): The custom validation functions.
        **kwargs (Any): The keyword arguments to pass to the Pydantic Field function.

    Returns:
        Any: A Pydantic field with the custom validators.
    '''
    metadata = {"custom_validators": validators}
    extra = kwargs.pop("json_schema_extra", {})
    extra.update(metadata)
    return Field(json_schema_extra=extra, **kwargs)
