from __future__ import annotations

from typing import Any

from .types import GraphqlApiConfig, RestApiConfig, SoapApiConfig


class ApiFactory:
  @staticmethod
  def rest(config: dict[str, Any]) -> RestApiConfig:
    return {"protocol": "rest", **config}

  @staticmethod
  def soap(config: dict[str, Any]) -> SoapApiConfig:
    return {"protocol": "soap", **config}

  @staticmethod
  def graphql(config: dict[str, Any]) -> GraphqlApiConfig:
    return {"protocol": "graphql", **config}


api = ApiFactory()
