"""Migración inicial limpia"""

from alembic import op
import sqlalchemy as sa

# Identificadores de Alembic
revision = '1a841fa66c1b'    # 👈 ESTE ID debe coincidir con el nombre del archivo
down_revision = None         # 👈 o la revisión previa si existiera
branch_labels = None
depends_on = None

# Definimos el ENUM manualmente
payment_status_enum = sa.Enum('PENDING', 'COMPLETED', name='payment_status')

def upgrade():
    # 1️⃣ Crear el tipo ENUM en la base
    payment_status_enum.create(op.get_bind(), checkfirst=True)

    # 2️⃣ Agregar la columna usando ese tipo
    op.add_column(
        'analysis',
        sa.Column('payment_status', payment_status_enum, nullable=False, server_default='PENDING')
    )

def downgrade():
    # 1️⃣ Eliminar la columna
    op.drop_column('analysis', 'payment_status')

    # 2️⃣ Eliminar el tipo ENUM
    payment_status_enum.drop(op.get_bind(), checkfirst=True)
