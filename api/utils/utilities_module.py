import base64
import os
import json
from flask import g, current_app, jsonify
import time

# Other imports
from google.auth import exceptions
from google.oauth2 import credentials as creds
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase
import mimetypes


# cc and bcc are string comma separated emails
def send_email(to_email, subject, body, html=None, attachments=None, cc=None, bcc=None, reply_to=None, from_email=None):
    refresh_token = current_app.config['REFRESH_TOKEN']  # GMail Refresh Token
    client_id = current_app.config['CLIENT_ID']  # GMail Client ID
    client_secret = current_app.config['CLIENT_SECRET']  # GMail Client Secret
    if from_email is None:
        from_email = current_app.config['DEFAULT_EMAIL']

    credentials = None

    # credentials for service account
    creds_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    credentials = creds.Credentials.from_authorized_user_info(
        creds_data)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            raise exceptions.RefreshError(
                "Could not refresh access token due to invalid or missing credentials."
            )

    service = build('gmail', 'v1', credentials=credentials)

    # create email
    email_message = MIMEMultipart()
    email_message['to'] = to_email
    email_message['from'] = from_email
    email_message['subject'] = subject

    if cc is not None:  # If CC is provided
        email_message['cc'] = cc

    if bcc is not None:  # If BCC is provided
        email_message['bcc'] = bcc

    if reply_to is not None:  # If reply-to is provided
        email_message['Reply-To'] = reply_to

    # Create MIMEMultipart for alternative text and HTML content
    text_html_multipart = MIMEMultipart("alternative")

    # Attach the text part first, and the HTML part second.
    # Email clients are supposed to display the last version they can handle.
    text_html_multipart.attach(MIMEText(body, 'plain'))

    # If HTML is provided
    if html is not None:
        text_html_multipart.attach(MIMEText(html, 'html'))

    # Attach the text_html_multipart to the main email message
    email_message.attach(text_html_multipart)

    # Attach files
    if attachments is not None:
        for filename in attachments:
            mimetype, _ = mimetypes.guess_type(filename)
            mime_type, mime_subtype = mimetype.split('/')
            with open(filename, 'rb') as f:
                mime_part = MIMEBase(mime_type, mime_subtype)
                mime_part.set_payload(f.read())
                encoders.encode_base64(mime_part)
                mime_part.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=os.path.basename(filename)
                )
                email_message.attach(mime_part)

    raw_string = base64.urlsafe_b64encode(email_message.as_bytes()).decode()

    message = service.users().messages().send(
        userId='me', body={'raw': raw_string}).execute()
    # print('Message Id: %s' % message['id'])
    return message


def is_production():
    return current_app.config['IS_PRODUCTION']


def escape(string):
    return string.replace("\n", "\\n")


def descape(string):
    return string.replace("\\n", "\n")


def get_site_parameters(pathname, domain):
    cursor = g.db.cursor()

    # Define a list of pathnames in order of precedence
    pathnames = [pathname, pathname + '/*', '*']
    domains = [domain, '*']

    # Prepare the results dictionary
    results = {}

    if is_production():
        app_domain = "https://app.socrasica.com"
    else:
        app_domain = "http://localhost:3000"

    # Try to get the specific parameters for each pathname, in order of precedence
    for path in pathnames:
        for domain in domains:
            cursor.execute(
                "SELECT [key], [value] FROM [dbo].[site_parameters] WHERE [path] = %s AND [access] = 0 OR [access] = 1 AND [domain] = %s", (path, domain))

            rows = cursor.fetchall()

            # If parameters are found, add them to the results dictionary
            for row in rows:
                key = row[0]
                value = row[1]

                # if the value contains the string `[API_DOMAIN]` then replace it with the app_domain
                if "[API_DOMAIN]" in value:
                    value = value.replace("[API_DOMAIN]", app_domain)

                # Try to parse JSON string to Python object
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    # If value is not a JSON string, do nothing and keep the original value
                    pass

                # If key does not exist in results yet or if the path has higher precedence, add/update the key-value pair
                if key not in results or path == pathname:
                    results[key] = value

    return results


def get_welcome_message(name, progress):
    # only first name
    welcome_message = "Welcome back, " + name.split(" ")[0] + "!"

    message = ""

    if progress == 0:
        message = "Let’s get started with your first task 😎"
    elif progress <= 10:
        message = "You’re off to a great start! Keep it up 😎"
    elif progress <= 20:
        message = "You’re off to a great start! Keep it up 😎"
    elif progress <= 30:
        message = "Keep up the great progress 😎"
    elif progress <= 40:
        message = "Keep up the great progress 😎"
    elif progress <= 50:
        message = "You’re almost there! Keep it up 😎"
    elif progress <= 60:
        message = "You’re almost there! Keep it up 😎"
    elif progress <= 70:
        message = "You’re so close! Keep it going 😎"
    elif progress <= 80:
        message = "You’re so close! Keep it going 😎"
    elif progress <= 90:
        message = "Almost finished! 😎"
    elif progress < 100:
        message = "Almost finished! 😎"
    elif progress == 100:
        message = "Congratulations! You’ve done it! 🎉"
    # replace [TOTAL_PROGRESS] with the total progress
    # replace [MESSAGE] with the message
    sub_welcome_message = "[TOTAL_PROGRESS] - [MESSAGE]"
    sub_welcome_message = sub_welcome_message.replace(
        "[TOTAL_PROGRESS]", str(progress) + "%")
    sub_welcome_message = sub_welcome_message.replace("[MESSAGE]", message)

    return welcome_message, sub_welcome_message


def get_user_progress(user_id, type):
    cursor = g.db.cursor()

    if type == "Dashboard":
        cursor.execute(
            "SELECT [DataID], [TaskID] FROM [dbo].[tasks] WHERE [TaskFor] = 'Dashboard'")
    else:
        return False

    rows = cursor.fetchall()

    progress_data = {
        "progress": {
            "total": 0,
            "tasks": []
        }
    }

    for row in rows:
        data_id = row[0]
        task_id = row[1]

        cursor.execute(
            "SELECT [ChildTaskID], [Method] FROM [dbo].[subtasks] WHERE [ParentID] = %s", (task_id,))
        subtask_rows = cursor.fetchall()

        completed_subtasks = 0

        total_subtasks = 0

        for subtask_row in subtask_rows:
            subtask_id = subtask_row[0]

            method = subtask_row[1]

            if method == None:
                total_subtasks += len(subtask_rows)

                cursor.execute(
                    "SELECT [TaskCompleted] FROM [dbo].[user_tasks] WHERE [UserID] = %s AND [TaskID] = %s", (user_id, subtask_id))
                user_subtask_rows = cursor.fetchall()

                for user_subtask_row in user_subtask_rows:
                    completed_subtasks += user_subtask_row[0]
            else:
                # Method is an SQL query that we can execute to determine the progress
                # Example Method: EXEC StatementAnalyserProgress @UserId = '[USER_ID]';
                # In this example, we would replace [USER_ID] with the user_id

                method = method.replace("[USER_ID]", str(user_id))
                # print(method)

                cursor.execute(method, (user_id,))
                # only fetch one row which should contain `completed_tasks` and `total_tasks`
                user_subtask_rows = cursor.fetchone()

                completed_subtasks += user_subtask_rows[0]
                total_subtasks += user_subtask_rows[1]

        progress_data["progress"]["tasks"].append({
            "id": data_id,
            "task_id": task_id,
            "completed_tasks": completed_subtasks,
            "total_tasks": total_subtasks,
            "formatted": f"{completed_subtasks}/{total_subtasks}"
        })

    progress_data["progress"]["total"] = round((sum(task["completed_tasks"] for task in progress_data["progress"]["tasks"]) / sum(task["total_tasks"]
                                                                                                                                  for task in progress_data["progress"]["tasks"])) * 100) if sum(task["total_tasks"] for task in progress_data["progress"]["tasks"]) != 0 else 0

    return progress_data


def get_dashboard_items():
    cursor = g.db.cursor()

    # Fetch dashboard items from the tasks table
    cursor.execute(
        "SELECT [DataID], [TaskID], [Title], [Description], [URL], [ImageURL] FROM [dbo].[tasks] WHERE [TaskFor] = 'Dashboard'")
    rows = cursor.fetchall()

    dashboard_items = []

    # Iterate over the rows
    for row in rows:
        item = {
            "id": row[0],  # DataID
            "step": f"Step {row[0]}",  # Formatted string of DataID
            "title": row[2],  # Title
            "description": row[3],  # Description
            "href": row[4],  # URL
            "imageURL": row[5],  # ImageURL
        }
        dashboard_items.append(item)

    # Form final output
    output = {"dashboard_items": dashboard_items}
    return output


def has_referred(user_id):
    cursor = g.db.cursor()

    cursor.execute(
        "SELECT [referring_id] FROM [dbo].[referrals] WHERE [referring_id] = %s", (user_id,))
    row = cursor.fetchone()

    if row is None:
        return False
    else:
        return True


def get_bank_statement(user_id):
    cursor = g.db.cursor()
    cursor.execute(
        'SELECT statement_id, statement_text FROM statements WHERE statement_owner = %s', (user_id,))
    statement = cursor.fetchone()

    statement_id = None
    statement_text = ""

    if statement is not None:
        statement_id = statement[0]
        statement_text = statement[1]

    return statement_id, statement_text


def assign_permission(user_id, permission_to_add):
    """Assign a new permission to a user."""
    if not isinstance(permission_to_add, int):
        permission_to_add = current_app.config['REVERSE_PERMISSIONS_DICT'].get(
            permission_to_add, 0)

    cursor = g.db.cursor()
    cursor.execute(
        "SELECT [permissions] FROM [dbo].[users] WHERE [user_id] = %s", (user_id,))
    row = cursor.fetchone()
    if row is None:
        return False
    else:
        current_permissions = row[0]

    new_permission = current_permissions | permission_to_add

    cursor.execute(
        "UPDATE [dbo].[users] SET [permissions] = %s WHERE [user_id] = %s", (new_permission, user_id))
    g.db.commit()
    return True


def remove_permission(user_id, permission_to_remove):
    """Remove a permission from a user."""
    if not isinstance(permission_to_remove, int):
        permission_to_remove = current_app.config['REVERSE_PERMISSIONS_DICT'].get(
            permission_to_remove, 0)

    cursor = g.db.cursor()
    cursor.execute(
        "SELECT [permissions] FROM [dbo].[users] WHERE [user_id] = %s", (user_id,))
    row = cursor.fetchone()
    if row is None:
        return False
    else:
        current_permissions = row[0]

    new_permission = current_permissions & ~permission_to_remove

    cursor.execute(
        "UPDATE [dbo].[users] SET [permissions] = %s WHERE [user_id] = %s", (new_permission, user_id))
    g.db.commit()
    return True


def read_permissions(current_permissions):
    """Convert from denary to binary to a list of permission text."""
    permission_list = []
    for i in range(48):
        bit_value = 1 << i
        if current_permissions & bit_value:
            permission_name = current_app.config['PERMISSIONS_DICT'].get(
                bit_value, f'Unknown ({bit_value})')
            permission_list.append(permission_name)
    return permission_list


def get_user_permissions(user_id):
    """Get the permissions of a user."""
    cursor = g.db.cursor()
    cursor.execute(
        "SELECT [permissions] FROM [dbo].[users] WHERE [user_id] = %s", (user_id,))
    row = cursor.fetchone()
    if row is None:
        return [
            "none"
        ]
    else:
        return read_permissions(row[0])


def check_if_user_has_permission(user_id, permission):
    """Check if a user is a staff member."""
    cursor = g.db.cursor()
    cursor.execute(
        "SELECT [is_staff] FROM [dbo].[users] WHERE [user_id] = %s", (user_id,))
    row = cursor.fetchone()
    if row is None:
        return False
    else:
        is_staff = row[0]
        if is_staff:
            return True
        return False

