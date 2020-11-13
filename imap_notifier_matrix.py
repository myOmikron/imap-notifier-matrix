#!/usr/bin/env python3
import asyncio

try:
    from imap_notifier_matrix import main, imap

    # Run the main function of the bot
    asyncio.get_event_loop().run_until_complete(main.main())
except ImportError as e:
    print("Unable to import imap_notifier_matrix.main:", e)
