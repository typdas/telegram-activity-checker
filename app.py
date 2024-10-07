import csv
import asyncio
from datetime import datetime, timezone
import yaml
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import GetMessageReactionsListRequest
from tqdm import tqdm

# Read configuration from config.yml
def load_config(path='config.yml'):
    with open(path, 'r') as file:
        return yaml.safe_load(file)

config = load_config()

api_id = config['api_id']
api_hash = config['api_hash']
session_name = config['session_name']
group_chat_id = config['group_chat_id']

async def main():
    # Prompt the user for the start date
    since_date_str = input("Enter the start date (YYYY-MM-DD) or leave blank to fetch all messages: ")
    if since_date_str:
        try:
            since_date = datetime.strptime(since_date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")
            return
    else:
        since_date = None  # No date filter

    client = TelegramClient(session_name, api_id, api_hash)

    await client.start()
    print("Client Created")

    # Ensure you're authorized
    if not await client.is_user_authorized():
        print("You need to log in.")
        phone = input('Enter your phone number (international format): ')
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code you received: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    # Get the group chat entity
    group_chat = await client.get_entity(group_chat_id)

    # Get the list of participants
    print("Fetching participants...")
    participants = await client.get_participants(group_chat)
    user_ids = {p.id for p in participants}

    # Initialize a dictionary to store latest activity per user
    latest_activity = {}  # user_id: {'date': datetime, 'type': 'message' or 'reaction', 'content': ...}

    # Fetch messages with an indeterminate progress bar
    print("Fetching messages...")
    with tqdm(desc="Processing Messages", unit=" messages") as pbar:
        async for message in client.iter_messages(group_chat):
            # Stop if message is older than since_date (if since_date is specified)
            if since_date and message.date < since_date:
                break

            # Update progress bar
            pbar.update(1)

            # Check for messages
            sender_id = message.sender_id
            if sender_id in user_ids and (sender_id not in latest_activity or message.date > latest_activity[sender_id]['date']):
                latest_activity[sender_id] = {
                    'date': message.date,
                    'type': 'message',
                    'content': message.text or 'Media message'
                }

            # Check for reactions
            if message.reactions:
                # Get reactors
                offset = b''  # Initialize offset as bytes
                while True:
                    result = await client(GetMessageReactionsListRequest(
                        peer=group_chat,
                        id=message.id,
                        limit=100,  # Max 100 per request
                        offset=offset,
                        reaction=None  # None to get all reactions
                    ))
                    reactors = result.users
                    if not reactors:
                        break
                    for user in reactors:
                        user_id = user.id
                        if user_id in user_ids:
                            # Update if this reaction is more recent
                            if (user_id not in latest_activity) or (message.date > latest_activity[user_id]['date']):
                                latest_activity[user_id] = {
                                    'date': message.date,
                                    'type': 'reaction',
                                    'content': f'Reacted to message ID {message.id}'
                                }
                    if result.next_offset is None:
                        break  # No more reactors to fetch
                    offset = result.next_offset
    # Write to CSV
    print("Writing to CSV...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'latest_activity_{timestamp}.csv'
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['user_id', 'username', 'date', 'type', 'content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for user in participants:
            activity = latest_activity.get(user.id)
            if activity:
                if user.deleted:
                    writer.writerow({
                        'user_id': user.id,
                        'username': 'Deleted Account',
                        'date': activity['date'].strftime('%Y-%m-%d %H:%M:%S'),
                        'type': activity['type'],
                        'content': activity['content']
                    })
                else:
                    writer.writerow({
                        'user_id': user.id,
                        'username': user.username or f"{user.first_name} {user.last_name or ''}".strip(),
                        'date': activity['date'].strftime('%Y-%m-%d %H:%M:%S'),
                        'type': activity['type'],
                        'content': activity['content']
                    })
            else:
                if user.deleted:
                    writer.writerow({
                        'user_id': user.id,
                        'username': 'Deleted Account',
                        'date': '',
                        'type': 'No recent activity',
                        'content': ''
                    })
                else:
                    writer.writerow({
                        'user_id': user.id,
                        'username': user.username or f"{user.first_name} {user.last_name or ''}".strip(),
                        'date': '',
                        'type': 'No recent activity',
                        'content': ''
                    })
    print(f"CSV file '{filename}' has been created.")

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())