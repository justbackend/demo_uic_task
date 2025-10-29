from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(32) NOT NULL,
    "password" VARCHAR(255) NOT NULL,
    "role" VARCHAR(5) NOT NULL DEFAULT 'agent'
);
CREATE INDEX IF NOT EXISTS "idx_users_usernam_266d85" ON "users" ("username");
CREATE INDEX IF NOT EXISTS "idx_users_role_35db31" ON "users" ("role");
COMMENT ON COLUMN "users"."role" IS 'ADMIN: admin\nAGENT: agent';
CREATE TABLE IF NOT EXISTS "audit_logs" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "user_id" BIGINT NOT NULL,
    "endpoint" VARCHAR(255) NOT NULL,
    "payload_hash" VARCHAR(64) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS "idx_audit_logs_user_id_fe717c" ON "audit_logs" ("user_id", "created_at");
CREATE TABLE IF NOT EXISTS "leads" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(128) NOT NULL,
    "phone" VARCHAR(15) NOT NULL,
    "email" VARCHAR(254) NOT NULL,
    "origin_zip" VARCHAR(20) NOT NULL,
    "dest_zip" VARCHAR(20) NOT NULL,
    "vehicle_type" VARCHAR(5) NOT NULL,
    "operable" BOOL NOT NULL,
    "attachment" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_by_id" INT REFERENCES "users" ("id") ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS "idx_leads_origin__1579ff" ON "leads" ("origin_zip", "dest_zip");
CREATE INDEX IF NOT EXISTS "idx_leads_created_675f57" ON "leads" ("created_by_id");
COMMENT ON COLUMN "leads"."vehicle_type" IS 'sedan | suv | truck';
CREATE TABLE IF NOT EXISTS "orders" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "status" VARCHAR(9) NOT NULL DEFAULT 'draft',
    "base_price" DECIMAL(12,2),
    "final_price" DECIMAL(12,2),
    "notes" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "lead_id" INT NOT NULL REFERENCES "leads" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_orders_lead_id_dc8178" ON "orders" ("lead_id", "status");
CREATE INDEX IF NOT EXISTS "idx_orders_status_33ec6d" ON "orders" ("status");
CREATE INDEX IF NOT EXISTS "idx_orders_created_cdc9e7" ON "orders" ("created_at");
COMMENT ON COLUMN "orders"."status" IS 'draft | quoted | booked | delivered';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "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"
)
