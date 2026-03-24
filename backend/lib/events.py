from datetime import datetime
from lib.websocket_manager import manager
import json

async def dispatch_event(user_id: str, event_type: str, data: dict):
    """
    Simulates a notification event. In this simplified version, it sends a websocket message.
    In a real app, this would push to Kafka/Redis.
    """
    message = {
        "event_type": event_type,
        "data": data,
        "timestamp": str(datetime.utcnow())
    }
    await manager.send_personal_message(json.dumps(message), user_id)


