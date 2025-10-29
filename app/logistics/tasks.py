import json
import uuid
from decimal import Decimal
from redis.asyncio import Redis

from app.logistics.schemas import QuoteCalcRequest
from app.logistics.services import OrderService
from app.service.redis_service import get_redis
import logging
logger = logging.getLogger("app")


TASK_QUEUE_KEY = "order_reprice_queue"


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


async def enqueue_reprice(order_id: int, order_data: dict) -> str:
    task_id = str(uuid.uuid4())
    redis: Redis = await get_redis()

    payload = {
        "task_id": task_id,
        "order_id": order_id,
        "data": order_data,
    }

    await redis.lpush(TASK_QUEUE_KEY, json.dumps(payload, cls=EnhancedJSONEncoder))
    return task_id


async def reprice_worker():
    redis: Redis = await get_redis()
    while True:
        _, raw = await redis.brpop(TASK_QUEUE_KEY)
        task = json.loads(raw)
        data = QuoteCalcRequest(**task["data"])
        result = OrderService.calculate_price(data)
        logger.info(f"[Task {task['task_id']}] Repriced order {task['order_id']}: {result.final_price}")
