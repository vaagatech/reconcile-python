from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from graphql import GraphQLArgument, GraphQLFloat, GraphQLID, GraphQLInt, GraphQLSchema, GraphQLString, graphql_sync
from graphql.type.definition import GraphQLField, GraphQLList, GraphQLNonNull, GraphQLObjectType

project_graphql_domain = {
    "email": "alice@vaagatech.com",
    "customer_id": "cust_1001",
    "sql_status": "ACTIVE",
    "segment": "ENTERPRISE",
    "orders": [
        {"orderId": "ord_9001", "sku": "SKU-A", "quantity": 2, "amount": 49.99},
        {"orderId": "ord_9002", "sku": "SKU-B", "quantity": 1, "amount": 19.5},
    ],
}


def _build_account(email: str) -> Optional[dict[str, Any]]:
    if email != project_graphql_domain["email"]:
        return None
    return {
        "customerId": project_graphql_domain["customer_id"],
        "email": project_graphql_domain["email"],
        "status": project_graphql_domain["sql_status"],
        "segment": project_graphql_domain["segment"],
    }


CustomerAccountType = GraphQLObjectType(
    "CustomerAccount",
    lambda: {
        "customerId": GraphQLField(GraphQLNonNull(GraphQLID)),
        "email": GraphQLField(GraphQLNonNull(GraphQLString)),
        "status": GraphQLField(GraphQLNonNull(GraphQLString)),
        "segment": GraphQLField(GraphQLNonNull(GraphQLString)),
    },
)

OrderLineType = GraphQLObjectType(
    "OrderLine",
    lambda: {
        "orderId": GraphQLField(GraphQLNonNull(GraphQLID)),
        "sku": GraphQLField(GraphQLNonNull(GraphQLString)),
        "quantity": GraphQLField(GraphQLNonNull(GraphQLInt)),
        "amount": GraphQLField(GraphQLNonNull(GraphQLFloat)),
    },
)

SyncResultType = GraphQLObjectType(
    "SyncResult",
    lambda: {
        "customerId": GraphQLField(GraphQLNonNull(GraphQLID)),
        "email": GraphQLField(GraphQLNonNull(GraphQLString)),
        "status": GraphQLField(GraphQLNonNull(GraphQLString)),
        "segment": GraphQLField(GraphQLNonNull(GraphQLString)),
        "syncedAt": GraphQLField(GraphQLNonNull(GraphQLString)),
    },
)

QueryType = GraphQLObjectType(
    "Query",
    lambda: {
        "customerAccount": GraphQLField(
            CustomerAccountType,
            args={"email": GraphQLArgument(GraphQLNonNull(GraphQLString))},
            resolve=lambda _root, info, email: _build_account(email),
        ),
        "customerOrders": GraphQLField(
            GraphQLList(GraphQLNonNull(OrderLineType)),
            args={
                "email": GraphQLArgument(GraphQLNonNull(GraphQLString)),
                "limit": GraphQLArgument(GraphQLInt, default_value=10),
            },
            resolve=lambda _root, info, email, limit=10: (
                project_graphql_domain["orders"][: max(0, limit)]
                if email == project_graphql_domain["email"]
                else []
            ),
        ),
    },
)

MutationType = GraphQLObjectType(
    "Mutation",
    lambda: {
        "syncCustomerProfile": GraphQLField(
            SyncResultType,
            args={
                "customerId": GraphQLArgument(GraphQLNonNull(GraphQLID)),
                "segment": GraphQLArgument(GraphQLNonNull(GraphQLString)),
            },
            resolve=lambda _root, info, customerId, segment: {
                "customerId": customerId,
                "email": project_graphql_domain["email"],
                "status": project_graphql_domain["sql_status"],
                "segment": segment,
                "syncedAt": datetime.now(timezone.utc).isoformat(),
            },
        ),
    },
)

project_graphql_schema = GraphQLSchema(query=QueryType, mutation=MutationType)


def execute_project_graphql(
    query: str,
    variables: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    result = graphql_sync(project_graphql_schema, query, variable_values=variables or {})
    if result.errors:
        return {"errors": [{"message": error.message} for error in result.errors]}
    return {"data": result.data}
