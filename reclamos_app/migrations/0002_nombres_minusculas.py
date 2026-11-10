from django.db import migrations


class Migration(migrations.Migration):
    """
    Histórica: en entornos antiguos renombraba tablas PascalCase → minúscula.
    El estado final ya quedó en 0001_initial; aquí solo se renombran si aún existen
    las tablas/columnas con mayúscula (producción legada). En BD de prueba es no-op.
    """

    dependencies = [
        ('reclamos_app', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                IF to_regclass('public."Barrios"') IS NOT NULL THEN
                    ALTER TABLE "Barrios" RENAME TO barrios;
                END IF;
                IF to_regclass('public."Roles"') IS NOT NULL THEN
                    ALTER TABLE "Roles" RENAME TO roles;
                END IF;
                IF to_regclass('public."Usuarios"') IS NOT NULL THEN
                    ALTER TABLE "Usuarios" RENAME TO usuarios;
                END IF;
                IF to_regclass('public."Usuarios_groups"') IS NOT NULL THEN
                    ALTER TABLE "Usuarios_groups" RENAME TO usuarios_groups;
                END IF;
                IF to_regclass('public."Usuarios_user_permissions"') IS NOT NULL THEN
                    ALTER TABLE "Usuarios_user_permissions" RENAME TO usuarios_user_permissions;
                END IF;

                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'barrios' AND column_name = 'Id_barrio'
                ) THEN
                    ALTER TABLE barrios RENAME COLUMN "Id_barrio" TO id_barrio;
                END IF;
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'roles' AND column_name = 'Id_rol'
                ) THEN
                    ALTER TABLE roles RENAME COLUMN "Id_rol" TO id_rol;
                END IF;
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'usuarios' AND column_name = 'Id_usuario'
                ) THEN
                    ALTER TABLE usuarios RENAME COLUMN "Id_usuario" TO id_usuario;
                END IF;
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'usuarios' AND column_name = 'Id_barrio'
                ) THEN
                    ALTER TABLE usuarios RENAME COLUMN "Id_barrio" TO id_barrio;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
