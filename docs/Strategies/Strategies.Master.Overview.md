# Strategies - Master Overview

> One page to **orient fast**: what orchestrators and presets are available, how to choose the right strategy, and jump links to every **strategy spec** in this docs set.

---

## ⚠️ IMPORTANT DISCLAIMER

**🎓 EDUCATIONAL & DEMONSTRATION PURPOSE ONLY**

All orchestrators and presets in this documentation are **DEMONSTRATION EXAMPLES** designed to showcase the CSharpMT5 API capabilities and serve as templates for building your own trading strategies.

**These are NOT production-ready trading systems.**

### Critical Limitations:

1. **Simplified Market Analysis**:

   - Volatility calculation uses basic formula (`spread × 10`)
   - News detection uses hardcoded UTC schedule (not real economic calendar)
   - No advanced technical indicators or ML-based analysis

2. **No Risk Management**:

   - No account balance protection
   - No drawdown limits
   - No position correlation analysis
   - No portfolio-level risk controls

3. **Basic Execution Logic**:

   - No slippage handling
   - No adverse market condition detection
   - No dynamic parameter adjustment

### ⚠️ DEMO ACCOUNTS ONLY

**NEVER use these strategies on live accounts without:**

- Complete understanding of the algorithm
- Comprehensive backtesting on historical data
- Forward testing on demo accounts for extended periods
- Proper risk management implementation
- Real-time monitoring and alerting systems
- Professional trading strategy validation

**Recommended approach:**

1. Study the code and understand every line
2. Test on demo accounts extensively
3. Modify and enhance with proper risk management
4. Build your own strategies using these as templates
5. Only after thorough validation, consider live trading with minimal capital

**By using these strategies, you acknowledge that:**

- You are fully responsible for any trading decisions
- These are educational examples, not investment advice
- Trading involves substantial risk of loss
- Past performance does not guarantee future results

---

## 🚦 Start here - Strategy Types

### Orchestrators - Single-Strategy Execution

**What**: Individual trading strategies that execute one specific algorithm.

**When to use**:

- You know exactly which strategy fits current market conditions
- Testing or optimizing a specific trading approach
- Building custom presets with specific orchestrator combinations

**Available Orchestrators**:

* **[GridTradingOrchestrator](./Orchestrators_EN/GridTradingOrchestrator.md)** - Grid trading for range-bound markets

* **[SimpleScalpingOrchestrator](./Orchestrators_EN/SimpleScalpingOrchestrator.md)** - Quick scalping trades with tight stops

* **[QuickHedgeOrchestrator](./Orchestrators_EN/QuickHedgeOrchestrator.md)** - Hedging strategy for high volatility

* **[NewsStraddleOrchestrator](./Orchestrators_EN/NewsStraddleOrchestrator.md)** - Breakout trading around news events

* **[PendingBreakoutOrchestrator](./Orchestrators_EN/PendingBreakoutOrchestrator.md)** - Pending orders for breakout trading

---

### Presets - Multi-Strategy Systems

**What**: Intelligent systems that combine multiple orchestrators with automatic strategy selection based on market analysis.

**When to use**:

- Want automated strategy selection based on market conditions

- Running strategies without constant monitoring

- Testing complex multi-strategy systems

- Production trading with adaptive behavior

**Available Presets**:

* **[AdaptiveMarketModePreset](./Presets/AdaptiveMarketModePreset.md)** - Intelligent multi-strategy system that analyzes market and selects optimal orchestrator

---

## 🧭 Quick Strategy Selector

**Range-bound / Low volatility**
→ [GridTradingOrchestrator](./Orchestrators_EN/GridTradingOrchestrator.md)
   *Captures oscillations within tight range*.

**Normal volatility / Trending**
→ [SimpleScalpingOrchestrator](./Orchestrators_EN/SimpleScalpingOrchestrator.md)
   *Quick entries/exits with tight risk control*.

**High volatility / Choppy**
→ [QuickHedgeOrchestrator](./Orchestrators_EN/QuickHedgeOrchestrator.md)
   *Hedged positions reduce directional risk*.

**News events / Economic calendar**
→ [NewsStraddleOrchestrator](./Orchestrators_EN/NewsStraddleOrchestrator.md)
   *Captures breakout in either direction*.

**Technical breakout setup**
→ [PendingBreakoutOrchestrator](./Orchestrators_EN/PendingBreakoutOrchestrator.md)
   *Pending orders at key levels*.

**Unknown / Dynamic conditions**
→ [AdaptiveMarketModePreset](./Presets/AdaptiveMarketModePreset.md)
   *Automatically selects best strategy*.

---

## 📚 Full Index · All Strategy Specs

---

## 🎯 Orchestrators

### Grid Trading

* **[GridTradingOrchestrator.md](./Orchestrators_EN/GridTradingOrchestrator.md)** - Complete specification.

* **[GridTradingOrchestrator.HOW_IT_WORKS.md](./Orchestrators_EN/GridTradingOrchestrator.HOW_IT_WORKS.md)** - Detailed algorithm explanation.

**Key Features**:

- Places Buy Limit orders below price, Sell Limit orders above
- Configurable grid levels and spacing
- Automatic TP/SL for each level
- Best for: Range-bound markets (low volatility < 15 points)

**Quick Start**:
```bash
dotnet run grid
```

**Configuration Example**:
```csharp
var orchestrator = new GridTradingOrchestrator(service)
{
    Symbol = "EURUSD",
    GridLevels = 3,              // 3 levels each direction
    GridSpacingPoints = 20,      // 20 points between levels
    VolumePerLevel = 0.01,       // 0.01 lots per level
    StopLossPoints = 50,         // 50 points SL
    TakeProfitPoints = 30,       // 30 points TP
    MaxRunMinutes = 15           // Run for 15 minutes
};
```

---

### Scalping

* **[SimpleScalpingOrchestrator.md](./Orchestrators_EN/SimpleScalpingOrchestrator.md)** - Complete specification.

* **[SimpleScalpingOrchestrator.HOW_IT_WORKS.md](./Orchestrators_EN/SimpleScalpingOrchestrator.HOW_IT_WORKS.md)** - Detailed algorithm explanation.

**Key Features**:

- Quick market entries with tight stops
- Risk-based position sizing
- Configurable hold time (seconds)
- Random or fixed direction
- Best for: Normal volatility (15-40 points)

**Quick Start**:
```bash
dotnet run scalping
```

**Configuration Example**:
```csharp
var orchestrator = new SimpleScalpingOrchestrator(service)
{
    Symbol = "EURUSD",
    RiskAmount = 20.0,           // Risk $20 per trade
    StopLossPoints = 15,         // 15 points SL
    TakeProfitPoints = 25,       // 25 points TP (R:R ≈ 1:1.67)
    MaxHoldSeconds = 60,         // Hold max 60 seconds
    IsBuy = true                 // Buy direction (or false for Sell)
};
```

---

### Hedging

* **[QuickHedgeOrchestrator.md](./Orchestrators_EN/QuickHedgeOrchestrator.md)** - Complete specification.

* **[QuickHedgeOrchestrator.HOW_IT_WORKS.md](./Orchestrators_EN/QuickHedgeOrchestrator.HOW_IT_WORKS.md)** - Detailed algorithm explanation.

**Key Features**:

- Opens hedged positions (Buy + Sell simultaneously)
- Closes losing position, keeps winner
- Reduces directional risk
- Best for: High volatility (> 40 points)

**Quick Start**:
```bash
dotnet run hedge
```

**Configuration Example**:
```csharp
var orchestrator = new QuickHedgeOrchestrator(service)
{
    Symbol = "EURUSD",
    Volume = 0.01,               // 0.01 lots per position
    StopLossPoints = 30,         // 30 points SL
    TakeProfitPoints = 50,       // 50 points TP
    MaxHoldSeconds = 120         // Hold max 2 minutes
};
```

---

### News Straddle

* **[NewsStraddleOrchestrator.md](./Orchestrators_EN/NewsStraddleOrchestrator.md)** - Complete specification.

* **[NewsStraddleOrchestrator.HOW_IT_WORKS.md](./Orchestrators_EN/NewsStraddleOrchestrator.HOW_IT_WORKS.md)** - Detailed algorithm explanation.

**Key Features**:

- Places Buy Stop above + Sell Stop below current price
- Captures breakout in either direction
- Cancels opposite order after one triggers
- Best for: News events (UTC schedule: 08:30, 12:30, 14:00, 18:00, 19:00)

**Quick Start**:
```bash
dotnet run news
```

**Configuration Example**:
```csharp
var orchestrator = new NewsStraddleOrchestrator(service)
{
    Symbol = "EURUSD",
    Volume = 0.01,               // 0.01 lots per position
    DistancePoints = 30,         // 30 points above/below price
    StopLossPoints = 20,         // 20 points SL
    TakeProfitPoints = 40,       // 40 points TP
    MaxWaitSeconds = 300         // Wait max 5 minutes
};
```

---

### Pending Breakout

* **[PendingBreakoutOrchestrator.md](./Orchestrators_EN/PendingBreakoutOrchestrator.md)** - Complete specification.

* **[PendingBreakoutOrchestrator.HOW_IT_WORKS.md](./Orchestrators_EN/PendingBreakoutOrchestrator.HOW_IT_WORKS.md)** - Detailed algorithm explanation.

**Key Features**:

- Places pending orders at technical levels
- Multiple levels with configurable spacing
- Automatic order management
- Best for: Technical breakout setups (spread > 3 points)

**Quick Start**:
```bash
dotnet run breakout
```

**Configuration Example**:
```csharp
var orchestrator = new PendingBreakoutOrchestrator(service)
{
    Symbol = "EURUSD",
    Volume = 0.01,               // 0.01 lots per order
    Levels = 3,                  // 3 pending orders
    LevelSpacingPoints = 25,     // 25 points between levels
    StopLossPoints = 40,         // 40 points SL
    TakeProfitPoints = 60,       // 60 points TP
    MaxRunMinutes = 20           // Run for 20 minutes
};
```

---

## 🎛️ Presets

### Adaptive Market Mode

* **[AdaptiveMarketModePreset.md](./Presets/AdaptiveMarketModePreset.md)** - Complete specification with decision tree.

**Key Features**:

- Analyzes market every cycle (5 minutes)
- Calculates volatility: `spread × 10` (simplified)
- Checks news schedule (hardcoded UTC times)
- Detects breakouts (spread > 3 points)
- Automatically selects and executes optimal orchestrator
- Combines ALL 5 orchestrators into one adaptive system

**Decision Tree**:
```
1. NEWS TIME? (UTC: 08:30, 12:30, 14:00, 18:00, 19:00)
   └─► YES → NewsStraddleOrchestrator (HIGHEST PRIORITY)

2. SPREAD > 3 points? (Breakout signal)
   └─► YES → PendingBreakoutOrchestrator

3. VOLATILITY < 15 points? (Range-bound)
   └─► YES → GridTradingOrchestrator

4. VOLATILITY < 40 points? (Normal)
   └─► YES → SimpleScalpingOrchestrator

5. DEFAULT (High volatility > 40 points)
   └─► QuickHedgeOrchestrator (Protection mode)
```

**Quick Start**:
```bash
dotnet run preset
```

**Configuration Example**:
```csharp
var preset = new AdaptiveMarketModePreset(service)
{
    Symbol = "EURUSD",
    BaseRiskAmount = 20.0,           // Base risk for scalping
    LowVolatilityThreshold = 15.0,   // < 15 pts = grid
    HighVolatilityThreshold = 40.0,  // > 40 pts = hedge
    EnableNewsMode = true,            // Enable news detection
    MinutesBeforeNews = 10,          // Start 10 min before news
    CycleDurationMinutes = 5,        // 5 minutes per cycle
    TotalRunMinutes = 60             // Run for 1 hour
};
```

---

## 🏗️ Architecture Overview

### Three-Layer System

```
LAYER 3: PRESETS
  Multi-strategy systems with automatic selection
  • AdaptiveMarketModePreset
    ↓
LAYER 2: ORCHESTRATORS
  Single-strategy execution engines
  • GridTrading  • Scalping  • Hedge
  • NewsStraddle • PendingBreakout
    ↓
LAYER 1: MT5 SERVICE
  Core trading API (Account, Service, Sugar)
  • MT5Account (low-level gRPC)
  • MT5Service (simplified wrappers)
  • MT5Sugar (high-level helpers)
```

---

### Common Features (All Orchestrators)

**Market Analysis**:

- Real-time volatility calculation
- Spread monitoring
- Price movement tracking
- Time-based conditions

**Risk Management**:

- Configurable stop loss (points)
- Configurable take profit (points)
- Volume/lot size control
- Risk-based position sizing (where applicable)

**Execution Control**:

- Maximum runtime limits
- Emergency stop functionality
- Position monitoring
- Automatic cleanup on exit

**Progress Reporting**:

- Console output with status updates
- Performance metrics (balance, equity, profit/loss)
- Order placement confirmations
- Error handling and logging

---

## 🔌 Usage Patterns

### Running an Orchestrator

```csharp
// 1. Create MT5 connection
var config = ConnectionHelper.BuildConfiguration();
var account = await ConnectionHelper.CreateAndConnectAccountAsync(config);
var service = new MT5Service(account);

// 2. Configure orchestrator
var orchestrator = new GridTradingOrchestrator(service)
{
    Symbol = "EURUSD",
    GridLevels = 3,
    GridSpacingPoints = 20,
    VolumePerLevel = 0.01,
    StopLossPoints = 50,
    TakeProfitPoints = 30,
    MaxRunMinutes = 15
};

// 3. Run orchestrator
await orchestrator.RunAsync();
```

---

### Running a Preset

```csharp
// 1. Create MT5 connection (same as above)
var config = ConnectionHelper.BuildConfiguration();
var account = await ConnectionHelper.CreateAndConnectAccountAsync(config);
var service = new MT5Service(account);

// 2. Configure preset
var preset = new AdaptiveMarketModePreset(service)
{
    Symbol = "EURUSD",
    BaseRiskAmount = 20.0,
    LowVolatilityThreshold = 15.0,
    HighVolatilityThreshold = 40.0,
    EnableNewsMode = true,
    CycleDurationMinutes = 5,
    TotalRunMinutes = 60
};

// 3. Run preset (will automatically select strategies)
await preset.RunAsync();
```

---

### Command-Line Shortcuts

Every orchestrator and preset has multiple command-line aliases:

```bash
# Orchestrators
dotnet run grid          # or: gridtrading, 9
dotnet run scalping      # or: scalp, 10
dotnet run hedge         # or: quickhedge, 11
dotnet run news          # or: newsstraddle, 12
dotnet run breakout      # or: pendingbreakout, 13

# Presets
dotnet run preset        # or: adaptive, adaptivemarket, 14
```

---

## 🎯 Strategy Selection Guide

### By Market Volatility

```
LOW VOLATILITY (< 15 points)
└─► GridTradingOrchestrator
    • Tight range
    • Frequent oscillations
    • Low spread

MEDIUM VOLATILITY (15-40 points)
└─► SimpleScalpingOrchestrator
    • Normal movement
    • Clear short-term trends
    • Moderate spread

HIGH VOLATILITY (> 40 points)
└─► QuickHedgeOrchestrator
    • Choppy price action
    • Wide spread
    • Uncertain direction
```

---

### By Market Event

```
NEWS EVENT (Economic Calendar)
└─► NewsStraddleOrchestrator
    • High-impact news release
    • Expected volatility spike
    • Directional breakout likely

TECHNICAL BREAKOUT (Chart Pattern)
└─► PendingBreakoutOrchestrator
    • Support/resistance level
    • Consolidation pattern
    • Pending breakout setup
```

---

### By Trading Style

```
PASSIVE / HANDS-OFF
└─► AdaptiveMarketModePreset
    • Let system choose strategy
    • Automatic market analysis
    • Multi-hour runtime

ACTIVE / MANUAL CONTROL
└─► Individual Orchestrators
    • You analyze market conditions
    • Select specific strategy
    • Shorter runtime (5-20 minutes)
```

---

## 💡 Key Concepts

### Volatility Calculation (Simplified)

All strategies use this simplified volatility metric:

```csharp
var tick = await service.SymbolInfoTickAsync(symbol);
var point = await service.GetPointAsync(symbol);
var spreadPoints = (tick.Ask - tick.Bid) / point;
var volatility = spreadPoints * 10;  // Simplified metric
```

**Real Production Note**: This is a **demonstration formula**. In real production systems, use proper volatility indicators:

- ATR (Average True Range)
- Standard deviation of price changes
- Bollinger Band width
- Historical volatility calculations

---

### News Detection (Hardcoded Schedule)

**Current Implementation**: Hardcoded UTC time schedule.
```csharp
int[] newsHours = { 8, 12, 14, 18, 19 };  // UTC hours
int[] newsMinutes = { 30 };                // xx:30
```

**Real Production Note**: This is a **demonstration approach**. In real production systems:

- Integrate with economic calendar API (e.g., Forex Factory, Investing.com)
- Parse real news events with impact levels (high/medium/low)
- Dynamic schedule updates
- Currency-specific news filtering

---

### Point-Based Calculations

All orchestrators use **points** (not pips) for distance calculations:

```csharp
// For EURUSD (5 digits):
// 1 pip = 10 points
// 20 points = 2 pips = 0.00020 price distance

// Conversion:
double priceDistance = points * symbolPoint;
double points = priceDistance / symbolPoint;
```

**Why points?** Universal across all instruments (forex, metals, indices, crypto).

---

### Risk Management

**Position Sizing Options**:

1. **Fixed Volume**: `VolumePerLevel = 0.01` (Grid, Hedge, News)

2. **Risk-Based**: `RiskAmount = 20.0` (Scalping) - calculates volume based on SL distance

**Stop Loss / Take Profit**:

- Always specified in **points**
- Automatically normalized to symbol precision
- Applied to every order/position

**Maximum Runtime**:

- `MaxRunMinutes` - hard limit on execution time
- Prevents runaway strategies
- Automatic cleanup on timeout

---

## ⚠️ Important Notes

### Trading Environment

* **Demo account first**: Always test on demo before live trading

* **Network stability**: gRPC connection required throughout runtime

* **Broker compatibility**: Some features may not be available on all brokers

* **Hedging support**: QuickHedgeOrchestrator requires hedging-enabled account

---

### Execution Safety

* **Emergency stop**: Press `Ctrl+C` to stop any strategy immediately

* **Position cleanup**: All orchestrators close positions on exit

* **Order cancellation**: Pending orders are cancelled on exit

* **Error handling**: Connection errors trigger retry logic (3 attempts with exponential backoff)

---

### Performance Considerations

* **Retry logic**: Built-in retry with exponential backoff (1s → 2s → 4s)

* **Rate limiting**: 3-second delay between order placements

* **Connection pooling**: Single gRPC connection shared across operations

* **Progress bars**: Visual feedback for long-running operations

---

## 📋 Best Practices

### 1. Strategy Selection

```csharp
// ❌ BAD: Running grid strategy in high volatility
var grid = new GridTradingOrchestrator(service)
{
    GridLevels = 5,  // Will hit all SL levels quickly!
    // ...
};

// ✅ GOOD: Use preset for automatic selection
var preset = new AdaptiveMarketModePreset(service)
{
    Symbol = "EURUSD",
    // Preset will detect high volatility and switch to hedge
};
```

---

### 2. Risk Configuration

```csharp
// ❌ BAD: Excessive risk per trade
var scalping = new SimpleScalpingOrchestrator(service)
{
    RiskAmount = 500.0,  // Too high for demo account!
    StopLossPoints = 10,  // Very tight SL
};

// ✅ GOOD: Conservative risk settings
var scalping = new SimpleScalpingOrchestrator(service)
{
    RiskAmount = 20.0,   // 1-2% of typical demo balance
    StopLossPoints = 15, // Reasonable SL distance
};
```

---

### 3. Runtime Limits

```csharp
// ❌ BAD: No runtime limit
var orchestrator = new GridTradingOrchestrator(service)
{
    MaxRunMinutes = 999999,  // Runs indefinitely!
};

// ✅ GOOD: Reasonable runtime with monitoring
var orchestrator = new GridTradingOrchestrator(service)
{
    MaxRunMinutes = 15,  // Clear exit condition
};
```

---

### 4. Error Handling

```csharp
try
{
    await orchestrator.RunAsync();
}
catch (OperationCanceledException)
{
    Console.WriteLine("Strategy stopped by user (Ctrl+C)");
}
catch (Exception ex)
{
    Console.WriteLine($"Strategy error: {ex.Message}");
    // Cleanup positions/orders here if needed
}
```

---

## 🎓 Learning Path

### Beginner Path

```
1. Start with: GridTradingOrchestrator
   • Simplest to understand
   • Visual grid concept
   • Clear entry/exit rules

2. Study: Program.cs routing logic
   • How commands map to orchestrators
   • Configuration patterns

3. Read: GridTradingOrchestrator.HOW_IT_WORKS.md
   • Understand algorithm step-by-step
   • Learn MT5Sugar methods used

4. Experiment: Modify grid parameters
   • Change GridLevels
   • Adjust GridSpacingPoints
   • Test on demo account
```

---

### Intermediate Path

```
1. Compare: All 5 orchestrators side-by-side
   • Identify common patterns (MT5Service usage)
   • See differences in algorithms
   • Understand when to use each

2. Study: AdaptiveMarketModePreset
   • How it analyzes market conditions
   • Decision tree logic
   • Orchestrator instantiation

3. Modify: Add custom orchestrator
   • Copy existing orchestrator as template
   • Implement your algorithm
   • Add to Program.cs routing

4. Test: Run preset for extended period
   • Observe strategy switching
   • Analyze performance across conditions
```

---

### Advanced Path

```
1. Enhance: Market analysis algorithms
   • Replace simplified volatility with ATR
   • Integrate real economic calendar API
   • Add ML-based condition detection

2. Build: Custom preset with your logic
   • Define your market conditions
   • Create decision tree
   • Combine orchestrators your way

3. Optimize: Parameters via backtesting
   • Historical data analysis
   • Parameter sensitivity testing
   • Walk-forward optimization

4. Production: Deploy with monitoring
   • Add logging and metrics
   • Implement alerting
   • Set up performance tracking
```

---

## 📖 Related Documentation

* **[MT5Account - Master Overview](../API_Reference/MT5Account.md)** - Low-level gRPC API reference.

* **[MT5Service Documentation](../API_Reference/MT5Service.md)** - Simplified wrapper methods.

* **[MT5Sugar Documentation](../API_Reference/MT5Sugar.md)** - High-level convenience API.

* **[GRPC_STREAM_MANAGEMENT.md](../All_Guides/GRPC_STREAM_MANAGEMENT.md)** - Streaming subscriptions guide.

* **[Sync_vs_Async.md](../All_Guides/SYNC_VS_ASYNC.md)** - Async/sync patterns explained.

* **[UserCode_Sandbox_Guide.md](../All_Guides/USERCODE_SANDBOX_GUIDE.md)** - How to write custom strategies.

---

## 🎯 Quick Jump - All Files

### Orchestrators

* [GridTradingOrchestrator.md](./Orchestrators_EN/GridTradingOrchestrator.md)
* [GridTradingOrchestrator.HOW_IT_WORKS.md](./Orchestrators_EN/GridTradingOrchestrator.HOW_IT_WORKS.md)
* [SimpleScalpingOrchestrator.md](./Orchestrators_EN/SimpleScalpingOrchestrator.md)
* [SimpleScalpingOrchestrator.HOW_IT_WORKS.md](./Orchestrators_EN/SimpleScalpingOrchestrator.HOW_IT_WORKS.md)
* [QuickHedgeOrchestrator.md](./Orchestrators_EN/QuickHedgeOrchestrator.md)
* [QuickHedgeOrchestrator.HOW_IT_WORKS.md](./Orchestrators_EN/QuickHedgeOrchestrator.HOW_IT_WORKS.md)
* [NewsStraddleOrchestrator.md](./Orchestrators_EN/NewsStraddleOrchestrator.md)
* [NewsStraddleOrchestrator.HOW_IT_WORKS.md](./Orchestrators_EN/NewsStraddleOrchestrator.HOW_IT_WORKS.md)
* [PendingBreakoutOrchestrator.md](./Orchestrators_EN/PendingBreakoutOrchestrator.md)
* [PendingBreakoutOrchestrator.HOW_IT_WORKS.md](./Orchestrators_EN/PendingBreakoutOrchestrator.HOW_IT_WORKS.md)

### Presets

* [AdaptiveMarketModePreset.md](./Presets/AdaptiveMarketModePreset.md)

---

"Trade smart, code clean, and may your orchestrators always close positions profitably."
