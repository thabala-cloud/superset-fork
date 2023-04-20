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


class GithubParametersSchema(Schema):
    owner = fields.String(required=True, allow_none=False, description=__("Github account or organization"))
    repository = fields.String(required=True, allow_none=False, description=__("Repository Name"))


class GithubParametersType(TypedDict, total=False):
    owner: str
    repository: str


class GithubAdapterSpec(BaseAdapterSpec):
    """
    Shillelagh github adapter spec
    """
    engine_name = "Github"
    adapter = "githubapi"

    # schema describing the parameters used to configure the adapter
    parameters_schema = GithubParametersSchema()


    @classmethod
    def update_encrypted_extra_from_params(  # pylint: disable=invalid-name
        cls,
        parameters: GithubParametersType,
        encrypted_extra: Optional[Dict[str, str]] = None,
    ) -> None:
        encrypted_extra = {
            "adapters": ["githubapi"],
            "adapter_kwargs": {
                "owner": parameters["owner"],
                "repository": parameters["repository"],
            },
        }

        return json.dumps(encrypted_extra)

    @classmethod
    def build_sqlalchemy_uri(  # pylint: disable=unused-argument
        cls,
        parameters: GithubParametersType,
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
            "owner": adapter_kwargs["owner"],
            "repository": adapter_kwargs["repository"],
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
            "owner",
            "repository",
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