import inspect
from .common.pb2_shim import apply_patch
apply_patch()

from MetaRpcMT5 import MT5Account
from MetaRpcMT5.mt5_term_api_account_helper_pb2 import SymbolSelectRequest


def main():
    # Lists for storing async and sync methods
    async_methods = []  # To store asynchronous methods
    sync_methods = []   # To store synchronous methods

    # Loop through all members (methods) of MT5Account class
    for name, member in inspect.getmembers(MT5Account):
        if name.startswith("_"):  # Skip internal methods (starting with "_")
            continue
        if inspect.isfunction(member):  # Check if the member is a function
            # If the function is asynchronous, add it to async_methods
            if inspect.iscoroutinefunction(member):
                async_methods.append(name)
            else:
                # Otherwise, add it to sync_methods (synchronous methods)
                sync_methods.append(name)

    # Output the list of asynchronous methods
    print("=== ASYNC methods ===")
    for n in async_methods:
        print("-", n)
    
    # Output the list of synchronous methods
    print("\n=== SYNC methods ===")
    for n in sync_methods:
        print("-", n)

# Run the main function when the script is executed
if __name__ == "__main__":
    main()
