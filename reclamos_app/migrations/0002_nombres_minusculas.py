import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reclamos_app', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # Las tablas principales ya existen en minúscula en PostgreSQL.
            # Solo renombramos las tablas M2M creadas por Django con mayúscula.
            database_operations=[
                migrations.RunSQL(
                    sql='ALTER TABLE IF EXISTS "Usuarios_groups" RENAME TO usuarios_groups;',
                    reverse_sql='ALTER TABLE IF EXISTS usuarios_groups RENAME TO "Usuarios_groups";',
                ),
                migrations.RunSQL(
                    sql='ALTER TABLE IF EXISTS "Usuarios_user_permissions" RENAME TO usuarios_user_permissions;',
                    reverse_sql='ALTER TABLE IF EXISTS usuarios_user_permissions RENAME TO "Usuarios_user_permissions";',
                ),
            ],
            state_operations=[
                migrations.AlterModelTable(name='barrio', table='barrios'),
                migrations.AlterModelTable(name='rol', table='roles'),
                migrations.AlterModelTable(name='usuario', table='usuarios'),
                migrations.AlterField(
                    model_name='barrio',
                    name='id_barrio',
                    field=models.AutoField(
                        db_column='id_barrio',
                        db_comment='Identificador único de barrio proporcionado por el sistema',
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                migrations.AlterField(
                    model_name='rol',
                    name='id_rol',
                    field=models.AutoField(
                        db_column='id_rol',
                        db_comment='Identificador único del rol proporcionado por el sistema',
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                migrations.AlterField(
                    model_name='usuario',
                    name='id_usuario',
                    field=models.AutoField(
                        db_column='id_usuario',
                        db_comment='Identificador único del usuario proporcionado por el sistema',
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                migrations.AlterField(
                    model_name='usuario',
                    name='barrio',
                    field=models.ForeignKey(
                        blank=True,
                        db_column='id_barrio',
                        db_comment='Número de barrio asignado/escogido proporcionado por el sistema',
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='usuarios',
                        to='reclamos_app.barrio',
                    ),
                ),
                migrations.AlterField(
                    model_name='usuario',
                    name='correo_electronico',
                    field=models.EmailField(
                        blank=True,
                        db_comment='Correo del usuario',
                        default='',
                        max_length=150,
                        verbose_name='correo electrónico',
                    ),
                ),
                migrations.AlterField(
                    model_name='usuario',
                    name='fecha_inicio',
                    field=models.DateField(
                        db_comment='Fecha en que se registra el usuario',
                        default=django.utils.timezone.localdate,
                        verbose_name='fecha de registro',
                    ),
                ),
            ],
        ),
    ]
