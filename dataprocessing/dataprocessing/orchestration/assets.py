from dagster import asset
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dataprocessing.orchestration.resources import AppConfigResource
from dataprocessing.processing import (
    IngestionService,
    DatabaseService,
    AuthHeader,
    embed_and_persist_files,
)
from openai import AsyncOpenAI


@asset
def persist_data(app_config_resource: AppConfigResource) -> None:
    app_config = app_config_resource.get_app_config()
    client = app_config.get_github_client()
    engine = create_engine(app_config.db_connection_string, echo=True)
    Session = sessionmaker(engine)
    db_service = DatabaseService(Session)
    ingestion_service = IngestionService(db_service, client)
    ingestion_service.fetch_and_persist_data()


@asset(deps=[persist_data])
async def persist_embeddings(app_config_resource: AppConfigResource) -> None:
    app_config = app_config_resource.get_app_config()
    engine = create_engine(app_config.db_connection_string, echo=True)
    Session = sessionmaker(engine)
    openai_client = AsyncOpenAI(api_key=app_config.openai_api_key)
    github_token = app_config.github_token
    auth_header = AuthHeader(Authorization="Authorization", token=github_token)
    await embed_and_persist_files(
        session_maker=Session,
        white_list=app_config.whitelisted_extensions,
        api_client=openai_client,
        auth_header=auth_header,
        model=app_config.embedding_model,
        max_characters=app_config.max_embedding_input_length,
        blacklisted_files=app_config.blacklisted_files,
    )
