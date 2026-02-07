"""
══════════════════════════════════════════════════════════════════════════════
FILE: errors.py - MT5 Error Handling & Utilities (CENTRALIZED)
══════════════════════════════════════════════════════════════════════════════

This module provides comprehensive error handling for MT5 API operations.
Combines API error types, RetCode constants, and helper utilities.

This is the SINGLE SOURCE OF TRUTH for error handling across the entire project:
  • package/MetaRpcMT5/mt5_account.py uses these classes
  • src/pymt5/* modules import from here
  • examples/* import through error_handler.py wrapper

ERROR TYPES:
  1. NotConnectedError - Raised when calling methods before connect()
  2. ApiError - Wraps protobuf Error with convenient Python methods
  3. Trade return codes - Complete set of MQL5 RetCode constants

HELPER FUNCTIONS:
  • Fatal error handling: fatal()
  • Non-critical errors: print_if_error(), print_short_error()
  • RetCode checking: check_retcode(), is_retcode_success(), is_retcode_requote()
  • Error formatting: format_api_error()
  • User feedback: print_success(), print_warning(), print_info()

USAGE EXAMPLES:

  # 1. Critical error - raises exception
  try:
      summary = await account.account_summary()
  except ApiError as e:
      fatal(e, "Failed to get account summary")

  # 2. Non-critical error - continues execution
  try:
      margin_data = await account.symbol_info_margin_rate(req)
  except Exception as e:
      if print_if_error(e, "Margin rate not available"):
          pass  # Continue with rest of code

  # 3. Check trade return code
  result = await account.order_send(req)
  if check_retcode(result.returned_code, "Order placement"):
      print(f"Order ticket: {result.order_ticket}")

  # 4. Handle retryable errors
  if is_retcode_retryable(result.returned_code):
      await asyncio.sleep(1)
      result = await account.order_send(req)  # Retry

══════════════════════════════════════════════════════════════════════════════
"""

from typing import Optional

# Import protobuf error types from MetaRpcMT5 package
from MetaRpcMT5 import mrpc_mt5_error_pb2 as error_pb2


# ══════════════════════════════════════════════════════════════════════════════
# EXCEPTION CLASSES
# ══════════════════════════════════════════════════════════════════════════════

class NotConnectedError(Exception):
    """
    Raised when attempting to call API methods before connect().

    This replaces the old ConnectExceptionMT5 class from mt5_account.py.

    Example:
        try:
            await account.account_summary()
        except NotConnectedError:
            print("Please connect first!")
    """
    def __init__(self, message: str = "MT5Account not connected - call connect() first"):
        super().__init__(message)
        self.message = message


# ══════════════════════════════════════════════════════════════════════════════
# API ERROR - Wrapper for protobuf Error
# ══════════════════════════════════════════════════════════════════════════════

class ApiError(Exception):
    """
    Wraps protobuf Error with convenient Python methods.

    This error is raised when MT5 server responds with an error.
    This replaces the old ApiExceptionMT5 class from mt5_account.py.

    WHEN THIS ERROR OCCURS:
      - MT5 server responds with an error in the reply message
      - Trade operation fails (invalid parameters, insufficient margin, etc.)
      - MQL script execution error on the server side
      - Invalid request parameters or forbidden operations

    Example:
        try:
            result = await account.order_send(request)
        except ApiError as e:
            if e.mql_error_trade_int_code() == TRADE_RETCODE_NO_MONEY:
                print(f"Insufficient funds: {e.mql_error_trade_description()}")
            else:
                print(f"Trade error: {e}")
    """

    def __init__(self, error: error_pb2.Error):
        """
        Create ApiError from protobuf Error.

        Parameters:
            error: Protobuf Error message from MT5 server
        """
        self._error = error
        # IMPORTANT: Call super().__init__() with our clean message, not str(error)
        # This prevents protobuf dump in exception messages
        super().__init__(self._format_short())

    def __str__(self) -> str:
        """
        Return clean, user-friendly error message (ONE LINE).

        Prioritizes most specific error: Trade Error > MQL Error > API Error
        This is similar to Go's Error() method.
        """
        return self._format_short()

    def __repr__(self) -> str:
        return f"ApiError({str(self)})"

    def _format_short(self) -> str:
        """Internal: Format short error message."""
        if not self._error:
            return "Unknown API error"

        # Trade errors are the most specific and user-friendly
        if self.mql_error_trade_int_code() != 0:
            code = self.mql_error_trade_code()
            code_str = code.name if hasattr(code, 'name') else str(code)
            return f"{self.mql_error_trade_description()} ({code_str})"

        # MQL errors are more specific than generic API errors
        if self.mql_error_int_code() != 0:
            code = self.mql_error_code()
            code_str = code.name if hasattr(code, 'name') else str(code)
            return f"{self.mql_error_description()} ({code_str})"

        # Generic API error
        if self._error.error_code:
            return f"API error: {self._error.error_code}"

        return "Unknown API error"

    def detailed_string(self) -> str:
        """
        Return detailed multi-line string representation (for debugging).

        Similar to Go's String() method - use this for logging/debugging.
        For normal error messages, use str(error) instead.

        Returns:
            Multi-line formatted string with all error details
        """
        if not self._error:
            return "ApiError{None}"

        lines = []

        # Error type and code
        if self._error.error_code:
            lines.append(f"API Error: {self._error.error_code} - {self._error.error_message}")
        else:
            lines.append(f"API Error: {self._error.error_message}")

        # MQL error details
        if self.mql_error_int_code() != 0:
            lines.append(f"MQL: {self.mql_error_code().name} ({self.mql_error_int_code()}) - {self.mql_error_description()}")

        # Trade error details (most specific)
        if self.mql_error_trade_int_code() != 0:
            lines.append(f"Trade: {self.mql_error_trade_code().name} ({self.mql_error_trade_int_code()}) - {self.mql_error_trade_description()}")

        # Command info
        if self.command_type_name():
            lines.append(f"Command: {self.command_type_name()}")

        # Stack trace (if available)
        if self.stack_trace():
            lines.append(f"Stack: {self.stack_trace()}")

        return "\n".join(lines)

    # ══════════════════════════════════════════════════════════════════════════
    # API-LEVEL ERROR PROPERTIES
    # ══════════════════════════════════════════════════════════════════════════

    def error_code(self) -> str:
        """
        Return API-level error code (e.g., "INVALID_SYMBOL", "TRADE_DISABLED").

        Returns:
            Error code string or empty string if not set
        """
        return self._error.error_code if self._error else ""

    def error_message(self) -> str:
        """
        Return human-readable error description.

        Returns:
            Error message string or empty string if not set
        """
        return self._error.error_message if self._error else ""

    def error_type(self) -> error_pb2.ErrorType:
        """
        Return error type from protobuf Error.

        Returns:
            ErrorType enum value
        """
        return self._error.type if self._error else error_pb2.ErrorType.UNDEFINED

    # ══════════════════════════════════════════════════════════════════════════
    # MQL ERROR PROPERTIES
    # ══════════════════════════════════════════════════════════════════════════

    def mql_error_code(self) -> error_pb2.MqlErrorCode:
        """
        Return MQL5 error code enum.

        Returns:
            MqlErrorCode enum value
        """
        return self._error.mql_error_code if self._error else error_pb2.MqlErrorCode.ERR_SUCCESS

    def mql_error_int_code(self) -> int:
        """
        Return MQL5 error code as integer.

        Returns:
            Integer error code (0 = no error)
        """
        return self._error.mql_error_int_code if self._error else 0

    def mql_error_description(self) -> str:
        """
        Return MQL5 error description.

        Returns:
            Error description string or empty string if not set
        """
        return self._error.mql_error_description if self._error else ""

    # ══════════════════════════════════════════════════════════════════════════
    # MQL TRADE ERROR PROPERTIES (Most Specific)
    # ══════════════════════════════════════════════════════════════════════════

    def mql_error_trade_code(self) -> error_pb2.MqlErrorTradeCode:
        """
        Return MQL5 trade-specific error code enum.

        Returns:
            MqlErrorTradeCode enum value
        """
        return self._error.mql_error_trade_code if self._error else 0

    def mql_error_trade_int_code(self) -> int:
        """
        Return MQL5 trade error code as integer.

        Common values:
            10009 - TRADE_RETCODE_DONE (success)
            10013 - TRADE_RETCODE_INVALID (invalid request)
            10014 - TRADE_RETCODE_INVALID_VOLUME
            10015 - TRADE_RETCODE_INVALID_PRICE
            10016 - TRADE_RETCODE_INVALID_STOPS
            10018 - TRADE_RETCODE_MARKET_CLOSED
            10019 - TRADE_RETCODE_NO_MONEY (insufficient funds)
            10028 - TRADE_RETCODE_FROZEN (trade context busy)

        Returns:
            Integer trade error code (0 = no error, 10009 = success)
        """
        return self._error.mql_error_trade_int_code if self._error else 0

    def mql_error_trade_description(self) -> str:
        """
        Return MQL5 trade error description (most user-friendly).

        Returns:
            Trade error description or empty string if not set
        """
        return self._error.mql_error_trade_description if self._error else ""

    # ══════════════════════════════════════════════════════════════════════════
    # ADDITIONAL PROPERTIES
    # ══════════════════════════════════════════════════════════════════════════

    def command_type_name(self) -> str:
        """
        Return command type name that caused the error.

        Returns:
            Command type name or empty string if not set
        """
        return self._error.command_type_name if self._error else ""

    def stack_trace(self) -> str:
        """
        Return stack trace if available.

        Returns:
            Stack trace string or empty string if not set
        """
        return self._error.stack_trace if self._error else ""


# ══════════════════════════════════════════════════════════════════════════════
# BACKWARD COMPATIBILITY ALIASES (for old mt5_account.py code)
# ══════════════════════════════════════════════════════════════════════════════

# Old class names that mt5_account.py uses - map to new classes
ConnectExceptionMT5 = NotConnectedError
ApiExceptionMT5 = ApiError


# ══════════════════════════════════════════════════════════════════════════════
# TRADE RETURN CODE CONSTANTS - Complete MQL5 Set
# ══════════════════════════════════════════════════════════════════════════════
#
# After EVERY trading operation (OrderSend, OrderModify, etc.), you MUST check
# the returned_code field. Only 10009 (TRADE_RETCODE_DONE) means success!
#
# CRITICAL: Trading success/failure is determined by ReturnCode, NOT by exceptions!
#
# ══════════════════════════════════════════════════════════════════════════════

# ──────────────────────────────────────────────────────────────────────────────
# SUCCESS CODES
# ──────────────────────────────────────────────────────────────────────────────

TRADE_RETCODE_SUCCESS = 0           # Success (generic, rarely used - prefer DONE)
TRADE_RETCODE_DONE = 10009          # Request completed successfully
TRADE_RETCODE_DONE_PARTIAL = 10010  # Only part of the request was completed
TRADE_RETCODE_PLACED = 10008        # Order placed (pending order activated)

# ──────────────────────────────────────────────────────────────────────────────
# REQUOTE CODES (Price Changed - Retry Required)
# ──────────────────────────────────────────────────────────────────────────────

TRADE_RETCODE_REQUOTE = 10004       # Requote (price changed, need to retry)
TRADE_RETCODE_PRICE_CHANGED = 10020 # Prices changed (same as requote)

# ──────────────────────────────────────────────────────────────────────────────
# REQUEST REJECTION CODES
# ──────────────────────────────────────────────────────────────────────────────

TRADE_RETCODE_REJECT = 10006        # Request rejected by server
TRADE_RETCODE_CANCEL = 10007        # Request canceled by trader
TRADE_RETCODE_INVALID_REQUEST = 10013       # Invalid request
TRADE_RETCODE_INVALID_VOLUME = 10014        # Invalid volume in the request
TRADE_RETCODE_INVALID_PRICE = 10015         # Invalid price in the request
TRADE_RETCODE_INVALID_STOPS = 10016         # Invalid stops (SL/TP too close to price)
TRADE_RETCODE_INVALID_EXPIRATION = 10022    # Invalid order expiration date in the request
TRADE_RETCODE_INVALID_FILL = 10030          # Invalid order filling type
TRADE_RETCODE_INVALID_ORDER = 10035         # Incorrect or prohibited order type
TRADE_RETCODE_INVALID_CLOSE_VOLUME = 10038  # Invalid close volume (exceeds position volume)

# Backward compatibility aliases
TRADE_RETCODE_INVALID = TRADE_RETCODE_INVALID_REQUEST

# ──────────────────────────────────────────────────────────────────────────────
# TRADING RESTRICTION CODES
# ──────────────────────────────────────────────────────────────────────────────

TRADE_RETCODE_TRADE_DISABLED = 10017    # Trading is disabled (global setting)
TRADE_RETCODE_MARKET_CLOSED = 10018     # Market is closed
TRADE_RETCODE_SERVER_DISABLES_AT = 10026 # Autotrading disabled by server
TRADE_RETCODE_CLIENT_DISABLES_AT = 10027 # Autotrading disabled by client terminal
TRADE_RETCODE_ONLY_REAL = 10032         # Operation is allowed only for live accounts
TRADE_RETCODE_LONG_ONLY = 10042         # Only long positions allowed
TRADE_RETCODE_SHORT_ONLY = 10043        # Only short positions allowed
TRADE_RETCODE_CLOSE_ONLY = 10044        # Only position close operations allowed
TRADE_RETCODE_FIFO_CLOSE = 10045        # Position close only by FIFO rule
TRADE_RETCODE_HEDGE_PROHIBITED = 10046  # Opposite positions prohibited (hedging disabled)

# ──────────────────────────────────────────────────────────────────────────────
# RESOURCE LIMIT CODES
# ──────────────────────────────────────────────────────────────────────────────

TRADE_RETCODE_NO_MONEY = 10019          # Not enough money (insufficient margin)
TRADE_RETCODE_LIMIT_ORDERS = 10033      # Number of pending orders reached the limit
TRADE_RETCODE_LIMIT_VOLUME = 10034      # Volume of orders and positions reached the limit
TRADE_RETCODE_LIMIT_POSITIONS = 10040   # Number of open positions reached the limit

# ──────────────────────────────────────────────────────────────────────────────
# TECHNICAL ISSUE CODES (Server/Network Problems)
# ──────────────────────────────────────────────────────────────────────────────

TRADE_RETCODE_ERROR = 10011             # Request processing error
TRADE_RETCODE_TIMEOUT = 10012           # Request canceled by timeout
TRADE_RETCODE_NO_QUOTES = 10021         # No quotes to process the request
TRADE_RETCODE_TOO_MANY_REQUESTS = 10024 # Too frequent requests
TRADE_RETCODE_LOCKED = 10028            # Request locked for processing
TRADE_RETCODE_FROZEN = 10029            # Order or position frozen
TRADE_RETCODE_NO_CONNECTION = 10031     # No connection with the trade server

# Backward compatibility aliases
TRADE_RETCODE_PRICE_OFF = TRADE_RETCODE_NO_QUOTES
TRADE_RETCODE_CONNECTION = TRADE_RETCODE_NO_CONNECTION

# ──────────────────────────────────────────────────────────────────────────────
# STATE MANAGEMENT CODES
# ──────────────────────────────────────────────────────────────────────────────

TRADE_RETCODE_ORDER_CHANGED = 10023     # Order state changed during request
TRADE_RETCODE_NO_CHANGES = 10025        # No changes in request (already in target state)
TRADE_RETCODE_POSITION_CLOSED = 10036   # Position with specified ID already closed
TRADE_RETCODE_CLOSE_ORDER_EXIST = 10039 # A close order already exists for position
TRADE_RETCODE_REJECT_CANCEL = 10041     # Pending order activation rejected and canceled


# ══════════════════════════════════════════════════════════════════════════════
# RETCODE HELPER FUNCTIONS - Checking and Classification
# ══════════════════════════════════════════════════════════════════════════════

def is_retcode_success(retcode: int) -> bool:
    """
    Check if trade return code indicates success.

    Only TRADE_RETCODE_DONE (10009) is considered full success.
    For partial success, use is_retcode_partial_success().

    Parameters:
        retcode: Trade operation return code

    Returns:
        True if operation succeeded (RetCode == 10009)

    Example:
        result = await account.order_send(req)
        if is_retcode_success(result.returned_code):
            print(f"Order placed: {result.order_ticket}")
    """
    return retcode == TRADE_RETCODE_DONE


def is_retcode_partial_success(retcode: int) -> bool:
    """
    Check if trade return code indicates partial success.

    Parameters:
        retcode: Trade operation return code

    Returns:
        True if operation partially succeeded (10010)

    Example:
        if is_retcode_partial_success(retcode):
            print(f"Partially filled: {result.volume} of {requested_volume}")
    """
    return retcode == TRADE_RETCODE_DONE_PARTIAL


def is_retcode_error(retcode: int) -> bool:
    """
    Check if trade return code indicates error.

    Parameters:
        retcode: Trade operation return code

    Returns:
        True if operation failed

    Example:
        if is_retcode_error(retcode):
            print(f"Order failed: {get_retcode_message(retcode)}")
    """
    return retcode != TRADE_RETCODE_DONE and retcode != TRADE_RETCODE_DONE_PARTIAL


def is_retcode_requote(retcode: int) -> bool:
    """
    Check if the return code indicates a requote (price changed).

    When this happens, you should retry the operation with updated price.

    Parameters:
        retcode: Trade operation return code

    Returns:
        True if requote occurred (10004 or 10020)

    Example:
        if is_retcode_requote(retcode):
            # Get fresh price and retry
            tick = await account.symbol_info_tick(symbol)
            order_req.price = tick.ask
            result = await account.order_send(order_req)
    """
    return retcode in (TRADE_RETCODE_REQUOTE, TRADE_RETCODE_PRICE_CHANGED)


def is_retcode_retryable(retcode: int) -> bool:
    """
    Check if the error is retryable (temporary issue).

    These errors might succeed if you retry with exponential backoff.
    Does NOT include requotes - use is_retcode_requote() for those.

    Parameters:
        retcode: Trade operation return code

    Returns:
        True if error is temporary and worth retrying

    Example:
        if is_retcode_retryable(retcode):
            await asyncio.sleep(1)  # Wait 1 second
            result = await account.order_send(order_req)  # Retry
    """
    return retcode in (
        TRADE_RETCODE_TIMEOUT,
        TRADE_RETCODE_NO_CONNECTION,
        TRADE_RETCODE_FROZEN,
        TRADE_RETCODE_LOCKED,
        TRADE_RETCODE_TOO_MANY_REQUESTS,
        TRADE_RETCODE_NO_QUOTES,
    )


def get_retcode_message(retcode: int) -> str:
    """
    Get human-readable message for trade return code.

    Parameters:
        retcode: Trade operation return code

    Returns:
        Description of the return code

    Example:
        print(f"Order failed: {get_retcode_message(result.returned_code)}")
    """
    messages = {
        # Success codes
        TRADE_RETCODE_DONE: "Request completed successfully",
        TRADE_RETCODE_DONE_PARTIAL: "Only part of the request was completed",
        TRADE_RETCODE_PLACED: "Order placed (pending order activated)",

        # Requote codes
        TRADE_RETCODE_REQUOTE: "Requote (price changed, need to retry)",
        TRADE_RETCODE_PRICE_CHANGED: "Prices changed (requote)",

        # Request rejection codes
        TRADE_RETCODE_REJECT: "Request rejected by server",
        TRADE_RETCODE_CANCEL: "Request canceled by trader",
        TRADE_RETCODE_INVALID_REQUEST: "Invalid request",
        TRADE_RETCODE_INVALID_VOLUME: "Invalid volume in the request",
        TRADE_RETCODE_INVALID_PRICE: "Invalid price in the request",
        TRADE_RETCODE_INVALID_STOPS: "Invalid stops in the request (SL/TP too close)",
        TRADE_RETCODE_INVALID_EXPIRATION: "Invalid order expiration date in the request",
        TRADE_RETCODE_INVALID_FILL: "Invalid order filling type",
        TRADE_RETCODE_INVALID_ORDER: "Incorrect or prohibited order type",
        TRADE_RETCODE_INVALID_CLOSE_VOLUME: "Invalid close volume (exceeds position volume)",

        # Trading restriction codes
        TRADE_RETCODE_TRADE_DISABLED: "Trade is disabled",
        TRADE_RETCODE_MARKET_CLOSED: "Market is closed",
        TRADE_RETCODE_SERVER_DISABLES_AT: "Autotrading disabled by server",
        TRADE_RETCODE_CLIENT_DISABLES_AT: "Autotrading disabled by client terminal",
        TRADE_RETCODE_ONLY_REAL: "Operation is allowed only for live accounts",
        TRADE_RETCODE_LONG_ONLY: "Only long positions allowed",
        TRADE_RETCODE_SHORT_ONLY: "Only short positions allowed",
        TRADE_RETCODE_CLOSE_ONLY: "Only position close operations allowed",
        TRADE_RETCODE_FIFO_CLOSE: "Position close only by FIFO rule",
        TRADE_RETCODE_HEDGE_PROHIBITED: "Opposite positions on same symbol prohibited (hedging disabled)",

        # Resource limit codes
        TRADE_RETCODE_NO_MONEY: "Not enough money to complete the request (insufficient margin)",
        TRADE_RETCODE_LIMIT_ORDERS: "The number of pending orders has reached the limit",
        TRADE_RETCODE_LIMIT_VOLUME: "The volume of orders and positions for the symbol has reached the limit",
        TRADE_RETCODE_LIMIT_POSITIONS: "The number of open positions has reached the limit",

        # Technical issue codes
        TRADE_RETCODE_ERROR: "Request processing error",
        TRADE_RETCODE_TIMEOUT: "Request canceled by timeout",
        TRADE_RETCODE_NO_QUOTES: "No quotes to process the request",
        TRADE_RETCODE_TOO_MANY_REQUESTS: "Too frequent requests",
        TRADE_RETCODE_LOCKED: "Request locked for processing",
        TRADE_RETCODE_FROZEN: "Order or position frozen",
        TRADE_RETCODE_NO_CONNECTION: "No connection with the trade server",

        # State management codes
        TRADE_RETCODE_ORDER_CHANGED: "Order state changed",
        TRADE_RETCODE_NO_CHANGES: "No changes in request",
        TRADE_RETCODE_POSITION_CLOSED: "Position with the specified identifier already closed",
        TRADE_RETCODE_CLOSE_ORDER_EXIST: "A close order already exists for a specified position",
        TRADE_RETCODE_REJECT_CANCEL: "Pending order activation rejected and canceled",
    }

    return messages.get(retcode, f"Unknown return code: {retcode}")


# ══════════════════════════════════════════════════════════════════════════════
# ERROR HANDLING UTILITIES - For Use in Examples and Applications
# ══════════════════════════════════════════════════════════════════════════════

def fatal(error: Optional[Exception], context: str):
    """
    Print detailed error information and raise exception.
    Use this for critical errors where continuing is impossible.

    Parameters:
        error: Exception that occurred (or None to raise RuntimeError)
        context: Description of what failed

    Raises:
        The original exception or RuntimeError if error is None

    Example:
        try:
            cfg = load_settings()
        except Exception as e:
            fatal(e, "Failed to load configuration")
    """
    if error is None:
        print(f"[FAIL] FATAL: {context}")
        raise RuntimeError(context)

    # Check if this is an ApiError from MT5 server
    if isinstance(error, ApiError):
        print(f"[FAIL] FATAL: {context}")
        print(f"   Error: {error}")  # Uses __str__() - clean one-line message
        raise error

    # Regular exception
    print(f"[FAIL] FATAL: {context}")
    print(f"   Error: {error}")
    raise error


def print_if_error(error: Optional[Exception], context: str) -> bool:
    """
    Print error details and return True if error exists.
    Use this for non-critical operations where the program should continue.

    IMPROVED: Now prints clean, readable error messages instead of protobuf dumps.

    Parameters:
        error: Exception that occurred (or None)
        context: Description of what failed

    Returns:
        True if error occurred (use with if statement to skip success path)
        False if no error (continue with normal flow)

    Example:
        try:
            margin_data = await account.symbol_info_margin_rate(req)
            print(f"Rate: {margin_data.initial_margin_rate}")
        except Exception as e:
            if print_if_error(e, "Margin rate not available"):
                pass  # Continue with rest of demo
    """
    if error is None:
        return False

    # For ApiError, use the clean __str__() message
    if isinstance(error, ApiError):
        print(f"  [WARN]  {context}: {error}")  # Uses __str__() - one clean line
        return True

    # Regular exception - simple format
    print(f"  [WARN]  {context}: {error}")
    return True


def print_short_error(error: Optional[Exception], context: str) -> bool:
    """
    Print a brief error message (clean and readable).
    Use when you want minimal output without details.

    Parameters:
        error: Exception that occurred (or None)
        context: Description of what failed

    Returns:
        True if error occurred
        False if no error

    Example:
        try:
            balance = await account.account_info_double(req)
        except Exception as e:
            print_short_error(e, "Balance retrieval failed")
    """
    if error is None:
        return False

    # For both ApiError and regular exceptions, use simple format
    print(f"  [FAIL] {context}: {error}")
    return True


def format_api_error(error: ApiError) -> str:
    """
    Return a detailed multi-line string representation of ApiError.
    Use when you need full error details for logging or debugging.

    Parameters:
        error: ApiError instance

    Returns:
        Formatted error string with all available details

    Example:
        try:
            result = await account.order_send(req)
        except ApiError as e:
            print(format_api_error(e))
    """
    if error is None:
        return "ApiError{None}"

    return error.detailed_string()


def check_retcode(retcode: int, operation: str) -> bool:
    """
    Check trade operation return code and print appropriate message.

    Parameters:
        retcode: Trade return code from OrderSend/OrderCheck/etc.
        operation: Operation name for display

    Returns:
        True if operation succeeded (RetCode == 10009)
        False if operation failed

    Example:
        place_data = await account.order_send(req)
        if check_retcode(place_data.returned_code, "Order placement"):
            print(f"Order ticket: {place_data.order_ticket}")
    """
    if is_retcode_success(retcode):
        print(f"  [OK] {operation} successful (RetCode: {retcode})")
        return True

    print(f"  [FAIL] {operation} failed (RetCode: {retcode})")
    print(f"     {get_retcode_message(retcode)}")

    # Provide helpful hints for common errors
    if retcode == TRADE_RETCODE_NO_MONEY:
        print("     💡 Hint: Check account margin - insufficient funds")
    elif retcode == TRADE_RETCODE_INVALID_STOPS:
        print("     💡 Hint: SL/TP too close to market price - check SYMBOL_TRADE_STOPS_LEVEL")
    elif retcode == TRADE_RETCODE_INVALID_VOLUME:
        print("     💡 Hint: Check SYMBOL_VOLUME_MIN, SYMBOL_VOLUME_MAX, SYMBOL_VOLUME_STEP")
    elif retcode == TRADE_RETCODE_MARKET_CLOSED:
        print("     💡 Hint: Market is closed - check trading hours")
    elif retcode in (TRADE_RETCODE_REQUOTE, TRADE_RETCODE_PRICE_CHANGED):
        print("     💡 Hint: Price changed - retry with updated price")
    elif retcode == TRADE_RETCODE_TIMEOUT:
        print("     💡 Hint: Request timed out - retry with exponential backoff")
    elif retcode == TRADE_RETCODE_TOO_MANY_REQUESTS:
        print("     💡 Hint: Too many requests - add rate limiting/delays")
    elif retcode == TRADE_RETCODE_NO_CONNECTION:
        print("     💡 Hint: Connection lost - check network and reconnect")

    return False


def print_retcode_warning(retcode: int, context: str):
    """
    Print a warning for non-critical trade return codes.
    Use when operation partially succeeded or requires retry.

    Parameters:
        retcode: Trade return code
        context: Context description

    Example:
        if retcode == TRADE_RETCODE_REQUOTE:
            print_retcode_warning(retcode, "Price changed - retrying...")
    """
    print(f"  [WARN]  {context} (RetCode: {retcode})")
    print(f"     {get_retcode_message(retcode)}")


# ══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS - User Feedback
# ══════════════════════════════════════════════════════════════════════════════

def print_success(message: str, details: str = ""):
    """Print success message with checkmark."""
    if details:
        print(f"  [OK] {message}: {details}")
    else:
        print(f"  [OK] {message}")


def print_warning(message: str, details: str = ""):
    """Print warning message."""
    if details:
        print(f"  [WARN] {message}: {details}")
    else:
        print(f"  [WARN] {message}")


def print_info(message: str, details: str = ""):
    """Print info message."""
    if details:
        print(f"  [INFO] {message}: {details}")
    else:
        print(f"  [INFO] {message}")
