"""Add updated_at on post

Revision ID: c63fbdae3e17
Revises: 77601f6b760b
Create Date: 2023-08-05 22:01:51.086849

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str | None = "c63fbdae3e17"
down_revision: str | None = "77601f6b760b"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("post", sa.Column("updated_at", sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("post", "updated_at")
    # ### end Alembic commands ###
