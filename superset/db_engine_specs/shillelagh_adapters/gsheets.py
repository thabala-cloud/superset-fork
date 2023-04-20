import json

from flask_babel import gettext as __, lazy_gettext as _
from marshmallow import fields, Schema
from sqlalchemy.engine.url import URL
from typing import (
    Any,
    Dict,
    List,
    Optional,
)
from typing_extensions import TypedDict

from superset.db_engine_specs.base import BasicPropertiesType
from superset.db_engine_specs.shillelagh_adapters.base import BaseAdapterSpec
from superset.errors import ErrorLevel, SupersetError, SupersetErrorType


class GSheetsParametersSchema(Schema):
    username = fields.String(required=True, allow_none=True, description=__("Username"))
    password = fields.String(allow_none=True, description=__("Password"))


class GSheetsParametersType(TypedDict, total=False):
    username: Optional[str]
    password: Optional[str]


class GSheetsAdapterSpec(BaseAdapterSpec):
    """
    Shillelagh google sheets adapter spec
    """
    engine_name = "Google Sheets"
    adapter = "gsheetsapi"

    # schema describing the parameters used to configure the adapter
    parameters_schema = GSheetsParametersSchema()


    @classmethod
    def update_encrypted_extra_from_params(  # pylint: disable=invalid-name
        cls,
        parameters: GSheetsParametersType,
        encrypted_extra: Optional[Dict[str, str]] = None,
    ) -> None:
        encrypted_extra = {
            "adapters": ["githubapi"],
            "adapter_kwargs": {
                "username": parameters["username"],
                "password": parameters["password"],
            },
        }

        return json.dumps(encrypted_extra)


    @classmethod
    def build_sqlalchemy_uri(  # pylint: disable=unused-argument
        cls,
        parameters: GSheetsParametersType,
        encrypted_extra: Optional[Dict[str, str]] = None,
    ) -> str:
        return str(
            URL(
                "shillelagh+safe",
            )
        )

    @classmethod
    def get_parameters_from_uri(
        cls,
        uri: str,  # pylint: disable=unused-argument
        encrypted_extra: Optional[Dict[str, Any]] = None,
    ) -> Any:
        adapter_kwargs = encrypted_extra["adapter_kwargs"]
        return {
            "username": adapter_kwargs["username"],
            "password": adapter_kwargs["password"],
        }

    @classmethod
    def get_public_information(cls) -> Dict[str, Any]:
        """
        Construct a Dict with properties we want to expose.

        :returns: Dict with shillelagh adapter
        """
        return {
            "adapter": cls.adapter,
            "engine_name": cls.engine_name,
        }

    @classmethod
    def validate_parameters(
        cls, properties: BasicPropertiesType
    ) -> List[SupersetError]:
        errors: List[SupersetError] = []
        required = {
            "username",
            "password",
        }
        parameters = properties.get("parameters", {})
        present = {key for key in parameters if parameters.get(key, ())}
        missing = sorted(required - present)

        if missing:
            errors.append(
                SupersetError(
                    message=f'One or more parameters are missing: {", ".join(missing)}',
                    error_type=SupersetErrorType.CONNECTION_MISSING_PARAMETERS_ERROR,
                    level=ErrorLevel.WARNING,
                    extra={"missing": missing},
                ),
            )
        return errors
