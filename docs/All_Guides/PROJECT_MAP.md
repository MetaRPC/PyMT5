# PyMT5 Project Map

> Complete architecture guide. Shows the three-tier system, component interactions, and file organization.

---

## 🗺️ Project Architecture Overview

PyMT5 is structured into three clean, decoupled layers designed to satisfy both low-level quantitative control and high-level strategy convenience:

```
PyMT5/
├── 📦 Layer 1: MT5Account (Low-level gRPC)
├── 🔧 Layer 2: MT5Service (Typed wrapper methods)
└── ⭐ Layer 3: MT5Sugar (High-level convenience API)
```

---

## 📊 Component Interaction Diagram

```
YOUR CODE (User-facing)
  ├─ Orchestrators (strategy implementations)
  ├─ Presets (multi-strategy combinations)
  └─ Examples (learning materials)
                  │
                  │ uses
                  ↓
MT5Sugar (Layer 3 - Convenience)
  ├─ Auto-normalization (volumes, prices)
  ├─ Risk management (CalculateVolume, BuyByRisk)
  ├─ Points-based methods (BuyLimitPoints, etc.)
  └─ Batch operations (CloseAll, CancelAll)
                  │
                  │ uses
                  ↓
MT5Service (Layer 2 - Wrappers)
  ├─ Direct data returns
  ├─ Type conversions (proto → native primitives)
  └─ Simplified signatures (no raw proto required)
                  │
                  │ uses
                  ↓
MT5Account (Layer 1 - Low-level)
  ├─ Proto Request/Response handling
  ├─ gRPC communication & channel management
  ├─ Auto-reconnection on transient faults
  └─ Real-time streaming subscriptions
                  │
                  │ gRPC
                  ↓
MT5 Gateway (mt5term) or MT5 Terminal
  └─ MetaTrader 5 with gRPC server
```

---

## 🔍 Layer Breakdown

### Layer 1: `MT5Account` (Low-Level gRPC)
- Direct gRPC stubs communicating with the terminal.
- Handles protobuf message serialization/deserialization.
- Responsible for connection recovery, channel state monitoring, and raw streaming calls.
- Ideal when you need complete control over protobuf payload fields.

### Layer 2: `MT5Service` (Wrappers)
- Translates protobuf messages into native Python primitives and data models.
- Removes boilerplate request/response wrapper instantiation.
- Simplifies method signatures for common terminal actions (Positions, Orders, and Deals).

### Layer 3: `MT5Sugar` (Convenience Layer)
- Automates lot size calculation and margin checks based on risk percentages.
- Automatically normalizes prices and volumes to broker specifications (step size, digits, minimum lot).
- Provides one-line batch operations: close all profitable positions, cancel pending orders.
- Point-offset helpers (`BuyLimitPoints`, `SellStopPoints`).

---

## 🎯 Which Layer Should You Use?

- **90% of trading applications**: Start with **`MT5Sugar`**. It protects you from off-quote rejections and invalid volume errors.
- **Custom algorithmic execution**: Use **`MT5Service`** when you manage your own volume normalization logic.
- **Protocol engineering**: Drop to **`MT5Account`** when you need raw protobuf structures.
