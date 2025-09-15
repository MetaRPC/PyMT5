import inspect
from MetaRpcMT5 import MT5Account

def main():
    async_methods = []
    sync_methods = []
    for name, member in inspect.getmembers(MT5Account):
        if name.startswith("_"):
            continue
        if inspect.isfunction(member):
            if inspect.iscoroutinefunction(member):
                async_methods.append(name)
            else:
                sync_methods.append(name)

    print("=== ASYNC methods ===")
    for n in async_methods:
        print("-", n)
    print("\n=== SYNC methods ===")
    for n in sync_methods:
        print("-", n)

if __name__ == "__main__":
    main()
