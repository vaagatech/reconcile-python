from __future__ import annotations

from datetime import datetime
from typing import Any

from graphql import GraphQLArgument, GraphQLFloat, GraphQLSchema, GraphQLString, graphql_sync
from graphql.type.definition import GraphQLField, GraphQLList, GraphQLNonNull, GraphQLObjectType

from .demo_domain import demo_domain, volatile_synced_at, volatile_trace_id

CustomerProfileType = GraphQLObjectType(
    "CustomerProfile",
    lambda: {
        "role": GraphQLField(GraphQLNonNull(GraphQLString)),
        "department": GraphQLField(GraphQLNonNull(GraphQLString)),
    },
)

CustomerSubscriptionType = GraphQLObjectType(
    "CustomerSubscription",
    lambda: {
        "planCode": GraphQLField(GraphQLNonNull(GraphQLString)),
        "renewsAt": GraphQLField(GraphQLNonNull(GraphQLString)),
    },
)

OrderSummaryType = GraphQLObjectType(
    "OrderSummary",
    lambda: {
        "orderId": GraphQLField(GraphQLNonNull(GraphQLString)),
        "status": GraphQLField(GraphQLNonNull(GraphQLString)),
        "total": GraphQLField(GraphQLNonNull(GraphQLFloat)),
        "shippedAt": GraphQLField(GraphQLNonNull(GraphQLString)),
    },
)

CustomerMetadataType = GraphQLObjectType(
    "CustomerMetadata",
    lambda: {
        "traceId": GraphQLField(GraphQLNonNull(GraphQLString)),
        "syncedAt": GraphQLField(GraphQLNonNull(GraphQLString)),
    },
)

CustomerAccountType = GraphQLObjectType(
    "CustomerAccount",
    lambda: {
        "email": GraphQLField(GraphQLNonNull(GraphQLString)),
        "status": GraphQLField(GraphQLNonNull(GraphQLString)),
        "tier": GraphQLField(GraphQLNonNull(GraphQLString)),
        "lastLogin": GraphQLField(GraphQLNonNull(GraphQLString)),
        "profile": GraphQLField(GraphQLNonNull(CustomerProfileType)),
        "subscription": GraphQLField(GraphQLNonNull(CustomerSubscriptionType)),
        "orders": GraphQLField(GraphQLNonNull(GraphQLList(GraphQLNonNull(OrderSummaryType)))),
        "metadata": GraphQLField(GraphQLNonNull(CustomerMetadataType)),
    },
)

CustomerSnapshotType = GraphQLObjectType(
    "CustomerSnapshot",
    lambda: {
        "email": GraphQLField(GraphQLNonNull(GraphQLString)),
        "status": GraphQLField(GraphQLNonNull(GraphQLString)),
        "tier": GraphQLField(GraphQLNonNull(GraphQLString)),
        "role": GraphQLField(GraphQLNonNull(GraphQLString)),
        "department": GraphQLField(GraphQLNonNull(GraphQLString)),
        "planCode": GraphQLField(GraphQLNonNull(GraphQLString)),
        "renewsAt": GraphQLField(GraphQLNonNull(GraphQLString)),
        "lastLogin": GraphQLField(GraphQLNonNull(GraphQLString)),
    },
)


def _to_iso_string(value: str) -> str:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    text = dt.isoformat(timespec="milliseconds")
    return text.replace("+00:00", "Z")


def _build_customer_account(email: str) -> dict[str, Any]:
    return {
        "email": email,
        "status": demo_domain.api_status,
        "tier": demo_domain.tier,
        "lastLogin": _to_iso_string(demo_domain.last_login),
        "profile": {
            "role": demo_domain.role,
            "department": demo_domain.department,
        },
        "subscription": {
            "planCode": demo_domain.api_plan_code,
            "renewsAt": _to_iso_string(demo_domain.renews_at),
        },
        "orders": [
            {
                "orderId": "ord_1001",
                "status": demo_domain.order_status,
                "total": demo_domain.order_total,
                "shippedAt": _to_iso_string(demo_domain.order_shipped_at),
            }
        ],
        "metadata": {
            "traceId": volatile_trace_id(),
            "syncedAt": volatile_synced_at(),
        },
    }


def _resolve_customer_account(_obj, info, email: str):
    return _build_customer_account(email)


def _resolve_customer_snapshot(_obj, info, email: str):
    account = _build_customer_account(email)
    return {
        "email": account["email"],
        "status": account["status"],
        "tier": account["tier"],
        "role": account["profile"]["role"],
        "department": account["profile"]["department"],
        "planCode": account["subscription"]["planCode"],
        "renewsAt": account["subscription"]["renewsAt"],
        "lastLogin": account["lastLogin"],
    }


QueryType = GraphQLObjectType(
    "Query",
    lambda: {
        "customerAccount": GraphQLField(
            CustomerAccountType,
            args={"email": GraphQLArgument(GraphQLNonNull(GraphQLString))},
            resolve=_resolve_customer_account,
        ),
        "customerSnapshot": GraphQLField(
            CustomerSnapshotType,
            args={"email": GraphQLArgument(GraphQLNonNull(GraphQLString))},
            resolve=_resolve_customer_snapshot,
        ),
        "user": GraphQLField(
            CustomerAccountType,
            args={"email": GraphQLArgument(GraphQLNonNull(GraphQLString))},
            resolve=_resolve_customer_account,
        ),
    },
)

demo_graphql_schema = GraphQLSchema(query=QueryType)


def execute_demo_graphql(
    query: str,
    variables: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = graphql_sync(
        demo_graphql_schema,
        query,
        variable_values=variables or {},
    )

    if result.errors:
        return {"errors": [{"message": error.message} for error in result.errors]}

    return {"data": result.data}
