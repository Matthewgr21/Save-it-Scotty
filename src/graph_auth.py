"""
Microsoft Graph API authentication module.
Handles authentication with Azure AD for Microsoft 365 data access.
"""

import logging
from typing import Dict, Optional
from msal import ConfidentialClientApplication
from azure.identity import ClientSecretCredential

logger = logging.getLogger(__name__)


class GraphAuthenticator:
    """Handles Microsoft Graph API authentication."""

    # Required Microsoft Graph API scopes
    REQUIRED_SCOPES = [
        "https://graph.microsoft.com/.default"
    ]

    def __init__(self, config: Dict):
        """
        Initialize the Graph API authenticator.

        Args:
            config: Configuration dictionary with Azure AD settings
        """
        self.config = config
        azure_config = config.get('azure', {})

        self.tenant_id = azure_config.get('tenant_id')
        self.client_id = azure_config.get('client_id')
        self.client_secret = azure_config.get('client_secret')

        if not all([self.tenant_id, self.client_id, self.client_secret]):
            raise ValueError("Azure AD configuration missing. Check config.yaml")

        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.app = None
        self.token = None
        self.credential = None

    def authenticate(self) -> str:
        """
        Authenticate with Microsoft Graph API.

        Returns:
            Access token

        Raises:
            Exception if authentication fails
        """
        logger.info("Authenticating with Microsoft Graph API")

        try:
            # Create MSAL confidential client application
            self.app = ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=self.authority
            )

            # Acquire token for application (not user delegation)
            result = self.app.acquire_token_for_client(scopes=self.REQUIRED_SCOPES)

            if "access_token" in result:
                self.token = result['access_token']
                logger.info("Successfully authenticated with Microsoft Graph API")
                return self.token
            else:
                error = result.get('error', 'Unknown error')
                error_desc = result.get('error_description', 'No description')
                raise Exception(f"Authentication failed: {error} - {error_desc}")

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise

    def get_credential(self) -> ClientSecretCredential:
        """
        Get Azure credential object for SDK usage.

        Returns:
            ClientSecretCredential object
        """
        if not self.credential:
            self.credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )

        return self.credential

    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers with authentication token.

        Returns:
            Dictionary of HTTP headers
        """
        if not self.token:
            self.authenticate()

        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def validate_permissions(self) -> bool:
        """
        Validate that the app has required permissions.

        Returns:
            True if permissions are valid, False otherwise
        """
        # This is a placeholder - in production you'd make a test API call
        # to verify permissions are granted
        logger.info("Validating Graph API permissions")

        required_permissions = [
            "User.Read.All",
            "Files.Read.All",
            "Sites.Read.All",
            "Chat.Read.All",
            "Mail.Read"
        ]

        logger.info(f"Required permissions: {', '.join(required_permissions)}")
        logger.warning("Please ensure these permissions are granted in Azure AD and admin consent is provided")

        return True
