"""etl procedures

Revision ID: b20ef0859147
Revises: 567ddcab4f81
Create Date: 2022-06-21 15:14:26.431058

"""
from alembic import op
import sqlalchemy as sa

from dotenv import load_dotenv
import sys, os
sys.path = ['', '..', '../..'] + sys.path[1:]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env_file = ".env"
if os.path.exists(".local.env"):
    env_file = ".local.env"


load_dotenv(os.path.join(BASE_DIR, "../..", env_file))
sys.path.append(BASE_DIR)

# Mock required settings to run this migration which depends on user settings
class settings:
    DB_USERNAME = os.environ['DB_USERNAME']
    DB_NAME = os.environ['DB_NAME']
    DB_HARVESTER_NAME = os.environ['DB_HARVESTER_NAME'] or "polkascan"


# revision identifiers, used by Alembic.
revision = 'b20ef0859147'
down_revision = '567ddcab4f81'
# Note: you can always rerun this migration independend: alembic upgrade b20ef0859147
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP PROCEDURE IF EXISTS `etl`")
    op.execute(f"""
        CREATE DEFINER=`{settings.DB_USERNAME}`@`%` PROCEDURE `etl`(`block_start` INT(11), `block_end` INT(11), `update_status` INT(1))
        BEGIN
                DECLARE `idx` INT;
                SET `idx` = `block_start`;
                SET @update_status = `update_status`;
                label1:
                WHILE `idx` <= `block_end` DO
                    CALL `etl_range`(`idx`,`idx`,`update_status`);
                    SET `idx` = `idx` + 1;
                END WHILE label1;
            END
                    """)

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

    op.execute("DROP PROCEDURE IF EXISTS `etl_explorer_blocks`")
    op.execute(f"""
            CREATE DEFINER=`{settings.DB_USERNAME}`@`%` PROCEDURE `etl_explorer_blocks`(`block_start` INT(11), `block_end` INT(11), `update_status` INT(1))
    BEGIN
            # GLOBAL SETTINGS
            SET @block_start = `block_start`;
            SET @block_end = `block_end`;
            SET @update_status = `update_status`;

            INSERT INTO `{settings.DB_NAME}`.`explorer_block` (
                `number`,
                `parent_number`,
                `hash`,
                `parent_hash`,
                `state_root`,
                `extrinsics_root`,
                `datetime`,
                `author_authority_index`,
                `author_slot_number`,
                `author_account_id`,
                `count_extrinsics`,
                `count_events`,
                `count_logs`,
                `spec_name`,
                `spec_version`,
                `complete`
            )(
                SELECT
                    `nbh`.`block_number` AS `number`,
                    IF(`nbh`.`block_number`=0,NULL,(`nbh`.`block_number`-1)) AS `parent_number`,
                    `nbh`.`hash` AS `hash`,
                    `nbh`.`parent_hash` AS `parent_hash`,
                    `nbh`.`state_root` AS `state_root`,
                    `nbh`.`extrinsics_root` AS `extrinsics_root`,
                    `cbts`.`datetime` AS `datetime`,
                    NULL AS `author_authority_index`,
                    NULL AS `author_slot_number`,
                    NULL AS `author_account_id`,
                    `nbh`.`count_extrinsics`,
                    (SELECT COUNT(*) FROM `{settings.DB_HARVESTER_NAME}`.`codec_block_event` AS `cbev` WHERE `cbev`.`block_hash`=`nbh`.`hash`) AS `count_events`,
                    `nbh`.`count_logs`,
                    `nbr`.`spec_name` AS `spec_name`,
                    `nbr`.`spec_version` AS `spec_version`,
                    1 AS `complete`
                FROM `{settings.DB_HARVESTER_NAME}`.`node_block_header` AS `nbh`
                INNER JOIN `{settings.DB_HARVESTER_NAME}`.`node_block_runtime` AS `nbr` ON `nbr`.`hash` = `nbh`.`hash` AND `nbr`.`block_number` >= @block_start AND	`nbr`.`block_number` <= @block_end
                INNER JOIN `{settings.DB_HARVESTER_NAME}`.`codec_block_timestamp` AS `cbts` ON `nbr`.`hash` = `cbts`.`block_hash` AND `cbts`.`block_number` >= @block_start AND	`cbts`.`block_number` <= @block_end
                WHERE `nbh`.`block_number` >= @block_start AND	`nbh`.`block_number` <= @block_end
            ) ON DUPLICATE KEY UPDATE
                `parent_number` = VALUES(`parent_number`),
                `hash` = VALUES(`hash`),
                `parent_hash` = VALUES(`parent_hash`),
                `state_root` = VALUES(`state_root`),
                `extrinsics_root` = VALUES(`extrinsics_root`),
                `datetime` = VALUES(`datetime`),
                `author_authority_index` = VALUES(`author_authority_index`),
                `author_slot_number` = VALUES(`author_slot_number`),
                `author_account_id` = VALUES(`author_account_id`),
                `count_extrinsics` = VALUES(`count_extrinsics`),
                `count_events` = VALUES(`count_events`),
                `count_logs` = VALUES(`count_logs`),
                `spec_name` = VALUES(`spec_name`),
                `spec_version` = VALUES(`spec_version`),
                `complete` = VALUES(`complete`)
            ;

    				### UPDATE STATUS TABLE ###
    				IF @update_status = 1 THEN
    						INSERT INTO `{settings.DB_NAME}`.`harvester_status` (`key`,`description`,`value`)(
    								SELECT
    										'PROCESS_ETL_EXPLORER_BLOCKS' AS	`key`,
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

    op.execute("DROP PROCEDURE IF EXISTS `etl_explorer_events`")
    op.execute(f"""
            CREATE DEFINER=`{settings.DB_USERNAME}`@`%` PROCEDURE `etl_explorer_events`(`block_start` INT(11), `block_end` INT(11), `update_status` INT(1))
            BEGIN
                    # GLOBAL SETTINGS
                    SET @block_start = `block_start`;
                    SET @block_end = `block_end`;
                    SET @update_status = `update_status`;

                    INSERT INTO `{settings.DB_NAME}`.`explorer_event` (
                        `block_number`,
                        `event_idx`,
                        `extrinsic_idx`,
                        `event`,
                        `event_module`,
                        `event_name`,
                        `phase_idx`,
                        `phase_name`,
                        `attributes`,
                        `topics`,
                        `block_datetime`,
                        `block_hash`,
                        `spec_name`,
                        `spec_version`,
                        `complete`
                    )(
                        SELECT
                            `cbev`.`block_number` AS `block_number`,
                            `cbev`.`event_idx` AS `event_idx`,
                            `cbev`.`extrinsic_idx` AS `extrinsic_idx`,
                            UNHEX(RIGHT(JSON_UNQUOTE(`cbev`.`data`->"$.event.event_index"),4)) AS `event`,
                            `cbev`.`event_module` AS `event_module`,
                            `cbev`.`event_name` AS `event_name`,
                            NULL AS `phase_idx`,
                            JSON_UNQUOTE(`cbev`.`data`->"$.phase") AS `phase_name`,
                            `cbev`.`data`->"$.event.attributes" AS `attributes`,
                            JSON_UNQUOTE(`cbev`.`data`->"$.topics") AS `topics`,
                            `cbts`.`datetime` AS `block_datetime`,
                            `cbev`.`block_hash` AS `block_hash`,
                            `nbr`.`spec_name` AS `spec_name`,
                            `nbr`.`spec_version` AS `spec_version`,
                            IF(`cbev`.`complete`=1,1,0) AS `complete`
                        FROM `{settings.DB_HARVESTER_NAME}`.`codec_block_event` AS `cbev`
                        INNER JOIN `{settings.DB_HARVESTER_NAME}`.`node_block_header` AS `nbh` ON `cbev`.`block_hash` = `nbh`.`hash` AND `nbh`.`block_number` >= @block_start AND	`nbh`.`block_number` <= @block_end
                        INNER JOIN `{settings.DB_HARVESTER_NAME}`.`node_block_runtime` AS `nbr` ON `cbev`.`block_hash` = `nbr`.`hash` AND `nbr`.`block_number` >= @block_start AND	`nbr`.`block_number` <= @block_end
                        INNER JOIN `{settings.DB_HARVESTER_NAME}`.`codec_block_timestamp` AS `cbts` ON `cbev`.`block_hash` = `cbts`.`block_hash` AND `cbts`.`block_number` >= @block_start AND	`cbts`.`block_number` <= @block_end
                        WHERE	`cbev`.`block_number` >= @block_start AND	`cbev`.`block_number` <= @block_end
                    ) ON DUPLICATE KEY UPDATE
                        `extrinsic_idx` = VALUES(`extrinsic_idx`),
                        `event` = VALUES(`event`),
                        `event_module` = VALUES(`event_module`),
                        `event_name` = VALUES(`event_name`),
                        `phase_idx` = VALUES(`phase_idx`),
                        `phase_name` = VALUES(`phase_name`),
                        `attributes` = VALUES(`attributes`),
                        `topics` = VALUES(`topics`),
                        `block_datetime` = VALUES(`block_datetime`),
                        `block_hash` = VALUES(`block_hash`),
                        `spec_name` = VALUES(`spec_name`),
                        `spec_version` = VALUES(`spec_version`),
                        `complete` = VALUES(`complete`)
                    ;

                            ### UPDATE STATUS TABLE ###
                            IF @update_status = 1 THEN
                                    INSERT INTO `{settings.DB_NAME}`.`harvester_status` (`key`,`description`,`value`)(
                                            SELECT
                                                    'PROCESS_ETL_EXPLORER_EVENTS' AS	`key`,
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

    op.execute("DROP PROCEDURE IF EXISTS `etl_explorer_extrinsics`")
    op.execute(f"""
            CREATE DEFINER=`{settings.DB_USERNAME}`@`%` PROCEDURE `etl_explorer_extrinsics`(`block_start` INT(11), `block_end` INT(11), `update_status` INT(1))
            BEGIN
                    # GLOBAL SETTINGS
                    SET @block_start = `block_start`;
                    SET @block_end = `block_end`;
                    SET @update_status = `update_status`;

                    INSERT INTO `{settings.DB_NAME}`.`explorer_extrinsic` (
                        `block_number`,
                        `extrinsic_idx`,
                        `hash`,
                        `version`,
                        `version_info`,
                        `call`,
                        `call_module`,
                        `call_name`,
                        `call_arguments`,
                        `call_hash`,
                        `signed`,
                        `signature`,
                        `signature_version`,
                        `multi_address_type`,
                        `multi_address_account_id`,
                        `multi_address_account_index`,
                        `multi_address_raw`,
                        `multi_address_address_32`,
                        `multi_address_address_20`,
                        `extrinsic_length`,
                        `nonce`,
                        `era`,
                        `era_immortal`,
                        `era_birth`,
                        `era_death`,
                        `tip`,
                        `block_datetime`,
                        `block_hash`,
                        `spec_name`,
                        `spec_version`,
                        `complete`
                    )(
                        SELECT
                            `cbex`.`block_number` AS `block_number`,
                            `cbex`.`extrinsic_idx` AS `extrinsic_idx`,
                            `nbex`.`hash` AS `hash`,
                            NULL AS `version`,
                            NULL AS `version_info`,
                            UNHEX(RIGHT(JSON_UNQUOTE(`cbex`.`data`->"$.call.call_index"),4)) AS `call`,
                            `cbex`.`call_module` AS `call_module`,
                            `cbex`.`call_name` AS `call_name`,
                            JSON_UNQUOTE(`cbex`.`data`->"$.call.call_args") AS `call_arguments`,
                            UNHEX(RIGHT(JSON_UNQUOTE(`cbex`.`data`->"$.call.call_hash"),64)) AS `call_hash`,
                            `cbex`.`signed` AS `signed`,
                            UNHEX(REPLACE(JSON_UNQUOTE(JSON_EXTRACT(`cbex`.`data`, CONCAT("$.signature.",JSON_UNQUOTE(JSON_EXTRACT(JSON_KEYS(`cbex`.`data`->"$.signature"), '$[0]'))))),"0x","")) AS `signature`,
                            JSON_UNQUOTE(JSON_EXTRACT(JSON_KEYS(`cbex`.`data`->"$.signature"), '$[0]')) AS `signature_version`,
                            NULL AS `multi_address_type`,
                            UNHEX(RIGHT(JSON_UNQUOTE(`cbex`.`data`->"$.address"),64)) AS `multi_address_account_id`,
                            NULL AS `multi_address_account_index`,
                            NULL AS `multi_address_raw`,
                            NULL AS `multi_address_address_32`,
                            NULL AS `multi_address_address_20`,
                            JSON_UNQUOTE(`cbex`.`data`->"$.extrinsic_length") AS `extrinsic_length`,
                            JSON_UNQUOTE(`cbex`.`data`->"$.nonce") AS `nonce`,
                            `cbex`.`data`->"$.era" AS `era`,
                            CASE JSON_UNQUOTE(`cbex`.`data`->"$.era")
                                WHEN '00' THEN 1
                                ELSE 0
                            END AS `era_immortal`,
                            NULL AS `era_birth`,
                            NULL AS `era_death`,
                            JSON_UNQUOTE(`cbex`.`data`->"$.tip") AS `tip`,
                            `cbts`.`datetime` AS `block_datetime`,
                            `cbex`.`block_hash` AS `block_hash`,
                            `nbr`.`spec_name` AS `spec_name`,
                            `nbr`.`spec_version` AS `spec_version`,
                            IF(`cbex`.`complete`=1,1,0) AS `complete`
                        FROM `{settings.DB_HARVESTER_NAME}`.`codec_block_extrinsic` AS `cbex`
                        INNER JOIN `{settings.DB_HARVESTER_NAME}`.`node_block_extrinsic` AS `nbex` ON `cbex`.`block_hash` = `nbex`.`block_hash` AND `cbex`.`extrinsic_idx` = `nbex`.`extrinsic_idx` AND `nbex`.`block_number` >= @block_start AND	`nbex`.`block_number` <= @block_end
                        INNER JOIN `{settings.DB_HARVESTER_NAME}`.`node_block_header` AS `nbh` ON `cbex`.`block_hash` = `nbh`.`hash` AND `nbh`.`block_number` >= @block_start AND	`nbh`.`block_number` <= @block_end
                        INNER JOIN `{settings.DB_HARVESTER_NAME}`.`node_block_runtime` AS `nbr` ON `cbex`.`block_hash` = `nbr`.`hash` AND `nbr`.`block_number` >= @block_start AND	`nbr`.`block_number` <= @block_end
                        INNER JOIN `{settings.DB_HARVESTER_NAME}`.`codec_block_timestamp` AS `cbts` ON `cbex`.`block_hash` = `cbts`.`block_hash` AND `cbts`.`block_number` >= @block_start AND	`cbts`.`block_number` <= @block_end
                        WHERE `cbex`.`block_number` >= @block_start AND	`cbex`.`block_number` <= @block_end
                    ) ON DUPLICATE KEY UPDATE
                        `hash` = VALUES(`hash`),
                        `version` = VALUES(`version`),
                        `version_info` = VALUES(`version_info`),
                        `call` = VALUES(`call`),
                        `call_module` = VALUES(`call_module`),
                        `call_name` = VALUES(`call_name`),
                        `call_arguments` = VALUES(`call_arguments`),
                        `call_hash` = VALUES(`call_hash`),
                        `signed` = VALUES(`signed`),
                        `signature` = VALUES(`signature`),
                        `signature_version` = VALUES(`signature_version`),
                        `multi_address_type` = VALUES(`multi_address_type`),
                        `multi_address_account_id` = VALUES(`multi_address_account_id`),
                        `multi_address_account_index` = VALUES(`multi_address_account_index`),
                        `multi_address_raw` = VALUES(`multi_address_raw`),
                        `multi_address_address_32` = VALUES(`multi_address_address_32`),
                        `multi_address_address_20` = VALUES(`multi_address_address_20`),
                        `extrinsic_length` = VALUES(`extrinsic_length`),
                        `nonce` = VALUES(`nonce`),
                        `era` = VALUES(`era`),
                        `era_immortal` = VALUES(`era_immortal`),
                        `era_birth` = VALUES(`era_birth`),
                        `era_death` = VALUES(`era_death`),
                        `tip` = VALUES(`tip`),
                        `block_datetime` = VALUES(`block_datetime`),
                        `block_hash` = VALUES(`block_hash`),
                        `spec_name` = VALUES(`spec_name`),
                        `spec_version` = VALUES(`spec_version`),
                        `complete` = VALUES(`complete`)
                    ;

                            ### UPDATE STATUS TABLE ###
                            IF @update_status = 1 THEN
                                    INSERT INTO `{settings.DB_NAME}`.`harvester_status` (`key`,`description`,`value`)(
                                            SELECT
                                                    'PROCESS_ETL_EXPLORER_EXTRINSICS' AS	`key`,
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

    op.execute("DROP PROCEDURE IF EXISTS `etl_explorer_logs`")
    op.execute(f"""
            CREATE DEFINER=`{settings.DB_USERNAME}`@`%` PROCEDURE `etl_explorer_logs`(`block_start` INT(11), `block_end` INT(11), `update_status` INT(1))
            BEGIN
                    # GLOBAL SETTINGS
                    SET @block_start = `block_start`;
                    SET @block_end = `block_end`;
                    SET @update_status = `update_status`;

                            INSERT INTO `{settings.DB_NAME}`.`explorer_log` (
                                `block_number`,
                                `log_idx`,
                                `type_id`,
                                `type_name`,
                                `data`,
                                `block_datetime`,
                                `block_hash`,
                                `spec_name`,
                                `spec_version`,
                                `complete`
                            )(
                                SELECT
                                    `cbhdl`.`block_number` AS `block_number`,
                                    `cbhdl`.`log_idx` AS `log_idx`,
                                    NULL AS `type_id`,
                                    JSON_UNQUOTE(JSON_EXTRACT(JSON_KEYS(`cbhdl`.`data`),"$[0]")) AS `type_name`,
                                    `cbhdl`.`data`,
                                    `cbts`.`datetime` AS `block_datetime`,
                                    `cbhdl`.`block_hash`,
                                    `nbr`.`spec_name` AS `spec_name`,
                                    `nbr`.`spec_version` AS `spec_version`,
                                    `cbhdl`.`complete`
                                FROM `{settings.DB_HARVESTER_NAME}`.`codec_block_header_digest_log` AS `cbhdl`
                                INNER JOIN `{settings.DB_HARVESTER_NAME}`.`node_block_runtime` AS `nbr` ON `cbhdl`.`block_hash` = `nbr`.`hash` AND `nbr`.`block_number` >= @block_start AND	`nbr`.`block_number` <= @block_end
                                INNER JOIN `{settings.DB_HARVESTER_NAME}`.`codec_block_timestamp` AS `cbts` ON `cbhdl`.`block_hash` = `cbts`.`block_hash` AND `cbts`.`block_number` >= @block_start AND	`cbts`.`block_number` <= @block_end
                                WHERE	`cbhdl`.`block_number` >= @block_start AND	`cbhdl`.`block_number` <= @block_end
                            ) ON DUPLICATE KEY UPDATE
                                    `type_id` = VALUES(`type_id`),
                                    `type_name` = VALUES(`type_name`),
                                    `data` = VALUES(`data`),
                                    `block_datetime` = VALUES(`block_datetime`),
                                    `block_hash` = VALUES(`block_hash`),
                                    `spec_name` = VALUES(`spec_name`),
                                    `spec_version` = VALUES(`spec_version`),
                                    `complete` = VALUES(`complete`)
                            ;

                            ### UPDATE STATUS TABLE ###
                            IF @update_status = 1 THEN
                                    INSERT INTO `{settings.DB_NAME}`.`harvester_status` (`key`,`description`,`value`)(
                                            SELECT
                                                    'PROCESS_ETL_EXPLORER_LOGS' AS	`key`,
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

    op.execute("DROP PROCEDURE IF EXISTS `etl_explorer_transfers`")
    op.execute(f"""
            CREATE DEFINER=`{settings.DB_USERNAME}`@`%` PROCEDURE `etl_explorer_transfers`(`block_start` INT(11), `block_end` INT(11), `update_status` INT(1))
            BEGIN
                    # GLOBAL SETTINGS
                    SET @block_start = `block_start`;
                    SET @block_end = `block_end`;
                    SET @update_status = `update_status`;

                    INSERT INTO `{settings.DB_NAME}`.`explorer_transfer` (
                                        `block_number`,
                                        `event_idx`,
                                        `extrinsic_idx`,
                                        `from_multi_address_type`,
                                        `from_multi_address_account_id`,
                                        `to_multi_address_type`,
                                        `to_multi_address_account_id`,
                                        `value`,
                                        `block_datetime`,
                                        `block_hash`,
                                        `complete`
                    )(
                                SELECT
                                        `cbev`.`block_number` AS `block_number`,
                                        `cbev`.`event_idx` AS `event_idx`,
                                        `cbev`.`extrinsic_idx` AS `extrinsic_idx`,
                                        0 AS `from_multi_address_type`,
                                        UNHEX(RIGHT(JSON_UNQUOTE(`cbev`.`data`->"$.event.attributes[0]"),64)) AS `from_multi_address_account_id`,
                                        0 AS `to_multi_address_type`,
                                        UNHEX(RIGHT(JSON_UNQUOTE(`cbev`.`data`->"$.event.attributes[1]"),64)) AS `to_multi_address_account_id`,
                                        JSON_UNQUOTE(`cbev`.`data`->"$.event.attributes[2]") AS `value`,
                                        `cbts`.`datetime` AS `block_datetime`,
                                        `cbev`.`block_hash` AS `block_hash`,
                                        `cbev`.`complete` AS `complete`
                                FROM `{settings.DB_HARVESTER_NAME}`.`codec_block_event` AS `cbev`
                                INNER JOIN `{settings.DB_HARVESTER_NAME}`.`node_block_header` AS `nbh` ON `cbev`.`block_hash` = `nbh`.`hash` AND `nbh`.`block_number` >= @block_start AND	`nbh`.`block_number` <= @block_end
                                INNER JOIN `{settings.DB_HARVESTER_NAME}`.`node_block_runtime` AS `nbr` ON `cbev`.`block_hash` = `nbr`.`hash` AND `nbr`.`block_number` >= @block_start AND	`nbr`.`block_number` <= @block_end
                                INNER JOIN `{settings.DB_HARVESTER_NAME}`.`codec_block_timestamp` AS `cbts` ON `cbev`.`block_hash` = `cbts`.`block_hash` AND `cbts`.`block_number` >= @block_start AND	`cbts`.`block_number` <= @block_end
                                WHERE	`cbev`.`block_number` >= @block_start AND	`cbev`.`block_number` <= @block_end
                                AND `cbev`.`event_module`='Balances' AND `cbev`.`event_name`='Transfer'
                    ) ON DUPLICATE KEY UPDATE
                                    `extrinsic_idx` = VALUES(`extrinsic_idx`),
                                    `from_multi_address_type` = VALUES(`from_multi_address_type`),
                                    `from_multi_address_account_id` = VALUES(`from_multi_address_account_id`),
                                    `to_multi_address_type` = VALUES(`to_multi_address_type`),
                                    `to_multi_address_account_id` = VALUES(`to_multi_address_account_id`),
                                    `value` = VALUES(`value`),
                                    `block_datetime` = VALUES(`block_datetime`),
                                    `block_hash` = VALUES(`block_hash`),
                                    `complete` = VALUES(`complete`)
                    ;

                            ### UPDATE STATUS TABLE ###
                            IF @update_status = 1 THEN
                                    INSERT INTO `{settings.DB_NAME}`.`harvester_status` (`key`,`description`,`value`)(
                                            SELECT
                                                    'PROCESS_ETL_EXPLORER_TRANSFERS' AS	`key`,
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
    op.execute("DROP PROCEDURE IF EXISTS `etl`")
    op.execute("DROP PROCEDURE IF EXISTS `etl_range`")
    op.execute("DROP PROCEDURE IF EXISTS `etl_explorer_blocks`")
    op.execute("DROP PROCEDURE IF EXISTS `etl_explorer_events`")
    op.execute("DROP PROCEDURE IF EXISTS `etl_explorer_extrinsics`")
    op.execute("DROP PROCEDURE IF EXISTS `etl_explorer_transfers`")
    op.execute("DROP PROCEDURE IF EXISTS `etl_explorer_logs`")
