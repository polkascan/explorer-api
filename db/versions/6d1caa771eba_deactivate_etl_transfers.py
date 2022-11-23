"""Deactivate ETL transfers

Revision ID: 6d1caa771eba
Revises: 6ee1e9759190
Create Date: 2022-11-15 13:29:09.784324

"""
from alembic import op
import os
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d1caa771eba'
down_revision = '6ee1e9759190'
branch_labels = None
depends_on = None

class settings:
    DB_USERNAME = os.environ['DB_USERNAME']
    DB_NAME = os.environ['DB_NAME']
    DB_HARVESTER_NAME = os.environ['DB_HARVESTER_NAME'] or "polkascan"


def upgrade():
    op.execute("DROP PROCEDURE IF EXISTS `etl_range`")
    op.execute(f"""
                CREATE DEFINER=`{settings.DB_USERNAME}`@`%` PROCEDURE `etl_range`(`block_start` INT(11), `block_end` INT(11), `update_status` INT(1))
                BEGIN
                            ### GLOBAL SETTINGS ###
                            SET @block_start = `block_start`;
                            SET @block_end = `block_end`;
                            SET @update_status = `update_status`;

                            ### CALL OTHER STORED PROCEDURES ###
                            CALL `etl_explorer_events`(`block_start`,`block_end`,`update_status`);
                            CALL `etl_explorer_extrinsics`(`block_start`,`block_end`,`update_status`);
                            CALL `etl_explorer_logs`(`block_start`,`block_end`,`update_status`);
                            CALL `etl_explorer_blocks`(`block_start`,`block_end`,`update_status`);

                            ### UPDATE STATUS TABLE ###
                            IF @update_status = 1 THEN
                                INSERT INTO `{settings.DB_NAME}`.`harvester_status` (`key`,`description`,`value`)(
                                    SELECT
                                        'PROCESS_ETL' AS	`key`,
                                        'Max blocknumber of etl process' AS `description`,
                                        CAST(@block_end AS JSON) AS `value`
                                    LIMIT 1
                                ) ON DUPLICATE KEY UPDATE
                                    `description` = VALUES(`description`),
                                    `value` = VALUES(`value`)
                                ;
                            END IF;
                        END
            """)


def downgrade():
    op.execute("DROP PROCEDURE IF EXISTS `etl_range`")
    op.execute(f"""
                    CREATE DEFINER=`{settings.DB_USERNAME}`@`%` PROCEDURE `etl_range`(`block_start` INT(11), `block_end` INT(11), `update_status` INT(1))
                    BEGIN
                                ### GLOBAL SETTINGS ###
                                SET @block_start = `block_start`;
                                SET @block_end = `block_end`;
                                SET @update_status = `update_status`;

                                ### CALL OTHER STORED PROCEDURES ###
                                CALL `etl_explorer_events`(`block_start`,`block_end`,`update_status`);
                                CALL `etl_explorer_extrinsics`(`block_start`,`block_end`,`update_status`);
                                CALL `etl_explorer_logs`(`block_start`,`block_end`,`update_status`);
                                CALL `etl_explorer_transfers`(`block_start`,`block_end`,`update_status`);
                                CALL `etl_explorer_blocks`(`block_start`,`block_end`,`update_status`);

                                ### UPDATE STATUS TABLE ###
                                IF @update_status = 1 THEN
                                    INSERT INTO `{settings.DB_NAME}`.`harvester_status` (`key`,`description`,`value`)(
                                        SELECT
                                            'PROCESS_ETL' AS	`key`,
                                            'Max blocknumber of etl process' AS `description`,
                                            CAST(@block_end AS JSON) AS `value`
                                        LIMIT 1
                                    ) ON DUPLICATE KEY UPDATE
                                        `description` = VALUES(`description`),
                                        `value` = VALUES(`value`)
                                    ;
                                END IF;
                            END
                """)
