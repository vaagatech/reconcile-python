# noinspection SqlNoDataSourceInspection,SqlDialectInspection
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from snapline.core import nosql
from snapline.core.nosql import InMemoryDocumentStore
from snapline.demo_shared import (
    SqliteConnection,
    create_sqlite_connection,
    exec_sqlite_sql,
)


@dataclass
class WarehouseSeedResult:
    """Demo: SQLite source + in-memory NoSQL. Swap for Postgres + MongoDB in production."""

    source_db: SqliteConnection
    target_db: InMemoryDocumentStore
    cleanup: Callable[[], None]


def seed_warehouse_demo() -> WarehouseSeedResult:
    source_db = create_sqlite_connection(":memory:")
    target_db = nosql.memory()

    exec_sqlite_sql(
        source_db,
        """
        CREATE TABLE wh_customers (
          customer_id TEXT PRIMARY KEY,
          email TEXT NOT NULL,
          status TEXT NOT NULL,
          segment TEXT NOT NULL
        );
        CREATE TABLE wh_addresses (
          address_id TEXT PRIMARY KEY,
          customer_id TEXT NOT NULL,
          city TEXT NOT NULL,
          country TEXT NOT NULL
        );
        CREATE TABLE wh_contacts (
          contact_id TEXT PRIMARY KEY,
          customer_id TEXT NOT NULL,
          channel TEXT NOT NULL,
          value TEXT NOT NULL
        );
        CREATE TABLE wh_products (
          product_id TEXT PRIMARY KEY,
          sku TEXT NOT NULL,
          category TEXT NOT NULL,
          list_price REAL NOT NULL
        );
        CREATE TABLE wh_orders (
          order_id TEXT PRIMARY KEY,
          customer_id TEXT NOT NULL,
          status TEXT NOT NULL,
          total_amount REAL NOT NULL
        );
        CREATE TABLE wh_order_lines (
          line_id TEXT PRIMARY KEY,
          order_id TEXT NOT NULL,
          sku TEXT NOT NULL,
          quantity INTEGER NOT NULL,
          line_amount REAL NOT NULL
        );
        CREATE TABLE wh_payments (
          payment_id TEXT PRIMARY KEY,
          order_id TEXT NOT NULL,
          method TEXT NOT NULL,
          amount REAL NOT NULL,
          status TEXT NOT NULL
        );
        CREATE TABLE wh_inventory (
          inventory_id TEXT PRIMARY KEY,
          product_id TEXT NOT NULL,
          warehouse_code TEXT NOT NULL,
          qty INTEGER NOT NULL
        );
        """,
    )

    exec_sqlite_sql(
        source_db,
        """
        INSERT INTO wh_customers VALUES ('cust_1','alice@vaagatech.com','ACTIVE','ENTERPRISE');
        INSERT INTO wh_addresses VALUES ('addr_1','cust_1','Austin','US');
        INSERT INTO wh_contacts VALUES ('cont_1','cust_1','email','alice@vaagatech.com');
        INSERT INTO wh_products VALUES ('prod_1','SKU-A','ELEC',49.99);
        INSERT INTO wh_orders VALUES ('ord_1','cust_1','SHIPPED',69.49);
        INSERT INTO wh_order_lines VALUES ('line_1','ord_1','SKU-A',1,49.99);
        INSERT INTO wh_payments VALUES ('pay_1','ord_1','card',69.49,'CAPTURED');
        INSERT INTO wh_inventory VALUES ('inv_1','prod_1','WH1',120);
        """,
    )

    nosql.seed(
        target_db,
        "customers",
        [{"customerId": "cust_1", "email": "alice@vaagatech.com", "status": "ACTV", "segment": "ENT"}],
    )
    nosql.seed(
        target_db,
        "addresses",
        [{"addressId": "addr_1", "customerId": "cust_1", "city": "Austin", "country": "USA"}],
    )
    nosql.seed(
        target_db,
        "contacts",
        [{"contactId": "cont_1", "customerId": "cust_1", "channel": "email", "value": "alice@vaagatech.com"}],
    )
    nosql.seed(
        target_db,
        "products",
        [{"productId": "prod_1", "sku": "SKU-A", "category": "electronics", "listPrice": 49.99}],
    )
    nosql.seed(
        target_db,
        "orders",
        [{"orderId": "ord_1", "customerId": "cust_1", "status": "DELIVERED", "totalAmount": 69.49}],
    )
    nosql.seed(
        target_db,
        "order_lines",
        [{"lineId": "line_1", "orderId": "ord_1", "sku": "SKU-A", "quantity": 1, "lineAmount": 49.99}],
    )
    nosql.seed(
        target_db,
        "payments",
        [{"paymentId": "pay_1", "orderId": "ord_1", "method": "card", "amount": 69.49, "status": "SETTLED"}],
    )
    nosql.seed(
        target_db,
        "inventory",
        [{"inventoryId": "inv_1", "productId": "prod_1", "warehouseCode": "warehouse-east", "qty": 120}],
    )

    return WarehouseSeedResult(
        source_db=source_db,
        target_db=target_db,
        cleanup=source_db.close,
    )
