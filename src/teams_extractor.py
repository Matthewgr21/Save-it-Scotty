"""
Microsoft Teams chat extraction module.
Extracts Teams chat messages and files via Microsoft Graph API.
"""

import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from urllib.parse import quote

logger = logging.getLogger(__name__)


class TeamsExtractor:
    """Extracts Teams chat messages and files using Microsoft Graph API."""

    GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"

    def __init__(self, authenticator, config: Dict, output_dir: Path):
        """
        Initialize the Teams extractor.

        Args:
            authenticator: GraphAuthenticator instance
            config: Configuration dictionary
            output_dir: Output directory for extracted data
        """
        self.auth = authenticator
        self.config = config
        self.output_dir = output_dir
        self.headers = None
        self.stats = {
            'chats_exported': 0,
            'messages_exported': 0,
            'files_downloaded': 0,
            'total_size': 0,
            'errors': []
        }

    def extract_all(self, user_email: str) -> Dict:
        """
        Extract all Teams chats for a user.

        Args:
            user_email: User's email address or UPN

        Returns:
            Dictionary with extraction statistics
        """
        logger.info(f"Starting Teams chat extraction for user: {user_email}")

        # Get authentication headers
        self.headers = self.auth.get_headers()

        # Create Teams output directory
        teams_output = self.output_dir / "teams_chats"
        teams_output.mkdir(parents=True, exist_ok=True)

        try:
            # Get user ID from email
            user_id = self._get_user_id(user_email)
            if not user_id:
                raise Exception(f"Could not find user: {user_email}")

            # Get all chats user is part of
            chats = self._get_user_chats(user_id)
            logger.info(f"Found {len(chats)} Teams chats")

            # Export each chat
            for i, chat in enumerate(chats, 1):
                chat_id = chat.get('id')
                if chat_id:
                    self._export_chat(user_id, chat_id, chat, teams_output, i)

            logger.info(f"Teams extraction completed. Chats exported: {self.stats['chats_exported']}, "
                       f"Messages exported: {self.stats['messages_exported']}, "
                       f"Files downloaded: {self.stats['files_downloaded']}")

        except Exception as e:
            error_msg = f"Teams extraction error: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)

        return self.stats

    def _get_user_id(self, user_email: str) -> Optional[str]:
        """
        Get user ID from email address.

        Args:
            user_email: User email address

        Returns:
            User ID or None if not found
        """
        try:
            url = f"{self.GRAPH_ENDPOINT}/users/{quote(user_email)}"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                user_data = response.json()
                return user_data.get('id')
            else:
                logger.error(f"Error getting user ID: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting user ID: {e}")
            return None

    def _get_user_chats(self, user_id: str) -> List[Dict]:
        """
        Get all chats the user is part of.

        Args:
            user_id: User ID

        Returns:
            List of chat dictionaries
        """
        chats = []

        try:
            url = f"{self.GRAPH_ENDPOINT}/users/{user_id}/chats"

            # Handle pagination
            while url:
                response = requests.get(url, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()
                    chats.extend(data.get('value', []))
                    url = data.get('@odata.nextLink')
                else:
                    logger.error(f"Error getting chats: {response.status_code} - {response.text}")
                    break

        except Exception as e:
            logger.error(f"Error getting user chats: {e}")

        return chats

    def _export_chat(self, user_id: str, chat_id: str, chat_info: Dict, output_dir: Path, chat_number: int) -> None:
        """
        Export a single chat conversation.

        Args:
            user_id: User ID
            chat_id: Chat ID
            chat_info: Chat information dictionary
            output_dir: Output directory
            chat_number: Chat number for naming
        """
        try:
            chat_type = chat_info.get('chatType', 'unknown')
            topic = chat_info.get('topic', f'Chat_{chat_number}')

            # Create safe folder name
            safe_name = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).strip()
            if not safe_name:
                safe_name = f'Chat_{chat_number}'

            chat_folder = output_dir / f"{chat_number:04d}_{safe_name}"
            chat_folder.mkdir(parents=True, exist_ok=True)

            logger.info(f"Exporting chat: {safe_name} (Type: {chat_type})")

            # Get chat members
            members = self._get_chat_members(chat_id)

            # Get all messages
            messages = self._get_chat_messages(chat_id)

            # Export chat metadata and messages to JSON
            chat_data = {
                'chat_id': chat_id,
                'chat_type': chat_type,
                'topic': topic,
                'created_datetime': chat_info.get('createdDateTime'),
                'last_updated': chat_info.get('lastUpdatedDateTime'),
                'members': members,
                'messages': messages,
                'message_count': len(messages)
            }

            # Save to JSON file
            json_path = chat_folder / 'chat_export.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, indent=2, ensure_ascii=False)

            # Create human-readable text transcript
            self._create_text_transcript(chat_data, chat_folder)

            # Download any file attachments
            self._download_chat_attachments(messages, chat_folder)

            self.stats['chats_exported'] += 1
            self.stats['messages_exported'] += len(messages)

        except Exception as e:
            error_msg = f"Error exporting chat {chat_id}: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)

    def _get_chat_members(self, chat_id: str) -> List[Dict]:
        """
        Get members of a chat.

        Args:
            chat_id: Chat ID

        Returns:
            List of member dictionaries
        """
        members = []

        try:
            url = f"{self.GRAPH_ENDPOINT}/chats/{chat_id}/members"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                members = data.get('value', [])
            else:
                logger.warning(f"Could not get chat members: {response.status_code}")

        except Exception as e:
            logger.warning(f"Error getting chat members: {e}")

        return members

    def _get_chat_messages(self, chat_id: str) -> List[Dict]:
        """
        Get all messages from a chat.

        Args:
            chat_id: Chat ID

        Returns:
            List of message dictionaries
        """
        messages = []

        try:
            url = f"{self.GRAPH_ENDPOINT}/chats/{chat_id}/messages"

            # Handle pagination
            while url:
                response = requests.get(url, headers=self.headers)

                if response.status_code == 200:
                    data = response.json()
                    messages.extend(data.get('value', []))
                    url = data.get('@odata.nextLink')
                else:
                    logger.warning(f"Error getting chat messages: {response.status_code}")
                    break

        except Exception as e:
            logger.warning(f"Error getting chat messages: {e}")

        # Sort messages by date
        messages.sort(key=lambda x: x.get('createdDateTime', ''))

        return messages

    def _create_text_transcript(self, chat_data: Dict, output_folder: Path) -> None:
        """
        Create a human-readable text transcript of the chat.

        Args:
            chat_data: Chat data dictionary
            output_folder: Output folder path
        """
        try:
            transcript_path = output_folder / 'transcript.txt'

            with open(transcript_path, 'w', encoding='utf-8') as f:
                # Header
                f.write(f"Teams Chat Transcript\n")
                f.write(f"=" * 80 + "\n\n")
                f.write(f"Chat: {chat_data.get('topic', 'Unnamed Chat')}\n")
                f.write(f"Type: {chat_data.get('chat_type', 'Unknown')}\n")
                f.write(f"Created: {chat_data.get('created_datetime', 'Unknown')}\n")
                f.write(f"Message Count: {chat_data.get('message_count', 0)}\n")
                f.write(f"\n" + "=" * 80 + "\n\n")

                # Members
                f.write("Members:\n")
                for member in chat_data.get('members', []):
                    display_name = member.get('displayName', 'Unknown')
                    email = member.get('email', '')
                    f.write(f"  - {display_name}")
                    if email:
                        f.write(f" ({email})")
                    f.write("\n")

                f.write(f"\n" + "=" * 80 + "\n\n")

                # Messages
                f.write("Messages:\n\n")
                for message in chat_data.get('messages', []):
                    timestamp = message.get('createdDateTime', 'Unknown time')
                    sender = message.get('from', {}).get('user', {}).get('displayName', 'Unknown')
                    body = message.get('body', {}).get('content', '')

                    # Strip HTML tags from body (basic)
                    import re
                    body = re.sub('<[^<]+?>', '', body)

                    f.write(f"[{timestamp}] {sender}:\n")
                    f.write(f"{body}\n")

                    # List attachments
                    attachments = message.get('attachments', [])
                    if attachments:
                        f.write("  Attachments:\n")
                        for att in attachments:
                            f.write(f"    - {att.get('name', 'Unknown')}\n")

                    f.write("\n")

        except Exception as e:
            logger.warning(f"Error creating text transcript: {e}")

    def _download_chat_attachments(self, messages: List[Dict], output_folder: Path) -> None:
        """
        Download file attachments from chat messages.

        Args:
            messages: List of message dictionaries
            output_folder: Output folder path
        """
        attachments_folder = output_folder / 'attachments'

        for message in messages:
            attachments = message.get('attachments', [])

            for attachment in attachments:
                content_url = attachment.get('contentUrl')
                file_name = attachment.get('name', 'attachment')

                if content_url and content_url.startswith('https://'):
                    if not attachments_folder.exists():
                        attachments_folder.mkdir(parents=True, exist_ok=True)

                    try:
                        self._download_attachment(content_url, file_name, attachments_folder)
                    except Exception as e:
                        logger.warning(f"Could not download attachment {file_name}: {e}")

    def _download_attachment(self, url: str, file_name: str, output_folder: Path) -> None:
        """
        Download a single attachment.

        Args:
            url: File URL
            file_name: File name
            output_folder: Output folder path
        """
        try:
            response = requests.get(url, headers=self.headers, stream=True)
            response.raise_for_status()

            dest_path = output_folder / file_name
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            file_size = dest_path.stat().st_size
            self.stats['files_downloaded'] += 1
            self.stats['total_size'] += file_size

            logger.debug(f"Downloaded attachment: {file_name}")

        except Exception as e:
            logger.warning(f"Error downloading attachment {file_name}: {e}")

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes into human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
