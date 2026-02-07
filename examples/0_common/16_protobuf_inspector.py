"""==============================================================================
FILE: examples/0_common/16_protobuf_inspector.py
      INTERACTIVE PROTOBUF TYPES INSPECTOR

PURPOSE:
  Interactive developer utility to explore MT5 protobuf types, fields,
  enums, and data structures from the MT5 gRPC API.

WHAT THIS TOOL DOES:
  - Interactive search for types, fields, and enums
  - Real-time inspection of protobuf message structures
  - Field-level discovery (find which types contain specific fields)
  - Field type discovery (find fields by their data type)
  - Enum value exploration (see all possible values)
  - Enum usage tracking (find where enums are used)
  - Type browsing with filters (list types by category)
  - JSON export (export type structures)
  - Statistics analysis (field types, enum counts, etc.)

HOW TO USE:

  1. START THE INSPECTOR:
     cd examples
     python main.py inspect

  2. AVAILABLE COMMANDS:

     COMMAND                DESCRIPTION
     -------                -----------
     list / ls              List all available protobuf types
     list --request         List only Request types
     list --reply           List only Reply types

     <TypeName>             Inspect specific type (e.g., "PositionInfo")
                            Shows all fields and their types

     search <text>          Search for types containing text
     find <text>            (e.g., "search Order" finds all Order* types)

     field <name>           Find all types containing a specific field
                            (e.g., "field Balance" -> AccountInfo)

     findtype <type>        Find all fields of a specific type
                            (e.g., "findtype double" -> all double fields)

     enum <name>            Show all values of an enum
                            (e.g., "enum AccountInfoDoublePropertyType")

     whereenum <name>       Find where enum is used
                            (e.g., "whereenum ORDER_TYPE")

     export <TypeName>      Export type structure to JSON
                            (e.g., "export PositionInfo")

     stats                  Show detailed statistics about types and fields

     help / ?               Show this help message

     exit / quit / q        Exit the inspector


PRACTICAL EXAMPLES:

  Example 1: Find out what fields PositionInfo has
  > PositionInfo
  Output:
    ticket: uint64
    type: int32
    symbol: string
    ...

  Example 2: Find which type has the "ticket" field
  > field ticket
  Output:
    Found in: PositionInfo, OrderInfo, DealInfo, ...

  Example 3: See all ORDER_TYPE enum values
  > enum ORDER_TYPE
  Output:
    ORDER_TYPE_BUY = 0
    ORDER_TYPE_SELL = 1
    ORDER_TYPE_BUY_LIMIT = 2
    ...

  Example 4: Find all types related to "Position"
  > search Position
  Output:
    PositionInfo
    PositionsGetRequest
    PositionsGetReply
    ...

  Example 5: List all available types
  > list
  Output:
    [Shows all protobuf types]

COMMON USE CASES:

  USE CASE 1: "I'm getting 'field not found' error"
  -> Use: field <fieldname>
  -> Example: field equity
  -> Result: Shows you the correct field name and which type has it

  USE CASE 2: "What fields does X have?"
  -> Use: <TypeName>
  -> Example: PositionInfo
  -> Result: Lists all fields (ticket, type, symbol, etc.)

  USE CASE 3: "What are valid enum values?"
  -> Use: enum <EnumName>
  -> Example: enum ORDER_TYPE
  -> Result: Shows all values with their numeric codes

  USE CASE 4: "I need to find types related to positions"
  -> Use: search Position
  -> Result: Lists all types with "Position" in the name

  USE CASE 5: "I want to browse what's available"
  -> Use: list
  -> Result: Shows all available types to explore

FEATURES:
  - Case-insensitive search       - "search Order" = "search order"
  - Partial field matching         - "field profit" finds profit, take_profit
  - Type categorization            - [Request], [Reply], [Data], [Info]
  - Category filtering             - list --request, list --reply, etc.
  - Field type search              - findtype double, findtype enum, etc.
  - Enum usage tracking            - whereenum shows where enum is used
  - JSON export capability         - export <TypeName> outputs JSON
  - Detailed statistics            - stats command shows comprehensive info
  - Array indicators               - [] suffix for repeated/array fields
  - Protobuf field numbers         - Shows field #N for each field
  - Smart error messages           - Suggests alternatives when type not found

USAGE:
  cd examples
  python main.py inspect

=============================================================================="""

import sys
import os
import json
from typing import Dict, List, Type, Set, Tuple
from collections import defaultdict
import inspect

# Add parent directory to path to import protobuf modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'package'))

# Import all protobuf modules
import MetaRpcMT5.mt5_term_api_account_helper_pb2 as account_helper_pb2
import MetaRpcMT5.mt5_term_api_account_information_pb2 as account_info_pb2
import MetaRpcMT5.mt5_term_api_market_info_pb2 as market_info_pb2
import MetaRpcMT5.mt5_term_api_trade_functions_pb2 as trading_pb2
import MetaRpcMT5.mt5_term_api_trading_helper_pb2 as trading_helper_pb2
import MetaRpcMT5.mt5_term_api_subscriptions_pb2 as subscriptions_pb2
import MetaRpcMT5.mt5_term_api_charts_pb2 as charts_pb2
import MetaRpcMT5.mt5_term_api_connection_pb2 as connection_pb2
from google.protobuf.message import Message
from google.protobuf.descriptor import FieldDescriptor, EnumDescriptor


class ProtobufInspector:
    """Interactive protobuf types inspector for MT5 API"""

    def __init__(self):
        self.types: Dict[str, Type[Message]] = {}
        self.enums: Dict[str, EnumDescriptor] = {}
        self.field_index: Dict[str, List[str]] = defaultdict(list)
        self.type_index: Dict[str, List[Tuple[str, str]]] = defaultdict(list)  # type -> [(msg_name, field_name)]
        self.enum_usage_index: Dict[str, List[Tuple[str, str]]] = defaultdict(list)  # enum_name -> [(msg_name, field_name)]
        self._discover_types()

    def _discover_types(self):
        """Discover all protobuf types and enums from imported modules"""
        modules = [
            account_helper_pb2,
            account_info_pb2,
            market_info_pb2,
            trading_pb2,
            trading_helper_pb2,
            subscriptions_pb2,
            charts_pb2,
            connection_pb2,
        ]

        for module in modules:
            # Find all message types
            for name in dir(module):
                obj = getattr(module, name)

                # Check if it's a protobuf message class
                if (inspect.isclass(obj) and
                    issubclass(obj, Message) and
                    obj is not Message):
                    self.types[name] = obj

                    # Index fields for quick lookup
                    try:
                        descriptor = obj.DESCRIPTOR
                        for field in descriptor.fields:
                            field_name = field.name
                            self.field_index[field_name.lower()].append(name)

                            # Index by field type
                            field_type = self._get_field_type_name(field)
                            self.type_index[field_type.lower()].append((name, field_name))

                            # Index enum usage
                            if field.type == FieldDescriptor.TYPE_ENUM and field.enum_type:
                                enum_name = field.enum_type.name
                                self.enum_usage_index[enum_name].append((name, field_name))
                    except:
                        pass

        # Discover enums
        for module in modules:
            try:
                # Get file descriptor
                if hasattr(module, 'DESCRIPTOR'):
                    file_desc = module.DESCRIPTOR
                    # Enum types at file level
                    for enum_desc in file_desc.enum_types_by_name.values():
                        self.enums[enum_desc.name] = enum_desc

                    # Enum types inside messages
                    for msg_desc in file_desc.message_types_by_name.values():
                        for enum_desc in msg_desc.enum_types:
                            self.enums[enum_desc.name] = enum_desc
            except:
                pass

    def print_header(self):
        """Print welcome header"""
        print("=" * 59)
        print("MT5 PROTOBUF TYPES INSPECTOR")
        print("=" * 59)
        print()
        print(f"  Discovered {len(self.types)} protobuf message types")
        print(f"  Discovered {len(self.enums)} enum types")
        print()
        print("  Type 'help' to see available commands")
        print("  Type 'list' to see all types")
        print("=" * 59)

    def print_help(self):
        """Print help message"""
        print()
        print("AVAILABLE COMMANDS:")
        print("-" * 59)
        print("  list / ls              - List all protobuf types")
        print("  list --request         - List only Request types")
        print("  list --reply           - List only Reply types")
        print("  <TypeName>             - Inspect a specific type")
        print("  search <text>          - Search for types by name")
        print("  find <text>            - Alias for search")
        print("  field <name>           - Find types containing a field")
        print("  findtype <type>        - Find all fields of a specific type")
        print("  enum <name>            - Show enum values")
        print("  whereenum <name>       - Find where enum is used")
        print("  export <TypeName>      - Export type to JSON")
        print("  stats                  - Show detailed statistics")
        print("  help / ?               - Show this help")
        print("  exit / quit / q        - Exit inspector")
        print()
        print("EXAMPLES:")
        print("  > PositionInfo         - Show all fields of PositionInfo")
        print("  > search Order         - Find all types with 'Order'")
        print("  > field profit         - Find types with 'profit' field")
        print("  > findtype double      - Find all double fields")
        print("  > enum ORDER_TYPE      - Show ORDER_TYPE enum values")
        print("  > whereenum ORDER_TYPE - Show where ORDER_TYPE is used")
        print("  > export PositionInfo  - Export PositionInfo to JSON")
        print("  > stats                - Show all statistics")
        print()

    def list_all_types(self, filter_arg: str = ""):
        """List all available protobuf types with optional filter"""
        print()

        # Group by category
        categories = {
            "Request": [],
            "Reply": [],
            "Data": [],
            "Info": [],
            "Other": []
        }

        for name in sorted(self.types.keys()):
            if "Request" in name:
                categories["Request"].append(name)
            elif "Reply" in name or "Response" in name:
                categories["Reply"].append(name)
            elif "Data" in name:
                categories["Data"].append(name)
            elif "Info" in name:
                categories["Info"].append(name)
            else:
                categories["Other"].append(name)

        # Apply filter
        if filter_arg == "--request":
            categories = {"Request": categories["Request"]}
            title = "REQUEST TYPES"
        elif filter_arg == "--reply":
            categories = {"Reply": categories["Reply"]}
            title = "REPLY TYPES"
        elif filter_arg == "--data":
            categories = {"Data": categories["Data"]}
            title = "DATA TYPES"
        elif filter_arg == "--info":
            categories = {"Info": categories["Info"]}
            title = "INFO TYPES"
        else:
            total = sum(len(types_list) for types_list in categories.values())
            title = f"AVAILABLE PROTOBUF TYPES ({total})"

        print(title)
        print("-" * 59)

        for category, types_list in categories.items():
            if types_list:
                print(f"\n[{category}] ({len(types_list)} types):")
                for i, type_name in enumerate(types_list, 1):
                    print(f"  {i:3}. {type_name}")

    def search_types(self, query: str):
        """Search for types by name"""
        query_lower = query.lower()
        matches = [name for name in self.types.keys()
                   if query_lower in name.lower()]

        print()
        if not matches:
            print(f"[!] No types found matching '{query}'")
            # Suggest similar
            suggestions = [name for name in self.types.keys()
                          if any(q in name.lower() for q in query_lower.split())]
            if suggestions[:5]:
                print(f"    Did you mean: {', '.join(suggestions[:5])}")
        else:
            print(f"FOUND {len(matches)} TYPES MATCHING '{query}':")
            print("-" * 59)
            for i, name in enumerate(sorted(matches), 1):
                print(f"  {i:3}. {name}")

    def find_field(self, field_name: str):
        """Find which types contain a specific field"""
        field_lower = field_name.lower()
        matches = self.field_index.get(field_lower, [])

        # Also check partial matches
        partial_matches = set()
        for indexed_field, type_list in self.field_index.items():
            if field_lower in indexed_field:
                partial_matches.update(type_list)

        print()
        if not matches and not partial_matches:
            print(f"[!] No types found with field '{field_name}'")
        else:
            if matches:
                print(f"EXACT MATCH: field '{field_name}' found in:")
                print("-" * 59)
                for i, type_name in enumerate(sorted(set(matches)), 1):
                    print(f"  {i:3}. {type_name}")

            if partial_matches - set(matches):
                print()
                print(f"PARTIAL MATCHES (field contains '{field_name}'):")
                print("-" * 59)
                for i, type_name in enumerate(sorted(partial_matches - set(matches)), 1):
                    print(f"  {i:3}. {type_name}")

    def find_by_field_type(self, field_type: str):
        """Find all fields of a specific type"""
        type_lower = field_type.lower()

        # Try exact match
        matches = self.type_index.get(type_lower, [])

        # Try partial matches
        partial_matches = []
        for indexed_type, field_list in self.type_index.items():
            if type_lower in indexed_type:
                partial_matches.extend(field_list)

        print()
        if not matches and not partial_matches:
            print(f"[!] No fields found of type '{field_type}'")
            print()
            print("Available types:")
            available_types = sorted(set(self.type_index.keys()))
            for i, t in enumerate(available_types, 1):
                print(f"  {i:3}. {t}")
        else:
            if matches:
                print(f"FIELDS OF TYPE '{field_type}' ({len(matches)} fields):")
                print("=" * 59)

                # Group by type
                by_type = defaultdict(list)
                for msg_name, field_name in matches:
                    by_type[msg_name].append(field_name)

                for msg_name in sorted(by_type.keys()):
                    fields = by_type[msg_name]
                    print(f"\n  {msg_name}:")
                    for field_name in sorted(fields):
                        print(f"    - {field_name}")

            if partial_matches and not matches:
                print(f"PARTIAL MATCHES (type contains '{field_type}'):")
                print("=" * 59)

                by_type = defaultdict(list)
                for msg_name, field_name in partial_matches:
                    by_type[msg_name].append(field_name)

                for msg_name in sorted(by_type.keys()):
                    fields = by_type[msg_name]
                    print(f"\n  {msg_name}:")
                    for field_name in sorted(fields):
                        print(f"    - {field_name}")

    def find_enum_usage(self, enum_name: str):
        """Find where a specific enum is used"""
        # Try exact match first
        matches = self.enum_usage_index.get(enum_name, [])

        # Try case-insensitive match
        if not matches:
            for name, usage_list in self.enum_usage_index.items():
                if name.lower() == enum_name.lower():
                    matches = usage_list
                    enum_name = name
                    break

        # Try partial match
        if not matches:
            partial_matches = []
            for name, usage_list in self.enum_usage_index.items():
                if enum_name.lower() in name.lower():
                    partial_matches.append((name, usage_list))

            if len(partial_matches) == 1:
                enum_name, matches = partial_matches[0]
            elif partial_matches:
                print()
                print(f"[!] Multiple enums match '{enum_name}':")
                for i, (name, _) in enumerate(sorted(partial_matches), 1):
                    print(f"  {i:3}. {name}")
                return

        print()
        if not matches:
            print(f"[!] Enum '{enum_name}' not found or not used in any fields")
            # Show available enums
            if self.enum_usage_index:
                print()
                print("Available enums (used in fields):")
                for i, name in enumerate(sorted(self.enum_usage_index.keys())[:10], 1):
                    print(f"  {i:3}. {name}")
                if len(self.enum_usage_index) > 10:
                    print(f"  ... and {len(self.enum_usage_index) - 10} more")
        else:
            print(f"ENUM '{enum_name}' USED IN ({len(matches)} fields):")
            print("=" * 59)

            # Group by type
            by_type = defaultdict(list)
            for msg_name, field_name in matches:
                by_type[msg_name].append(field_name)

            for msg_name in sorted(by_type.keys()):
                fields = by_type[msg_name]
                print(f"\n  {msg_name}:")
                for field_name in sorted(fields):
                    print(f"    - {field_name}")

    def show_stats(self):
        """Show detailed statistics"""
        print()
        print("PROTOBUF INSPECTOR STATISTICS")
        print("=" * 59)

        # Type counts by category
        categories = {
            "Request": 0,
            "Reply": 0,
            "Data": 0,
            "Info": 0,
            "Other": 0
        }

        for name in self.types.keys():
            if "Request" in name:
                categories["Request"] += 1
            elif "Reply" in name or "Response" in name:
                categories["Reply"] += 1
            elif "Data" in name:
                categories["Data"] += 1
            elif "Info" in name:
                categories["Info"] += 1
            else:
                categories["Other"] += 1

        print(f"\nMessage Types: {len(self.types)} total")
        print("-" * 59)
        for category, count in categories.items():
            if count > 0:
                print(f"  {category:15} : {count:3} types")

        # Enum statistics
        print(f"\nEnum Types: {len(self.enums)} total")
        print("-" * 59)
        total_enum_values = sum(len(enum_desc.values) for enum_desc in self.enums.values())
        print(f"  Total enum values  : {total_enum_values}")

        # Largest enums
        largest_enums = sorted(
            [(name, len(desc.values)) for name, desc in self.enums.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]

        print(f"\n  Top 5 largest enums:")
        for name, count in largest_enums:
            print(f"    {name:40} : {count:3} values")

        # Field type statistics
        print(f"\nField Types: {len(self.type_index)} distinct types")
        print("-" * 59)
        type_counts = [(t, len(fields)) for t, fields in self.type_index.items()]
        type_counts.sort(key=lambda x: x[1], reverse=True)

        print("  Top 10 most common field types:")
        for field_type, count in type_counts[:10]:
            print(f"    {field_type:20} : {count:3} fields")

        # Total fields
        total_fields = sum(len(fields) for fields in self.type_index.values())
        print(f"\nTotal Fields: {total_fields}")
        print("=" * 59)

    def export_type_to_json(self, type_name: str):
        """Export type structure to JSON"""
        # Try exact match first
        msg_class = self.types.get(type_name)

        # Try case-insensitive match
        if not msg_class:
            for name, cls in self.types.items():
                if name.lower() == type_name.lower():
                    msg_class = cls
                    type_name = name
                    break

        if not msg_class:
            print()
            print(f"[!] Type '{type_name}' not found")
            return

        descriptor = msg_class.DESCRIPTOR

        # Build JSON structure
        export_data = {
            "type_name": type_name,
            "full_name": descriptor.full_name,
            "fields": []
        }

        for field in descriptor.fields:
            field_info = {
                "number": field.number,
                "name": field.name,
                "type": self._get_field_type_name(field),
                "label": "repeated" if field.label == FieldDescriptor.LABEL_REPEATED else "optional"
            }

            # Add enum info if applicable
            if field.type == FieldDescriptor.TYPE_ENUM and field.enum_type:
                field_info["enum_name"] = field.enum_type.name
                field_info["enum_values"] = {v.name: v.number for v in field.enum_type.values}

            export_data["fields"].append(field_info)

        print()
        print(f"TYPE: {type_name} (JSON export)")
        print("=" * 59)
        print(json.dumps(export_data, indent=2))

    def inspect_enum(self, enum_name: str):
        """Show all values of an enum"""
        # Try exact match first
        enum_desc = self.enums.get(enum_name)

        # Try case-insensitive match
        if not enum_desc:
            for name, desc in self.enums.items():
                if name.lower() == enum_name.lower():
                    enum_desc = desc
                    enum_name = name
                    break

        # Try partial match
        if not enum_desc:
            matches = [name for name in self.enums.keys()
                      if enum_name.lower() in name.lower()]
            if len(matches) == 1:
                enum_name = matches[0]
                enum_desc = self.enums[enum_name]
            elif matches:
                print()
                print(f"[!] Multiple enums match '{enum_name}':")
                for i, name in enumerate(sorted(matches), 1):
                    print(f"  {i:3}. {name}")
                return

        if not enum_desc:
            print()
            print(f"[!] Enum '{enum_name}' not found")
            # Suggest similar
            suggestions = [name for name in self.enums.keys()
                          if any(q in name.lower() for q in enum_name.lower().split())]
            if suggestions[:5]:
                print(f"    Did you mean: {', '.join(suggestions[:5])}")
            return

        print()
        print(f"ENUM: {enum_name}")
        print("=" * 59)
        values = [(v.name, v.number) for v in enum_desc.values]
        for name, number in sorted(values, key=lambda x: x[1]):
            print(f"  {name:40} = {number}")

    def inspect_type(self, type_name: str):
        """Inspect a specific protobuf type and show all fields"""
        # Try exact match first
        msg_class = self.types.get(type_name)

        # Try case-insensitive match
        if not msg_class:
            for name, cls in self.types.items():
                if name.lower() == type_name.lower():
                    msg_class = cls
                    type_name = name
                    break

        # Try partial match
        if not msg_class:
            matches = [name for name in self.types.keys()
                      if type_name.lower() in name.lower()]
            if len(matches) == 1:
                type_name = matches[0]
                msg_class = self.types[type_name]
            elif matches:
                print()
                print(f"[!] Multiple types match '{type_name}':")
                for i, name in enumerate(sorted(matches), 1):
                    print(f"  {i:3}. {name}")
                return

        if not msg_class:
            print()
            print(f"[!] Type '{type_name}' not found")
            # Suggest similar
            suggestions = [name for name in self.types.keys()
                          if any(q in name.lower() for q in type_name.lower().split())]
            if suggestions[:5]:
                print(f"    Did you mean: {', '.join(suggestions[:5])}")
            return

        # Show type information
        print()
        print(f"TYPE: {type_name}")
        print("=" * 59)

        descriptor = msg_class.DESCRIPTOR
        if not descriptor.fields:
            print("  [i] No fields (empty message)")
            return

        print(f"FIELDS ({len(descriptor.fields)}):")
        print("-" * 59)

        for field in descriptor.fields:
            field_num = field.number
            field_name = field.name
            field_type = self._get_field_type_name(field)

            # Mark repeated fields
            if field.label == FieldDescriptor.LABEL_REPEATED:
                field_type += "[]"

            print(f"  #{field_num:3} {field_name:30} : {field_type}")

    def _get_field_type_name(self, field: FieldDescriptor) -> str:
        """Get human-readable field type name"""
        type_map = {
            FieldDescriptor.TYPE_DOUBLE: "double",
            FieldDescriptor.TYPE_FLOAT: "float",
            FieldDescriptor.TYPE_INT64: "int64",
            FieldDescriptor.TYPE_UINT64: "uint64",
            FieldDescriptor.TYPE_INT32: "int32",
            FieldDescriptor.TYPE_FIXED64: "fixed64",
            FieldDescriptor.TYPE_FIXED32: "fixed32",
            FieldDescriptor.TYPE_BOOL: "bool",
            FieldDescriptor.TYPE_STRING: "string",
            FieldDescriptor.TYPE_BYTES: "bytes",
            FieldDescriptor.TYPE_UINT32: "uint32",
            FieldDescriptor.TYPE_SFIXED32: "sfixed32",
            FieldDescriptor.TYPE_SFIXED64: "sfixed64",
            FieldDescriptor.TYPE_SINT32: "sint32",
            FieldDescriptor.TYPE_SINT64: "sint64",
        }

        if field.type in type_map:
            return type_map[field.type]
        elif field.type == FieldDescriptor.TYPE_MESSAGE:
            return field.message_type.name if field.message_type else "message"
        elif field.type == FieldDescriptor.TYPE_ENUM:
            return field.enum_type.name if field.enum_type else "enum"
        else:
            return "unknown"

    def run(self):
        """Main REPL loop"""
        self.print_header()

        while True:
            try:
                user_input = input("\n> ").strip()

                if not user_input:
                    continue

                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""

                if command in ("exit", "quit", "q"):
                    print("\n[+] Goodbye!")
                    break

                elif command in ("help", "?"):
                    self.print_help()

                elif command in ("list", "ls"):
                    self.list_all_types(arg)

                elif command in ("search", "find"):
                    if not arg:
                        print("[!] Usage: search <text>")
                    else:
                        self.search_types(arg)

                elif command == "field":
                    if not arg:
                        print("[!] Usage: field <fieldname>")
                    else:
                        self.find_field(arg)

                elif command == "findtype":
                    if not arg:
                        print("[!] Usage: findtype <type>")
                        print("    Examples: findtype double, findtype string, findtype enum")
                    else:
                        self.find_by_field_type(arg)

                elif command == "enum":
                    if not arg:
                        print("[!] Usage: enum <enumname>")
                    else:
                        self.inspect_enum(arg)

                elif command == "whereenum":
                    if not arg:
                        print("[!] Usage: whereenum <enumname>")
                    else:
                        self.find_enum_usage(arg)

                elif command == "export":
                    if not arg:
                        print("[!] Usage: export <TypeName>")
                    else:
                        self.export_type_to_json(arg)

                elif command == "stats":
                    self.show_stats()

                else:
                    # Assume it's a type name
                    self.inspect_type(user_input)

            except KeyboardInterrupt:
                print("\n\n[+] Interrupted. Type 'exit' to quit.")
            except EOFError:
                print("\n\n[+] Goodbye!")
                break
            except Exception as e:
                print(f"\n[X] Error: {e}")


def run_protobuf_inspector():
    """Entry point for main.py integration"""
    inspector = ProtobufInspector()
    inspector.run()


if __name__ == "__main__":
    run_protobuf_inspector()
