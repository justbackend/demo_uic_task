from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "audit_logs" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "user_id" BIGINT NOT NULL,
    "endpoint" VARCHAR(255) NOT NULL,
    "payload_hash" VARCHAR(64) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_audit_logs_user_id_fe717c" ON "audit_logs" ("user_id", "created_at");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "audit_logs";"""


MODELS_STATE = (
    "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"
)
