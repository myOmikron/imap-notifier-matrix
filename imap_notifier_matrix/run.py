import logging
from time import sleep

from aiohttp import ClientConnectionError, ServerDisconnectedError
from nio import (
    AsyncClient,
    LocalProtocolError,
    LoginError,
)


logger = logging.getLogger(__name__)


async def run(client: AsyncClient, user_id: str, user_password: str, device_name: str, config):
    """
    This function runs a client as user in an endless loop.
    :param client: the client object to use
    :type client: AsyncClient
    :param user_id: the user to run as
    :type user_id: str
    :param user_password: the user password to authenticate
    :type user_password: str
    :param device_name: the device to run as
    :type device_name: str
    """

    # Keep trying to reconnect on failure (with some time in-between)
    while True:
        try:
            # Try to login with the configured username/password
            try:
                logger.info(f"Trying to log in as {user_id}")
                login_response = await client.login(
                    password=user_password, device_name=device_name,
                )

                # Check if login failed
                if type(login_response) == LoginError:
                    logger.error("Failed to login: %s", login_response.message)
                    return False
            except LocalProtocolError as e:
                # There's an edge case here where the user hasn't installed the correct C
                # dependencies. In that case, a LocalProtocolError is raised on login.
                logger.fatal(
                    "Failed to login. Have you installed the correct dependencies? "
                    "https://github.com/poljar/matrix-nio#installation "
                    "Error: %s",
                    e,
                )
                return False

            # Login succeeded!
            logger.info(f"Logged in as {user_id}")

            from imap_notifier_matrix.imap import fetch_and_delete
            import asyncio
            asyncio.get_event_loop().create_task(fetch_and_delete(client, config))
            await client.sync_forever(timeout=30000, full_state=True, loop_sleep_time=100)

        except (ClientConnectionError, ServerDisconnectedError):
            logger.warning("Unable to connect to homeserver, retrying in 15s...")

            # Sleep so we don't bombard the server with login requests
            sleep(15)
        finally:
            # Make sure to close the client connection on disconnect
            await client.close()
