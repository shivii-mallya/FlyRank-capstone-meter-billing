from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.databases.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique=True, nullable=False)

    api_call_limit = Column(Integer, nullable=False)
    ai_token_limit = Column(Integer, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    tenants = relationship(
        "Tenant",
        back_populates="plan"
    )


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    plan_id = Column(
        Integer,
        ForeignKey("plans.id"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    plan = relationship(
        "Plan",
        back_populates="tenants"
    )

    subscriptions = relationship(
        "Subscription",
        back_populates="tenant"
    )

    usage_events = relationship(
        "UsageEvent",
        back_populates="tenant"
    )


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)

    tenant_id = Column(
        Integer,
        ForeignKey("tenants.id"),
        nullable=False
    )

    payment_provider = Column(
        String,
        nullable=True
    )

    provider_subscription_id = Column(
        String,
        unique=True,
        nullable=True
    )

    status = Column(
        String,
        default="active",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    tenant = relationship(
        "Tenant",
        back_populates="subscriptions"
    )


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(Integer, primary_key=True, index=True)

    tenant_id = Column(
        Integer,
        ForeignKey("tenants.id"),
        nullable=False
    )

    usage_type = Column(
        String,
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )
    input_tokens = Column(Integer, nullable=True, default=0)
    cached_input_tokens = Column(Integer, nullable=True, default=0)
    output_tokens = Column(Integer, nullable=True, default=0)
    reasoning_tokens = Column(Integer, nullable=True, default=0)
    
    idempotency_key = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    tenant = relationship(
        "Tenant",
        back_populates="usage_events"
    )

    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_usage_idempotency"
        ),
    )


class ProcessedWebhookEvent(Base):
    __tablename__ = "processed_webhook_events"

    id = Column(Integer, primary_key=True, index=True)

    provider_event_id = Column(
        String,
        unique=True,
        nullable=False
    )

    event_type = Column(
        String,
        nullable=False
    )

    payment_provider = Column(
        String,
        nullable=False
    )

    processed_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )