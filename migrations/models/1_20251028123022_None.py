from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(32) NOT NULL,
    "password" VARCHAR(255) NOT NULL,
    "role" SMALLINT NOT NULL DEFAULT 2
);
CREATE INDEX IF NOT EXISTS "idx_users_usernam_266d85" ON "users" ("username");
CREATE INDEX IF NOT EXISTS "idx_users_role_35db31" ON "users" ("role");
COMMENT ON COLUMN "users"."role" IS 'ADMIN: 1\nAGENT: 2';
CREATE TABLE IF NOT EXISTS "leads" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(128) NOT NULL,
    "phone" VARCHAR(15) NOT NULL,
    "email" VARCHAR(254) NOT NULL,
    "origin_zip" VARCHAR(20) NOT NULL,
    "dest_zip" VARCHAR(20) NOT NULL,
    "vehicle_type" VARCHAR(5) NOT NULL,
    "operable" BOOL NOT NULL,
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
    "eJztmltzmzgUx7+Kh6d0xpuJiXPrG76k9daXnYS0nWYzjAyyzQQEAZHE28133yNxvxZ7nc"
    "Tu+MWDj84B6YfEOX/BT8G0NGy4hzcudoSPjZ8CQSaGg5S92RCQbcdWZqBoanBHDzy4BU1d"
    "6iCVgnGGDBeDScOu6ug21S0CVuIZBjNaKjjqZB6bPKI/eFih1hzTBe/I7R2YdaLhZ+yyv7"
    "f8Orxz0HIrOBZc/Y452ffKTMeGluq9rrEecbtClza3DQi95I6sD1NFtQzPJLGzvaQLi0Te"
    "OqHMOscEO4hidnrqeGxQrM/B4MNx+v2PXfyOJ2I0PEOeQRMQapJRLcKoQm9cPsA5u8ofYq"
    "t91j4/Pm2fgwvvSWQ5e/GHF4/dD+QExrLwwtsRRb4HhxtziyDn6HUXyCnGl4zJQISuZyGG"
    "yKoohoYYYzyhNsTRRM+KgcmcLuDvsVgB7at01f0sXR0cix/YWCyY4v7EHwctIm9iXGOONn"
    "LdJ8spmIXlHJMxu8lRPDmpARK8SknytjRKvtKLFnOfeCYnOYAuIaLiHNEw9NdLe1M0xRxK"
    "QeqNBuOPjdbfRPrUH8vgI6yy1I/Fs9NolbM/VQv8eiQNh/4qZ4/G2X1ikTPDFKn3T8jRlF"
    "RLzNrASHPzsDtB2OWXK2wgPrA81SBhDOEUNegGz8U3nKov4ewIrUEvOClLtMpQ5ZtM0cxa"
    "EEFz3mt2bXalJI2CtBpSKk+r0a145bRqOfpcJ8o/ui34Z6b8mCdZ1cHsDirT5T7VbjzVrp"
    "pmdzvFtsTzGqkBvEpTA2/LZFkAsRLDKGBHIdZJr63y7NrKJVdsIt1YhWAUsJsExZN2rQql"
    "XVGhtLMQ04/QuiTTUTuK86gOzaNymEdZllECWoFkMmbP0ef4iBc6uPkgCln+unzOnuOd2Q"
    "ou1hBp/NtwvUf4hXSv3tcspVOw6zxEy5+huUeoZcPwp0UapWOB/kCkZPknwjJgpxC3nbO2"
    "glxnMhmyTpuu+2Bww0DOMLwZdfqQnzhacNIpTlZKMdGw7EQ0z7QHLVQ3cTHUdGQGqxaEHo"
    "YH28lYgDFoE2IshUCflDOXB6P+tSyN/kqB70lyn7VwnWkuM9aD08zUjk7S+DaQPzfY38aP"
    "ybjPCVounTv8irGf/ENgfUIetRRiPSlIS1TfoTUEk7qxnq2teWPTkfsb+643Nuh8fsFOl8"
    "pKajAXt9ZGzdtvJWxCGub2Z4pw5lleWg7W5+QLXuZyd/F+TLiBv3UQy/ZjwOygp2ijIT9J"
    "YIwwMuxnj+u+3BjfDIfCS539LcvRgpcV629wTdg5tvMJ8y5bXD6Pgj2uCFT5Jld8P155l8"
    "sI9ttgtVDP9Xe3kseJwmG/07Xpna4AdI5dPRUSR7+d/hA0B82okEPq20F8PHgWXBEOoFa/"
    "5wcwt/VH7GBtHUlyUUOSXJRKkousJJkiFyu2o6sFoqSHVd1ERvGkTQdmyyw/8jA4wzYnlS"
    "KOvX53MJKGBy2xKWYkSIi4nZPRM50gYy2Umcg9S4HAkil4Csj4ueQRGgWstfC3Cpjc/y6n"
    "avlw9R6MpO8fUvX8cDL+FLonVnt3OOnsdfLvKKf2Ovk3vbE5ncyq0NUUciLi7T5ieP9qsk"
    "Ich5X8/5TFNT9T2CIR18zo4sTUSCnirnTdlXr9KkH8mnJQwlDyLIQCPRi0NKsEIYp9XlMQ"
    "7iXeGouyWSHxQPm4wa5J3bd2iZAdfWn3Gl+7saWxAsTAfTcBto7qvPYEr/IPGo5yKgOuSD"
    "EpKJz+vJ6MS6rhOCQD8obAAG81XaXNhqG79G47sVZQZKOuFh5ZjZGpetgJOqt9T7j59PLy"
    "HxKD9a8="
)
