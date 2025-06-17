import os
import pty
import re
import shlex
import subprocess
import asyncio
import sys
import json
import base64
import hashlib
import hmac
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set
from urllib.parse import parse_qsl

import aiohttp
import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

server = Server("cli_use")

# Global session management
authenticated_sessions: Set[str] = set()

class TelegramAuthError(Exception):
    """Telegram authentication related errors"""
    pass

class SessionError(Exception):
    """Session management related errors"""
    pass

class TelegramAuthValidator:
    """Validates Telegram authentication tokens using bot token"""
    
    def __init__(self, bot_token: Optional[str] = None, coder_auth_url: Optional[str] = None):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.coder_auth_url = coder_auth_url or os.getenv("CODER_AUTH_URL", "http://localhost:1780/api/telegram/auth")
        self.allowed_users = self._parse_allowed_users(os.getenv("TELEGRAM_ALLOWED_USERS", "everyone"))
    
    def _parse_allowed_users(self, allowed_users_str: str) -> set:
        """Parse allowed users from environment variable"""
        if allowed_users_str.lower() == "everyone":
            return {"everyone"}
        
        # Parse comma-separated list of usernames
        users = set()
        for user in allowed_users_str.split(","):
            user = user.strip()
            if user:
                # Remove @ if present, normalize to lowercase
                if user.startswith("@"):
                    user = user[1:]
                users.add(user.lower())
        
        return users
    
    def _is_user_allowed(self, username: Optional[str]) -> bool:
        """Check if user is allowed to access the system"""
        if "everyone" in self.allowed_users:
            return True
        
        if not username:
            return False
        
        # Normalize username (remove @, lowercase)
        username = username.lower()
        if username.startswith("@"):
            username = username[1:]
        
        return username in self.allowed_users
        
    async def validate_with_coder_service(self, auth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate token using Coder Actor's authentication service"""
        try:
            # Encode auth data as base64 JSON (matching Coder Actor's expected format)
            auth_json = json.dumps(auth_data)
            base64_token = base64.b64encode(auth_json.encode()).decode()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.coder_auth_url,
                    json={"tgAuthResult": base64_token},
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    result = await response.json()
                    
                    if result.get("success"):
                        return result.get("user", {})
                    else:
                        raise TelegramAuthError(f"Authentication failed: {result.get('error', 'Unknown error')}")
                        
        except aiohttp.ClientError as e:
            raise TelegramAuthError(f"Failed to connect to auth service: {str(e)}")
        except Exception as e:
            raise TelegramAuthError(f"Authentication validation error: {str(e)}")
    
    def validate_hash_locally(self, auth_data: Dict[str, Any]) -> bool:
        """Validate hash using local bot token (fallback method)"""
        if not self.bot_token:
            raise TelegramAuthError("Bot token not configured for local validation")
            
        auth_hash = auth_data.pop('hash', None)
        if not auth_hash:
            raise TelegramAuthError("No hash provided in auth data")
            
        # Create data string for hash validation
        data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(auth_data.items())])
        
        # Create secret key
        secret_key = hashlib.sha256(self.bot_token.encode()).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Verify hash
        return hmac.compare_digest(calculated_hash, auth_hash)
    
    async def validate_auth_data(self, auth_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main validation method - tries Coder service first, falls back to local"""
        # Validate required fields
        required_fields = ['id', 'first_name', 'auth_date', 'hash']
        missing_fields = [field for field in required_fields if field not in auth_data]
        if missing_fields:
            raise TelegramAuthError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Check auth_date (24 hour expiry)
        auth_date = int(auth_data.get('auth_date', 0))
        current_time = int(time.time())
        if current_time - auth_date > 86400:  # 24 hours
            raise TelegramAuthError("Authentication token expired")
        
        # Check user access before validation
        username = auth_data.get('username')
        print(f"🔍 DEBUG: Checking access for user: {username}")
        print(f"🔍 DEBUG: Allowed users: {self.allowed_users}")
        
        if not self._is_user_allowed(username):
            print(f"❌ DEBUG: User {username} not in allowed list")
            raise TelegramAuthError(f"Access denied. User @{username or 'unknown'} is not authorized to access this system.")
        
        print(f"✅ DEBUG: User {username} access granted")
        
        # TEMPORARY: Skip Coder service, use local validation directly
        print(f"🔍 DEBUG: Validating auth data: {auth_data}")
        
        if self.bot_token:
            auth_data_copy = auth_data.copy()
            print(f"🔍 DEBUG: Using bot token: {self.bot_token[:10]}...")
            
            if self.validate_hash_locally(auth_data_copy):
                print(f"✅ DEBUG: Local validation SUCCESS")
                # Return user info for successful local validation
                return {
                    'id': auth_data['id'],
                    'first_name': auth_data['first_name'],
                    'last_name': auth_data.get('last_name', ''),
                    'username': auth_data.get('username', ''),
                    'auth_date': auth_data['auth_date']
                }
            else:
                print(f"❌ DEBUG: Local validation FAILED")
                raise TelegramAuthError("Invalid hash")
        else:
            print(f"❌ DEBUG: No bot token configured")
            raise TelegramAuthError("Bot token not configured for local validation")

class SessionManager:
    """Manages authenticated sessions"""
    
    @staticmethod
    def create_session_id(user_data: Dict[str, Any]) -> str:
        """Create a session ID from user data"""
        session_data = f"{user_data['id']}:{user_data['auth_date']}"
        return hashlib.sha256(session_data.encode()).hexdigest()[:16]
    
    @staticmethod
    def authenticate_session(session_id: str) -> None:
        """Mark a session as authenticated"""
        authenticated_sessions.add(session_id)
    
    @staticmethod
    def is_authenticated(session_id: str) -> bool:
        """Check if a session is authenticated"""
        return session_id in authenticated_sessions
    
    @staticmethod
    def deauthenticate_session(session_id: str) -> None:
        """Remove session authentication"""
        authenticated_sessions.discard(session_id)
    
    @staticmethod
    def get_session_id_from_request() -> Optional[str]:
        """Extract session ID from current request context"""
        # In a real implementation, this would extract from HTTP headers or connection context
        # For now, we'll use a simple approach with connection tracking
        return getattr(server, '_current_session_id', None)

def require_authentication(func):
    """Decorator to require authentication for tool calls"""
    async def wrapper(*args, **kwargs):
        # Skip authentication in test mode
        test_mode = os.getenv("TEST_MODE")
        if test_mode == "true":
            return await func(*args, **kwargs)
            
        session_id = SessionManager.get_session_id_from_request()
        if not session_id or not SessionManager.is_authenticated(session_id):
            return [types.TextContent(
                type="text", 
                text="🔒 Authentication required. Please use the telegram_auth tool first.", 
                error=True
            )]
        return await func(*args, **kwargs)
    return wrapper


class CommandError(Exception):
    """Base exception for command-related errors"""

    pass


class CommandSecurityError(CommandError):
    """Security violation errors"""

    pass


class CommandExecutionError(CommandError):
    """Command execution errors"""

    pass


class CommandTimeoutError(CommandError):
    """Command timeout errors"""

    pass


@dataclass
class SecurityConfig:
    """
    Security configuration for command execution
    """

    allowed_commands: set[str]
    allowed_flags: set[str]
    max_command_length: int
    command_timeout: int
    allow_all_commands: bool = False
    allow_all_flags: bool = False
    allow_shell_operators: bool = False


class CommandExecutor:
    def __init__(self, allowed_dir: str, security_config: SecurityConfig):
        if not allowed_dir or not os.path.exists(allowed_dir):
            raise ValueError("Valid ALLOWED_DIR is required")
        self.allowed_dir = os.path.abspath(os.path.realpath(allowed_dir))
        self.security_config = security_config
        self.shell_path = self._detect_shell()
    
    def _detect_shell(self) -> str:
        """
        Detect the available shell, preferring zsh but falling back to bash or sh.
        """
        shells = ["/bin/zsh", "/bin/bash", "/bin/sh"]
        for shell in shells:
            if os.path.exists(shell):
                return shell
        # Fallback to system shell
        return os.environ.get("SHELL", "/bin/sh")

    def _normalize_path(self, path: str) -> str:
        """
        Normalizes a path and ensures it's within allowed directory.
        """
        try:
            if os.path.isabs(path):
                # If absolute path, check directly
                real_path = os.path.abspath(os.path.realpath(path))
            else:
                # If relative path, combine with allowed_dir first
                real_path = os.path.abspath(
                    os.path.realpath(os.path.join(self.allowed_dir, path))
                )

            if not self._is_path_safe(real_path):
                raise CommandSecurityError(
                    f"Path '{path}' is outside of allowed directory: {self.allowed_dir}"
                )

            return real_path
        except CommandSecurityError:
            raise
        except Exception as e:
            raise CommandSecurityError(f"Invalid path '{path}': {str(e)}")

    def validate_command(self, command_string: str) -> tuple[str, List[str]]:
        """
        Validates and parses a command string for security and formatting.

        Checks if the command string contains shell operators. If it does, splits the command
        by operators and validates each part individually. If all parts are valid, returns
        the original command string to be executed with shell=True.

        For commands without shell operators, splits into command and arguments and validates
        each part according to security rules.

        Args:
            command_string (str): The command string to validate and parse.

        Returns:
            tuple[str, List[str]]: A tuple containing:
                - For regular commands: The command name (str) and list of arguments (List[str])
                - For commands with shell operators: The full command string and empty args list

        Raises:
            CommandSecurityError: If any part of the command fails security validation.
        """

        # Define shell operators
        shell_operators = ["&&", "||", "|", ">", ">>", "<", "<<", ";"]

        # Check if command contains shell operators
        contains_shell_operator = any(
            operator in command_string for operator in shell_operators
        )

        if contains_shell_operator:
            # Check if shell operators are allowed
            if not self.security_config.allow_shell_operators:
                # If shell operators are not allowed, raise an error
                for operator in shell_operators:
                    if operator in command_string:
                        raise CommandSecurityError(
                            f"Shell operator '{operator}' is not supported. Set ALLOW_SHELL_OPERATORS=true to enable."
                        )

            # Split the command by shell operators and validate each part
            return self._validate_command_with_operators(
                command_string, shell_operators
            )

        # Process single command without shell operators
        return self._validate_single_command(command_string)

    def _is_url_path(self, path: str) -> bool:
        """
        Checks if a given path is a URL of type http or https.

        Args:
            path (str): The path to check.

        Returns:
            bool: True if the path is a URL, False otherwise.
        """
        url_pattern = re.compile(r"^https?://")
        return bool(url_pattern.match(path))

    def _is_path_safe(self, path: str) -> bool:
        """
        Checks if a given path is safe to access within allowed directory boundaries.

        Validates that the absolute resolved path is within the allowed directory
        to prevent directory traversal attacks.

        Args:
            path (str): The path to validate.

        Returns:
            bool: True if path is within allowed directory, False otherwise.
                Returns False if path resolution fails for any reason.

        Private method intended for internal use only.
        """
        try:
            # Resolve any symlinks and get absolute path
            real_path = os.path.abspath(os.path.realpath(path))
            allowed_dir_real = os.path.abspath(os.path.realpath(self.allowed_dir))

            # Check if the path starts with allowed_dir
            return real_path.startswith(allowed_dir_real)
        except Exception:
            return False

    def _validate_single_command(self, command_string: str) -> tuple[str, List[str]]:
        """
        Validates a single command without shell operators.

        Args:
            command_string (str): The command string to validate.

        Returns:
            tuple[str, List[str]]: A tuple containing the command and validated arguments.

        Raises:
            CommandSecurityError: If the command fails validation.
        """
        try:
            parts = shlex.split(command_string)
            if not parts:
                raise CommandSecurityError("Empty command")

            command, args = parts[0], parts[1:]

            # Validate command if not in allow-all mode
            if (
                not self.security_config.allow_all_commands
                and command not in self.security_config.allowed_commands
            ):
                raise CommandSecurityError(f"Command '{command}' is not allowed")

            # Process and validate arguments
            validated_args = []
            for arg in args:
                if arg.startswith("-"):
                    if (
                        not self.security_config.allow_all_flags
                        and arg not in self.security_config.allowed_flags
                    ):
                        raise CommandSecurityError(f"Flag '{arg}' is not allowed")
                    validated_args.append(arg)
                    continue

                # For any path-like argument, validate it
                if "/" in arg or "\\" in arg or os.path.isabs(arg) or arg == ".":
                    if self._is_url_path(arg):
                        # If it's a URL, we don't need to normalize it
                        validated_args.append(arg)
                        continue

                    normalized_path = self._normalize_path(arg)
                    validated_args.append(normalized_path)
                else:
                    # For non-path arguments, add them as-is
                    validated_args.append(arg)

            return command, validated_args

        except ValueError as e:
            raise CommandSecurityError(f"Invalid command format: {str(e)}")

    def _validate_command_with_operators(
        self, command_string: str, shell_operators: List[str]
    ) -> tuple[str, List[str]]:
        """
        Validates a command string that contains shell operators.

        Splits the command string by shell operators and validates each part individually.
        If all parts are valid, returns the original command to be executed with shell=True.

        Args:
            command_string (str): The command string containing shell operators.
            shell_operators (List[str]): List of shell operators to split by.

        Returns:
            tuple[str, List[str]]: A tuple containing the command and empty args list
                                  (since the command will be executed with shell=True)

        Raises:
            CommandSecurityError: If any part of the command fails validation.
        """
        # Create a regex pattern to split by any of the shell operators
        # We need to escape special regex characters in the operators
        escaped_operators = [re.escape(op) for op in shell_operators]
        pattern = "|".join(escaped_operators)

        # Split the command string by shell operators, keeping the operators
        parts = re.split(f"({pattern})", command_string)

        # Filter out empty parts and whitespace-only parts
        parts = [part.strip() for part in parts if part.strip()]

        # Group commands and operators
        commands = []
        i = 0
        while i < len(parts):
            if i + 1 < len(parts) and parts[i + 1] in shell_operators:
                # If next part is an operator, current part is a command
                if parts[i]:  # Skip empty commands
                    commands.append(parts[i])
                i += 2  # Skip the operator
            else:
                # If no operator follows, this is the last command
                if (
                    parts[i] and parts[i] not in shell_operators
                ):  # Skip if it's an operator
                    commands.append(parts[i])
                i += 1

        # Validate each command individually
        for cmd in commands:
            try:
                # Use the extracted validation method for each command
                self._validate_single_command(cmd)
            except CommandSecurityError as e:
                raise CommandSecurityError(f"Invalid command part '{cmd}': {str(e)}")
            except ValueError as e:
                raise CommandSecurityError(
                    f"Invalid command format in '{cmd}': {str(e)}"
                )

        # If we get here, all commands passed validation
        # Return the original command string to be executed with shell=True
        return command_string, []

    def _execute_with_pty(self, command_string: str) -> subprocess.CompletedProcess:
        """
        Execute command using PTY for better terminal compatibility.
        """
        import signal
        import time
        import select
        
        # Create a result object to mimic subprocess.CompletedProcess
        class PTYResult:
            def __init__(self):
                self.stdout = ""
                self.stderr = ""
                self.returncode = 0
        
        result = PTYResult()
        shell_path = self.shell_path  # Store shell path for child process
        
        try:
            # Create PTY
            master, slave = pty.openpty()
            
            # Fork process
            pid = os.fork()
            if pid == 0:  # Child process
                os.close(master)
                os.dup2(slave, 0)  # stdin
                os.dup2(slave, 1)  # stdout
                os.dup2(slave, 2)  # stderr
                os.close(slave)
                
                # Change to allowed directory
                os.chdir(self.allowed_dir)
                
                # Execute command in shell
                shell_args = [shell_path, "-c", command_string]
                if "zsh" in shell_path:
                    shell_args = [shell_path, "-l", "-c", command_string]
                os.execve(shell_path, shell_args, os.environ)
            else:  # Parent process
                os.close(slave)
                
                # Set non-blocking on master
                import fcntl
                flags = fcntl.fcntl(master, fcntl.F_GETFL)
                fcntl.fcntl(master, fcntl.F_SETFL, flags | os.O_NONBLOCK)
                
                output = ""
                start_time = time.time()
                
                while True:
                    # Check if process is still running
                    try:
                        pid_result = os.waitpid(pid, os.WNOHANG)
                        if pid_result[0] != 0:  # Process has exited
                            result.returncode = pid_result[1]
                            break
                    except OSError:
                        break
                    
                    # Check for timeout
                    if time.time() - start_time > self.security_config.command_timeout:
                        os.kill(pid, signal.SIGTERM)
                        time.sleep(0.1)
                        try:
                            os.kill(pid, signal.SIGKILL)
                        except:
                            pass
                        raise CommandTimeoutError(f"Command timed out after {self.security_config.command_timeout} seconds")
                    
                    # Read available data
                    try:
                        ready, _, _ = select.select([master], [], [], 0.1)
                        if ready:
                            data = os.read(master, 1024).decode('utf-8', errors='ignore')
                            output += data
                    except OSError:
                        break
                
                # Read any remaining data
                try:
                    while True:
                        data = os.read(master, 1024).decode('utf-8', errors='ignore')
                        if not data:
                            break
                        output += data
                except OSError:
                    pass
                
                os.close(master)
                result.stdout = output
                
        except Exception as e:
            raise CommandExecutionError(f"PTY execution failed: {str(e)}")
        
        return result

    def execute(self, command_string: str) -> subprocess.CompletedProcess:
        """
        Executes a command string in a secure, controlled environment.

        Runs the command after validating it against security constraints including length limits
        and shell operator restrictions. Executes with controlled parameters for safety.

        Args:
            command_string (str): The command string to execute.

        Returns:
            subprocess.CompletedProcess: The result of the command execution containing
                stdout, stderr, and return code.

        Raises:
            CommandSecurityError: If the command:
                - Exceeds maximum length
                - Fails security validation
                - Fails during execution

        Notes:
            - Uses shell=True for commands with shell operators, shell=False otherwise
            - Uses timeout and working directory constraints
            - Captures both stdout and stderr
        """
        if len(command_string) > self.security_config.max_command_length:
            raise CommandSecurityError(
                f"Command exceeds maximum length of {self.security_config.max_command_length}"
            )

        try:
            command, args = self.validate_command(command_string)

            # Check if this is a command with shell operators
            shell_operators = ["&&", "||", "|", ">", ">>", "<", "<<", ";"]
            use_shell = any(operator in command_string for operator in shell_operators)

            # Double-check that shell operators are allowed if they are present
            if use_shell and not self.security_config.allow_shell_operators:
                for operator in shell_operators:
                    if operator in command_string:
                        raise CommandSecurityError(
                            f"Shell operator '{operator}' is not supported. Set ALLOW_SHELL_OPERATORS=true to enable."
                        )

            # Try PTY for claude commands to get better terminal environment
            if "claude" in command_string:
                return self._execute_with_pty(command_string)
            
            if use_shell:
                # For commands with shell operators, execute through detected shell
                shell_args = [self.shell_path, "-c", command]
                if "zsh" in self.shell_path:
                    shell_args = [self.shell_path, "-l", "-c", command]
                return subprocess.run(
                    shell_args,
                    shell=False,
                    text=True,
                    capture_output=True,
                    timeout=self.security_config.command_timeout,
                    cwd=self.allowed_dir,
                    env=os.environ,
                )
            else:
                # For regular commands, execute through detected shell
                full_command = shlex.join([command] + args)
                shell_args = [self.shell_path, "-c", full_command]
                if "zsh" in self.shell_path:
                    shell_args = [self.shell_path, "-l", "-c", full_command]
                return subprocess.run(
                    shell_args,
                    shell=False,
                    text=True,
                    capture_output=True,
                    timeout=self.security_config.command_timeout,
                    cwd=self.allowed_dir,
                    env=os.environ,
                )
        except subprocess.TimeoutExpired:
            raise CommandTimeoutError(
                f"Command timed out after {self.security_config.command_timeout} seconds"
            )
        except CommandError:
            raise
        except Exception as e:
            raise CommandExecutionError(f"Command execution failed: {str(e)}")


# Load security configuration from environment
def load_security_config() -> SecurityConfig:
    """
    Loads security configuration from environment variables with default fallbacks.

    Creates a SecurityConfig instance using environment variables to configure allowed
    commands, flags, patterns, and execution constraints. Uses predefined defaults if
    environment variables are not set.

    Returns:
        SecurityConfig: Configuration object containing:
            - allowed_commands: Set of permitted command names
            - allowed_flags: Set of permitted command flags/options
            - max_command_length: Maximum length of command string
            - command_timeout: Maximum execution time in seconds
            - allow_all_commands: Whether all commands are allowed
            - allow_all_flags: Whether all flags are allowed
            - allow_shell_operators: Whether shell operators (&&, ||, |, etc.) are allowed

    Environment Variables:
        ALLOWED_COMMANDS: Comma-separated list of allowed commands or 'all' (default: "ls,cat,pwd")
        ALLOWED_FLAGS: Comma-separated list of allowed flags or 'all' (default: "-l,-a,--help")
        MAX_COMMAND_LENGTH: Maximum command string length (default: 1024)
        COMMAND_TIMEOUT: Command timeout in seconds (default: 30)
        ALLOW_SHELL_OPERATORS: Whether to allow shell operators like &&, ||, |, >, etc. (default: false)
                              Set to "true" or "1" to enable, any other value to disable.
    """
    allowed_commands = os.getenv("ALLOWED_COMMANDS", "ls,cat,pwd")
    allowed_flags = os.getenv("ALLOWED_FLAGS", "-l,-a,--help")
    allow_shell_operators_env = os.getenv("ALLOW_SHELL_OPERATORS", "false")

    allow_all_commands = allowed_commands.lower() == "all"
    allow_all_flags = allowed_flags.lower() == "all"
    allow_shell_operators = allow_shell_operators_env.lower() in ("true", "1")

    return SecurityConfig(
        allowed_commands=(
            set() if allow_all_commands else set(allowed_commands.split(","))
        ),
        allowed_flags=set() if allow_all_flags else set(allowed_flags.split(",")),
        max_command_length=int(os.getenv("MAX_COMMAND_LENGTH", "1024")),
        command_timeout=int(os.getenv("COMMAND_TIMEOUT", "30")),
        allow_all_commands=allow_all_commands,
        allow_all_flags=allow_all_flags,
        allow_shell_operators=allow_shell_operators,
    )


executor = CommandExecutor(
    allowed_dir=os.getenv("ALLOWED_DIR", ""), security_config=load_security_config()
)

# Initialize Telegram auth validator
auth_validator = TelegramAuthValidator()


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    # In test mode, bypass authentication
    if os.getenv("TEST_MODE") == "true":
        is_authenticated = True
    else:
        session_id = SessionManager.get_session_id_from_request()
        is_authenticated = session_id and SessionManager.is_authenticated(session_id)
    
    # Always available tools
    tools = [
        types.Tool(
            name="telegram_auth",
            description=(
                "Authenticate using Telegram credentials to unlock CLI tools.\n\n"
                "Required for accessing run_command and show_security_rules tools.\n"
                "Provide Telegram authentication data with id, first_name, auth_date, and hash fields."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Telegram user ID"
                    },
                    "first_name": {
                        "type": "string", 
                        "description": "User's first name"
                    },
                    "last_name": {
                        "type": "string",
                        "description": "User's last name (optional)"
                    },
                    "username": {
                        "type": "string",
                        "description": "Telegram username (optional)"
                    },
                    "photo_url": {
                        "type": "string",
                        "description": "Profile photo URL (optional)"
                    },
                    "auth_date": {
                        "type": "string",
                        "description": "Unix timestamp of authentication"
                    },
                    "hash": {
                        "type": "string",
                        "description": "HMAC-SHA256 hash for validation"
                    }
                },
                "required": ["id", "first_name", "auth_date", "hash"]
            }
        )
    ]
    
    # Authenticated-only tools
    if is_authenticated:
        commands_desc = (
            "all commands"
            if executor.security_config.allow_all_commands
            else ", ".join(executor.security_config.allowed_commands)
        )
        flags_desc = (
            "all flags"
            if executor.security_config.allow_all_flags
            else ", ".join(executor.security_config.allowed_flags)
        )
        
        tools.extend([
            types.Tool(
                name="run_command",
                description=(
                    f"🔒 AUTHENTICATED: Allows command (CLI) execution in the directory: {executor.allowed_dir}\n\n"
                    f"Available commands: {commands_desc}\n"
                    f"Available flags: {flags_desc}\n\n"
                    f"Shell operators (&&, ||, |, >, >>, <, <<, ;) are {'supported' if executor.security_config.allow_shell_operators else 'not supported'}. Set ALLOW_SHELL_OPERATORS=true to enable."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Single command to execute (example: 'ls -l' or 'cat file.txt')",
                        }
                    },
                    "required": ["command"],
                },
            ),
            types.Tool(
                name="show_security_rules",
                description=(
                    "🔒 AUTHENTICATED: Show what commands and operations are allowed in this environment.\n"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="telegram_logout",
                description=(
                    "🔒 AUTHENTICATED: Logout and invalidate the current session.\n\n"
                    "This will deauthenticate the session and return to unauthenticated state.\n"
                    "After logout, only the telegram_auth tool will be available."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ])
    
    return tools


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Optional[Dict[str, Any]]
) -> List[types.TextContent]:
    
    if name == "telegram_auth":
        if not arguments:
            return [types.TextContent(
                type="text", 
                text="No authentication data provided", 
                error=True
            )]
        
        try:
            # Validate authentication
            user_data = await auth_validator.validate_auth_data(arguments)
            
            # Create session
            session_id = SessionManager.create_session_id(user_data)
            SessionManager.authenticate_session(session_id)
            
            # Store session in server context (simple approach for demo)
            server._current_session_id = session_id
            
            return [types.TextContent(
                type="text",
                text=f"✅ Authentication successful!\n\n"
                     f"Welcome {user_data['first_name']} {user_data.get('last_name', '')}\n"
                     f"User ID: {user_data['id']}\n"
                     f"Session ID: {session_id}\n\n"
                     f"🔓 CLI tools are now unlocked:\n"
                     f"• run_command - Execute CLI commands\n"
                     f"• show_security_rules - View security configuration"
            )]
            
        except TelegramAuthError as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Authentication failed: {str(e)}",
                error=True
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"❌ Unexpected error: {str(e)}",
                error=True
            )]
    
    # Check authentication for protected tools (skip in test mode)
    test_mode = os.getenv("TEST_MODE")
    if test_mode != "true":
        session_id = SessionManager.get_session_id_from_request()
        if not session_id or not SessionManager.is_authenticated(session_id):
            return [types.TextContent(
                type="text",
                text="🔒 Authentication required. Please use the telegram_auth tool first.",
                error=True
            )]
    
    if name == "run_command":
        if not arguments or "command" not in arguments:
            return [
                types.TextContent(type="text", text="No command provided", error=True)
            ]

        try:
            result = executor.execute(arguments["command"])

            response = []
            if result.stdout:
                response.append(types.TextContent(type="text", text=result.stdout))
            if result.stderr:
                response.append(
                    types.TextContent(type="text", text=result.stderr, error=True)
                )

            response.append(
                types.TextContent(
                    type="text",
                    text=f"\nCommand completed with return code: {result.returncode}",
                )
            )

            return response

        except CommandSecurityError as e:
            return [
                types.TextContent(
                    type="text", text=f"Security violation: {str(e)}", error=True
                )
            ]
        except subprocess.TimeoutExpired:
            return [
                types.TextContent(
                    type="text",
                    text=f"Command timed out after {executor.security_config.command_timeout} seconds",
                    error=True,
                )
            ]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}", error=True)]

    elif name == "show_security_rules":
        commands_desc = (
            "All commands allowed"
            if executor.security_config.allow_all_commands
            else ", ".join(sorted(executor.security_config.allowed_commands))
        )
        flags_desc = (
            "All flags allowed"
            if executor.security_config.allow_all_flags
            else ", ".join(sorted(executor.security_config.allowed_flags))
        )

        security_info = (
            "🔒 AUTHENTICATED Security Configuration:\n"
            f"==========================================\n"
            f"Working Directory: {executor.allowed_dir}\n"
            f"Session ID: {session_id}\n"
            f"\nAllowed Commands:\n"
            f"----------------\n"
            f"{commands_desc}\n"
            f"\nAllowed Flags:\n"
            f"-------------\n"
            f"{flags_desc}\n"
            f"\nSecurity Limits:\n"
            f"---------------\n"
            f"Max Command Length: {executor.security_config.max_command_length} characters\n"
            f"Command Timeout: {executor.security_config.command_timeout} seconds\n"
            f"Shell Operators: {'Enabled' if executor.security_config.allow_shell_operators else 'Disabled'}\n"
        )
        return [types.TextContent(type="text", text=security_info)]

    elif name == "telegram_logout":
        session_id = SessionManager.get_session_id_from_request()
        if session_id:
            SessionManager.deauthenticate_session(session_id)
            # Clear session from server context
            server._current_session_id = None
            
            return [types.TextContent(
                type="text",
                text="🔓 Logout successful!\n\n"
                     f"Session {session_id} has been invalidated.\n"
                     f"You are now in unauthenticated state.\n\n"
                     f"Available tools:\n"
                     f"• telegram_auth - Authenticate to access CLI tools\n\n"
                     f"To access protected tools again, use telegram_auth."
            )]
        else:
            return [types.TextContent(
                type="text",
                text="⚠️ No active session found to logout.",
                error=True
            )]

    raise ValueError(f"Unknown tool: {name}")


async def main():
    # Default stdio mode
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="cli_use",
                server_version="0.2.1",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
