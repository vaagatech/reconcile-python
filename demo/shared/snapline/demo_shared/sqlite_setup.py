from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .stub_db import db
from .sqlite_connection import SqliteConnection

from .demo_domain import demo_domain


def _seed_warehouse_tables(connection: SqliteConnection, variant: str) -> None:
    connection.exec(
        """
    CREATE TABLE customers (
      email TEXT PRIMARY KEY,
      status_code TEXT NOT NULL,
      tier TEXT NOT NULL
    );

    CREATE TABLE customer_profiles (
      email TEXT PRIMARY KEY,
      role TEXT NOT NULL,
      department TEXT NOT NULL
    );

    CREATE TABLE customer_subscriptions (
      email TEXT PRIMARY KEY,
      plan_code TEXT NOT NULL,
      renews_at TEXT NOT NULL
    );

    CREATE TABLE orders (
      order_id TEXT PRIMARY KEY,
      email TEXT NOT NULL,
      status TEXT NOT NULL,
      amount REAL NOT NULL,
      shipped_at TEXT NOT NULL
    );
    """
    )

    status_code = (
        demo_domain.warehouse_source_status
        if variant == "source"
        else demo_domain.warehouse_target_status
    )
    plan_code = (
        demo_domain.warehouse_source_plan
        if variant == "source"
        else demo_domain.warehouse_target_plan
    )
    order_status = (
        demo_domain.warehouse_source_order_status
        if variant == "source"
        else demo_domain.warehouse_target_order_status
    )

    connection.exec(
        f"""
    INSERT INTO customers (email, status_code, tier) VALUES
      ('{demo_domain.email}', '{status_code}', '{demo_domain.tier}');

    INSERT INTO customer_profiles (email, role, department) VALUES
      ('{demo_domain.email}', '{demo_domain.role}', '{demo_domain.department}');

    INSERT INTO customer_subscriptions (email, plan_code, renews_at) VALUES
      ('{demo_domain.email}', '{plan_code}', '{demo_domain.renews_at}');

    INSERT INTO orders (order_id, email, status, amount, shipped_at) VALUES
      ('ord_1001', '{demo_domain.email}', '{order_status}', {demo_domain.order_total}, '{demo_domain.order_shipped_at}');
    """
    )


def _seed_app_database(connection: SqliteConnection) -> None:
    connection.exec(
        f"""
    CREATE TABLE customers (
      email TEXT PRIMARY KEY,
      status TEXT NOT NULL,
      tier TEXT NOT NULL,
      last_login TEXT NOT NULL
    );

    CREATE TABLE customer_profiles (
      email TEXT PRIMARY KEY,
      role TEXT NOT NULL,
      department TEXT NOT NULL
    );

    CREATE TABLE customer_subscriptions (
      email TEXT PRIMARY KEY,
      plan_code TEXT NOT NULL,
      renews_at TEXT NOT NULL
    );

    CREATE TABLE orders (
      order_id TEXT PRIMARY KEY,
      email TEXT NOT NULL,
      status TEXT NOT NULL,
      amount REAL NOT NULL,
      shipped_at TEXT NOT NULL
    );

    INSERT INTO customers (email, status, tier, last_login) VALUES
      ('{demo_domain.email}', '{demo_domain.app_db_status}', '{demo_domain.tier}', '{demo_domain.last_login}');

    INSERT INTO customer_profiles (email, role, department) VALUES
      ('{demo_domain.email}', '{demo_domain.role}', '{demo_domain.department}');

    INSERT INTO customer_subscriptions (email, plan_code, renews_at) VALUES
      ('{demo_domain.email}', '{demo_domain.warehouse_target_plan}', '{demo_domain.renews_at}');

    INSERT INTO orders (order_id, email, status, amount, shipped_at) VALUES
      ('ord_1001', '{demo_domain.email}', '{demo_domain.warehouse_target_order_status}', {demo_domain.order_total}, '{demo_domain.order_shipped_at}');
    """
    )


def _create_audit_table(connection: SqliteConnection, logged_at: str) -> None:
    connection.exec(
        f"""
    CREATE TABLE users_audit (
      email TEXT PRIMARY KEY,
      logged_at TEXT NOT NULL,
      status TEXT NOT NULL
    );

    INSERT INTO users_audit (email, logged_at, status) VALUES
      ('{demo_domain.email}', '{logged_at}', 'ACTIVE');
    """
    )


@dataclass
class DemoDatabase:
    source_db: SqliteConnection
    target_db: SqliteConnection
    app_db: SqliteConnection
    audit_source_db: SqliteConnection
    audit_target_db: SqliteConnection


def create_demo_database() -> DemoDatabase:
    source_db = db.sqlite(":memory:")
    _seed_warehouse_tables(source_db, "source")

    target_db = db.sqlite(":memory:")
    _seed_warehouse_tables(target_db, "target")

    app_db = db.sqlite(":memory:")
    _seed_app_database(app_db)

    audit_source_db = db.sqlite(":memory:")
    _create_audit_table(audit_source_db, demo_domain.audit_logged_at)

    audit_target_db = db.sqlite(":memory:")
    _create_audit_table(audit_target_db, "VALID_DATE")

    return DemoDatabase(
        source_db=source_db,
        target_db=target_db,
        app_db=app_db,
        audit_source_db=audit_source_db,
        audit_target_db=audit_target_db,
    )


def close_demo_database(database: DemoDatabase) -> None:
    database.source_db.close()
    database.target_db.close()
    database.app_db.close()
    database.audit_source_db.close()
    database.audit_target_db.close()
