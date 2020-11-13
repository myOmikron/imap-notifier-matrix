import logging

from nio import JoinError

logger = logging.getLogger(__name__)


class Callbacks(object):
    def __init__(self, client, config):
        """
        Args:
            client (nio.AsyncClient): nio client used to interact with matrix

            config (Config): Bot configuration parameters
        """
        self.client = client
        self.config = config

    async def invite(self, room, event):
        """Callback for when an invite is received. Join the room specified in the invite"""
        logger.info(f"Got invite to {room.room_id} from {event.sender}.")
        if room.room_id not in self.config["allowed_room_ids"]:
            return

        # Attempt to join 3 times before giving up
        for attempt in range(3):
            result = await self.client.join(room.room_id)
            if type(result) == JoinError:
                logger.error(
                    f"Error joining room {room.room_id} (attempt %d): %s",
                    attempt,
                    result.message,
                )
            else:
                break
        else:
            logger.error("Unable to join room: %s", room.room_id)

        # Successfully joined room
        logger.info(f"Joined {room.room_id}")
