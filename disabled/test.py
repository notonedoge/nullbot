import asyncio
from twitchAPI.twitch import Twitch
from twitchAPI.helper import first
from twitchAPI.type import AuthScope
from twitchAPI.eventsub.webhook import EventSubWebhook
from twitchAPI.object.eventsub import ChannelFollowEvent, StreamOnlineEvent, StreamOfflineEvent

# Your Twitch application credentials
CLIENT_ID = 'cbpx761vtg0ycz6di9111zyhmnypjx'
CLIENT_SECRET = 'b78jk9zksqxd36kvxaavk3rf5n43lb'
CALLBACK_URL = 'https://echolocation.cc/eventsub/callback'  # Must be HTTPS (just the domain)
WEBHOOK_SECRET = '49357382870486834'  # Create a random string (16-100 chars)

# Target channel username
TARGET_CHANNEL = 'xarrak99'


async def on_stream_online(data: StreamOnlineEvent):
    """Called when the stream goes online"""
    print(f'🔴 Stream is now ONLINE!')
    print(f'   Broadcaster: {data.event.broadcaster_user_name}')
    print(f'   Started at: {data.event.started_at}')
    print(f'   Type: {data.event.type}')


async def on_stream_offline(data: StreamOfflineEvent):
    """Called when the stream goes offline"""
    print(f'⚫ Stream is now OFFLINE!')
    print(f'   Broadcaster: {data.event.broadcaster_user_name}')


async def main():
    # Initialize Twitch API (app access token is automatic)
    twitch = await Twitch(CLIENT_ID, CLIENT_SECRET)

    # Get the user ID for the target channel
    user = await first(twitch.get_users(logins=[TARGET_CHANNEL]))
    if not user:
        print(f"User {TARGET_CHANNEL} not found!")
        return

    user_id = user.id
    print(f"Found user: {user.display_name} (ID: {user_id})")

    # Set up EventSub webhook
    eventsub = EventSubWebhook(
        callback_url=CALLBACK_URL,
        port=8081,
        twitch=twitch
    )

    # Start the webhook server
    eventsub.start()
    print("EventSub webhook server started on port 8081\n")

    # Subscribe to events
    try:
        # Subscribe to stream online events
        await eventsub.listen_stream_online(
            broadcaster_user_id=user_id,
            callback=on_stream_online
        )
        print(f"✓ Subscribed to stream online events")

        # Subscribe to stream offline events
        await eventsub.listen_stream_offline(
            broadcaster_user_id=user_id,
            callback=on_stream_offline
        )
        print(f"✓ Subscribed to stream offline events")

        print("\n🚀 EventSub is running. Press Ctrl+C to stop.\n")

        # Keep the program running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n\nShutting down...")

    finally:
        # Clean up
        await eventsub.stop()
        await twitch.close()


if __name__ == '__main__':
    asyncio.run(main())