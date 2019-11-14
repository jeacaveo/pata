"""add latest unit version view

Revision ID: fee7030659ca
Revises: 49de8f4de319
Create Date: 2019-11-13 15:21:49.351048+00:00

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'fee7030659ca'
down_revision = '49de8f4de319'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()


def upgrade_sqlite():
    op.execute(
        """
        CREATE VIEW latest_unit_version AS
        SELECT *
        FROM units u, unit_versions uv
        WHERE u.id = uv.unit_id
        AND uv.id = (
            SELECT max(uv1.id)
            FROM unit_versions uv1
            WHERE uv1.unit_id = u.id
            )
        """
        )


def downgrade_sqlite():
    op.execute("DROP VIEW latest_unit_version")
