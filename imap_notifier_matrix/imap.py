import asyncio
import logging

from imap_tools import MailBox

from nio import SendRetryError

logger = logging.getLogger(__name__)


async def fetch_and_delete(client, config):
    logger.debug(f"Syncing client first time")
    await client.sync(full_state=True, timeout=30000)
    while True:
        with MailBox(config["mail_host"]).login(config["mail_user"], config["mail_pass"]) as mailbox:
            for msg in mailbox.fetch():
                logger.info(f"Received a mail from {msg.from_values['full']}")
                body = msg.text.strip().replace('\r\n', '\n')
                body_msg = f"I received a mail\nFrom: {msg.from_values['full']}\nSubject: {msg.subject}\nBody:\n\n" \
                           f"{body}"
                formatted_msg = f"<p><strong>I received a mail!</strong></p>\n\n<p>From: {msg.from_values['full']}" \
                                f"</br> Subject: {msg.subject}</br>Body:</p>\n\n<pre><code>{body}</code></pre>"

                for room in config["allowed_room_ids"]:
                    try:
                        content = {
                            "msgtype": "m.text",
                            "format": "org.matrix.custom.html",
                            "body": body_msg,
                            "formatted_body": formatted_msg
                        }
                        await client.room_send(
                            room, "m.room.message", content, ignore_unverified_devices=True,
                        )
                    except SendRetryError:
                        logger.exception(f"Unable to send message to {room}")

            mailbox.delete([msg.uid for msg in mailbox.fetch()])

        await asyncio.sleep(60)
