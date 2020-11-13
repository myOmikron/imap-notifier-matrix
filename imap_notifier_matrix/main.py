import logging

from nio import (
    AsyncClient,
    AsyncClientConfig,
    InviteMemberEvent
)

from imap_notifier_matrix.config import JsonConfig
from imap_notifier_matrix.callbacks import Callbacks

from imap_notifier_matrix.run import run

logger = logging.getLogger(__name__)


async def main():
    # Read config file
    class MyConfig(JsonConfig):

        def init(self):
            self["allowed_room_ids"] = []
            self["mail_host"] = ""
            self["mail_imap_port"] = 465
            self["mail_user"] = ""
            self["mail_pass"] = ""

    config = MyConfig("config.json")

    # Configuration options for the AsyncClient
    client_config = AsyncClientConfig(
        max_limit_exceeded=0,
        max_timeouts=0,
        store_sync_tokens=True,
        encryption_enabled=True,
    )

    # Initialize the matrix client
    client = AsyncClient(
        config.homeserver,
        config.user_id,
        device_id=config.device_id,
        store_path=config.store_path,
        config=client_config,
    )

    # Set up event callbacks
    callbacks = Callbacks(client, config)
    client.add_event_callback(callbacks.invite, InviteMemberEvent)
    await run(client, config["matrix"]["user_id"], config["matrix"]["user_password"], config["matrix"]["device_name"], config)
