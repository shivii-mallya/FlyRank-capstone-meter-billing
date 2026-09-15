from alembic import op
import sqlalchemy as sa
import secrets


# revision identifiers, used by Alembic.
revision = "e584df6fd757"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add the column temporarily as nullable
    with op.batch_alter_table("tenants") as batch_op:
        batch_op.add_column(
            sa.Column("api_key", sa.String(), nullable=True)
        )

    # 2. Generate a unique API key for every existing tenant
    connection = op.get_bind()

    tenants = connection.execute(
        sa.text("SELECT id FROM tenants")
    ).fetchall()

    for tenant in tenants:
        api_key = secrets.token_urlsafe(32)

        connection.execute(
            sa.text(
                "UPDATE tenants SET api_key = :api_key WHERE id = :tenant_id"
            ),
            {
                "api_key": api_key,
                "tenant_id": tenant.id,
            }
        )

    # 3. Make the column required and unique
    with op.batch_alter_table("tenants") as batch_op:
        batch_op.alter_column(
            "api_key",
            existing_type=sa.String(),
            nullable=False
        )
        batch_op.create_unique_constraint(
            "uq_tenants_api_key",
            ["api_key"]
        )


def downgrade():
    with op.batch_alter_table("tenants") as batch_op:
        batch_op.drop_constraint(
            "uq_tenants_api_key",
            type_="unique"
        )
        batch_op.drop_column("api_key")