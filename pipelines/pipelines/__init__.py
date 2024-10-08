import os
from dagster import (
    Definitions,
    ScheduleDefinition,
    define_asset_job,
    load_assets_from_modules,
)
from dotenv import load_dotenv
from pipelines.orchestration.resources import AppConfigResource
from shared.database import run_migrations
from .orchestration import assets
from shared.log import setup_custom_logger


logger = setup_custom_logger("app_logger")
if not os.getenv("PRODUCTION"):
    logger.warning("Running in development mode")
    load_dotenv("../config/.env.secret.dev")


run_migrations("../shared/shared/migrations", logger)

all_assets = load_assets_from_modules([assets])
all_assets_job = define_asset_job(name="all_assets_job")

ingestion_schedule = ScheduleDefinition(
    job=all_assets_job,
    cron_schedule="0 0 * * *",
)

defs = Definitions(
    assets=all_assets,
    resources={"app_config_resource": AppConfigResource.from_env()},
    schedules=[ingestion_schedule],
)
