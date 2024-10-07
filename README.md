# Telegram Activity Checker

This Python script uses Telethon to generate a list of the latest activity (messages or reactions) of each user in a Telegram group chat and outputs the data to a CSV file.

## Prerequisites

- Python 3.6 or higher
- Telegram account
- Telegram API credentials (API ID and API Hash)

## Installation

1. **Clone the Repository**

   Navigate to your desired directory and clone the repository:

   ```bash
   git clone https://github.com/typdas/telegram-activity-checker.git
   cd telegram-activity-checker
   ```

2. **Create a Virtual Environment (Optional)**

   ```bash
   # For Windows
   python -m venv venv
   venv\Scripts\activate

   # For macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**

   Ensure you have `pip` installed, then run:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Obtain Telegram API Credentials**

   - Go to [my.telegram.org](https://my.telegram.org).
   - Log in with your Telegram account.
   - Navigate to the "API Development Tools" section.
   - Create a new application to obtain your `api_id` and `api_hash`.

2. **Edit the `config.yml` File**

   Edit or create the file named `config.yml` in the project directory with the following content:

   ```yaml
   api_id: YOUR_API_ID
   api_hash: YOUR_API_HASH
   session_name: session_name
   group_chat_id: group_chat_id
   ```

   - Replace `YOUR_API_ID` with your actual API ID.
   - Replace `YOUR_API_HASH` with your actual API Hash.
   - Set `session_name` to a name of your choice (e.g., `session_name`).
   - Replace `group_chat_id` with ID of the group chat you want to monitor. [How to find the ID of a group](https://stackoverflow.com/a/72649378).

## Usage

1. **Start the script**

   ```bash
   python app.py
   ```

2. **Enter the start date**

    When prompted, enter the start date in `YYYY-MM-DD` format to fetch messages since that date.
    Example:

     ```bash
     Enter the start date (YYYY-MM-DD) or leave blank to fetch all messages: 2023-10-01
     ```

    If you want to fetch all messages, simply press `Enter` without typing a date.

3. **Authentication (if required)**

   - If this is your first time running the script or your session has expired, you will be prompted to enter your phone number and the code sent by Telegram.

4. **Completion**

   - Once processing is complete, a `latest_activity.csv` file will be generated in the project directory.

## Output

The `latest_activity.csv` file contains the following fields:

- `user_id`: The unique Telegram user ID.
- `username`: The username or full name of the user.
- `date`: The date and time of the latest activity in `YYYY-MM-DD HH:MM:SS` format.
- `type`: Indicates whether the activity was a 'message' or 'reaction'.
- `content`: The content of the message or a placeholder text for reactions.

**Example:**

```csv
user_id,username,date,type,content
123456789,johndoe,2023-10-07 14:23:45,message,Hello everyone!
987654321,janedoe,2023-10-07 13:45:12,reaction,Reacted to message ID 12345
...
```
