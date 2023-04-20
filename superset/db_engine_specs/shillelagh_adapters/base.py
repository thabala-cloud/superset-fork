from typing import Optional


from superset.db_engine_specs.base import BaseEngineSpec
from superset.db_engine_specs.base import BasicParametersMixin


class BaseAdapterSpec(BaseEngineSpec, BasicParametersMixin):  # pylint: disable=too-many-public-methods
    """Abstract class for shillelagh adapter specific configurations"""

    engine_name = "Shillelagh"
    engine = "shillelagh"
    engine_type = "api"
    drivers = {"apsw": "SQLite driver"}
    default_driver = "apsw"
    sqlalchemy_uri_placeholder = "shillelagh://"
    adapter = ""

    allows_joins = True
    allows_subqueries = True
