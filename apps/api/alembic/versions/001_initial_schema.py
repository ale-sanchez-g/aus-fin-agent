"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "providers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("abn", sa.String(11), nullable=True),
        sa.Column("cdr_holder_id", sa.String(255), nullable=True),
        sa.Column("endpoint_url", sa.String(500), nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_table(
        "data_sources",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider_id", sa.String(36), sa.ForeignKey("providers.id"), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("url", sa.String(500), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "sync_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider_id", sa.String(36), sa.ForeignKey("providers.id"), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_synced", sa.Integer(), nullable=False, default=0),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider_id", sa.String(36), sa.ForeignKey("providers.id"), nullable=False),
        sa.Column("external_product_id", sa.String(255), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("brand", sa.String(255), nullable=True),
        sa.Column("brand_name", sa.String(255), nullable=True),
        sa.Column("application_uri", sa.String(500), nullable=True),
        sa.Column("is_tailored", sa.Boolean(), nullable=False, default=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effective_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=True),
        sa.Column("additional_info", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "product_features",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("feature_type", sa.String(100), nullable=False),
        sa.Column("additional_value", sa.String(500), nullable=True),
        sa.Column("additional_info", sa.Text(), nullable=True),
        sa.Column("additional_info_uri", sa.String(500), nullable=True),
    )

    op.create_table(
        "product_rates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("rate_type", sa.String(100), nullable=False),
        sa.Column("rate", sa.String(50), nullable=True),
        sa.Column("comparison_rate", sa.String(50), nullable=True),
        sa.Column("calculation_frequency", sa.String(50), nullable=True),
        sa.Column("application_frequency", sa.String(50), nullable=True),
        sa.Column("tiers", sa.JSON(), nullable=True),
        sa.Column("additional_value", sa.String(500), nullable=True),
        sa.Column("additional_info", sa.Text(), nullable=True),
    )

    op.create_table(
        "product_fees",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("fee_type", sa.String(100), nullable=False),
        sa.Column("amount", sa.String(50), nullable=True),
        sa.Column("balance_rate", sa.String(50), nullable=True),
        sa.Column("transaction_rate", sa.String(50), nullable=True),
        sa.Column("currency", sa.String(10), nullable=True, default="AUD"),
        sa.Column("additional_info", sa.Text(), nullable=True),
        sa.Column("discounts", sa.JSON(), nullable=True),
    )

    op.create_table(
        "eligibility_rules",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("eligibility_type", sa.String(100), nullable=False),
        sa.Column("additional_value", sa.String(500), nullable=True),
        sa.Column("additional_info", sa.Text(), nullable=True),
        sa.Column("additional_info_uri", sa.String(500), nullable=True),
    )

    op.create_table(
        "client_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("product_category", sa.String(100), nullable=True),
        sa.Column("preferences", sa.JSON(), nullable=True),
        sa.Column("constraints", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "discovery_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("client_profile_id", sa.String(36), sa.ForeignKey("client_profiles.id"), nullable=True),
        sa.Column("user_intent", sa.Text(), nullable=True),
        sa.Column("product_category", sa.String(100), nullable=True),
        sa.Column("preferences", sa.JSON(), nullable=True),
        sa.Column("constraints", sa.JSON(), nullable=True),
        sa.Column("weight_profile", sa.String(50), nullable=True, default="balanced"),
        sa.Column("status", sa.String(50), nullable=False, default="pending"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "recommendation_results",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("session_id", sa.String(36), sa.ForeignKey("discovery_sessions.id"), nullable=False),
        sa.Column("product_id", sa.String(36), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("external_product_id", sa.String(255), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("total_score", sa.Float(), nullable=False),
        sa.Column("score_breakdown", sa.JSON(), nullable=True),
        sa.Column("narrative", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "report_artifacts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("session_id", sa.String(36), sa.ForeignKey("discovery_sessions.id"), nullable=False),
        sa.Column("report_type", sa.String(50), nullable=False, default="discovery"),
        sa.Column("s3_key", sa.String(500), nullable=True),
        sa.Column("local_path", sa.String(500), nullable=True),
        sa.Column("content", sa.JSON(), nullable=True),
        sa.Column("format", sa.String(20), nullable=False, default="json"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("report_artifacts")
    op.drop_table("recommendation_results")
    op.drop_table("discovery_sessions")
    op.drop_table("client_profiles")
    op.drop_table("eligibility_rules")
    op.drop_table("product_fees")
    op.drop_table("product_rates")
    op.drop_table("product_features")
    op.drop_table("products")
    op.drop_table("sync_jobs")
    op.drop_table("data_sources")
    op.drop_table("providers")
