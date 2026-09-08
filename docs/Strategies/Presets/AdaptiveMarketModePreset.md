# AdaptiveMarketModePreset - Intelligent Multi-Strategy System

## Description

**AdaptiveMarketModePreset** is an intelligent trading system that automatically selects and executes the most appropriate orchestrator based on real-time market condition analysis. It combines ALL 5 orchestrators into one adaptive system that switches strategies dynamically every cycle.

**Principle**: "The right strategy for the right conditions" - the preset analyzes current market volatility, time, spread, and news schedule, then selects the optimal orchestrator (Grid, Scalping, Hedge, News Straddle, or Breakout) and executes it with preset-optimized parameters.

**File**: `Examples\Presets\AdaptiveMarketModePreset.cs`

---

## Architecture

```
ADAPTIVE MARKET MODE PRESET
    ↓
Market Analysis Engine
  • Volatility (spread×10)
  • Time-based news check
  • Breakout detection
    ↓
  ┌─────────┼─────────┐
  ↓         ↓         ↓
Low Vol   Medium    High Vol
(<15 pts) (15-40)   (>40 pts)
  ↓         ↓         ↓
Grid      Scalping   Hedge
Trading   Orchestr.  Orchestr.
Orchestr.
          ↓
    ┌─────┼─────┐
    ↓           ↓
  News        Spread>3
  Time        (Breakout)
    ↓           ↓
  News        Pending
  Straddle    Breakout
  Orchestr.   Orchestr.
```

### Dependencies

**MT5Service**: Service layer for MT5

- **All 5 Orchestrators**:
  - GridTradingOrchestrator
  - SimpleScalpingOrchestrator
  - QuickHedgeOrchestrator
  - NewsStraddleOrchestrator
  - PendingBreakoutOrchestrator
- **mt5_term_api**: gRPC types

---

## Market Conditions & Orchestrator Selection

### 📊 CONDITION 1: LOW VOLATILITY (< 15 points)

**Selected Orchestrator**: [GridTradingOrchestrator](../Orchestrators_EN/GridTradingOrchestrator.md)

**Why**: Range-bound markets are perfect for grid strategies. When price moves in a narrow range, grid levels capture small movements in both directions.

**Parameters**:
```csharp
GridLevels = 3              // Fewer levels for safety
GridSpacingPoints = 20      // 20 points between levels
VolumePerLevel = 0.01       // 0.01 lots per level
StopLossPoints = 30         // 30 points SL
TakeProfitPoints = 50       // 50 points TP
MaxRunMinutes = 5           // Run for 5 minutes
```

---

### 📊 CONDITION 2: MEDIUM VOLATILITY (15-40 points)

**Selected Orchestrator**: [SimpleScalpingOrchestrator](../Orchestrators_EN/SimpleScalpingOrchestrator.md)

**Why**: Normal market conditions suit quick scalping trades with tight stops and risk-based position sizing.

**Parameters**:
```csharp
RiskAmount = BaseRiskAmount  // Uses preset's base risk ($20)
StopLossPoints = 15          // 15 points SL
TakeProfitPoints = 25        // 25 points TP (R:R ≈ 1:1.67)
IsBuy = Random               // Randomly selected direction
MaxHoldSeconds = 60          // Hold maximum 60 seconds
```

---

### 📊 CONDITION 3: HIGH VOLATILITY (> 40 points)

**Selected Orchestrator**: [QuickHedgeOrchestrator](../Orchestrators_EN/QuickHedgeOrchestrator.md)

**Why**: Volatile markets need hedging protection. Opens position, then hedges if price moves adversely, limiting downside risk.

**Parameters**:
```csharp
RiskAmount = BaseRiskAmount × 0.7  // REDUCED RISK (70%)
StopLossPoints = 25                // 25 points SL
TakeProfitPoints = 40              // 40 points TP
HedgeTriggerPoints = 15            // Hedge after 15 points adverse move
OpenBuyFirst = Random              // Randomly selected direction
```

**Key Feature**: Risk is reduced to 70% of base amount in high volatility for capital preservation.

---

### 📊 CONDITION 4: NEWS EVENT DETECTED

**Selected Orchestrator**: [NewsStraddleOrchestrator](../Orchestrators_EN/NewsStraddleOrchestrator.md)

**Why**: Capture explosive volatility from high-impact news releases with symmetrical pending orders.

**News Schedule (UTC)**:

- 08:30 - Economic data releases (NFP, CPI, Retail Sales)
- 12:30 - Midday economic reports
- 14:00 - FOMC statements, GDP releases
- 18:00 - ECB announcements
- 19:00 - Evening economic data

**Detection**: Preset checks if current time is within 5 minutes before any scheduled news event.

**Parameters**:
```csharp
StraddleDistancePoints = 15     // 15 points from current price
Volume = 0.02                    // 0.02 lots (fixed)
StopLossPoints = 20              // 20 points SL
TakeProfitPoints = 40            // 40 points TP
SecondsBeforeNews = 30           // 30 sec countdown (shortened for demo)
MaxWaitAfterNewsSeconds = 120    // Wait 2 minutes for breakout
```

---

### 📊 CONDITION 5: BREAKOUT SIGNAL (Spread > 3 points)

**Selected Orchestrator**: [PendingBreakoutOrchestrator](../Orchestrators_EN/PendingBreakoutOrchestrator.md)

**Why**: Large spread indicates potential breakout movement. Places BUY STOP above and SELL STOP below to catch momentum.

**Detection**: Current spread exceeds 3.0 points (unusual width suggests imminent volatility).

**Parameters**:
```csharp
BreakoutDistancePoints = 20  // 20 points from current price
Volume = 0.01                 // 0.01 lots (fixed)
StopLossPoints = 20           // 20 points SL
TakeProfitPoints = 40         // 40 points TP
MaxWaitMinutes = 3            // Wait 3 minutes for breakout
```

---

## Configuration Parameters

| Parameter | Type | Default | Description |
|----------|-----|--------------|----------|
| `Symbol` | string | `"EURUSD"` | Trading instrument |
| `BaseRiskAmount` | double | `20.0` | Base risk per trade in dollars |
| `LowVolatilityThreshold` | double | `15.0` | Max volatility for grid mode (points) |
| `HighVolatilityThreshold` | double | `40.0` | Min volatility for hedge mode (points) |
| `EnableNewsMode` | bool | `true` | Enable news event detection |
| `MinutesBeforeNews` | int | `5` | Switch to news mode N minutes early |

### Configuration Example

```csharp
var preset = new AdaptiveMarketModePreset(service)
{
    Symbol = "GBPUSD",
    BaseRiskAmount = 50.0,          // Higher risk for larger account
    LowVolatilityThreshold = 20.0,  // More opportunities for grid
    HighVolatilityThreshold = 30.0, // Trigger hedge earlier
    EnableNewsMode = true
};
```

---

## How to Run

You can execute this preset using several command variations:

```bash
# Option 1: By number
dotnet run 14

# Option 2: By short name
dotnet run adaptive

# Option 3: By full name
dotnet run preset
```

All three commands will launch the **AdaptiveMarketModePreset** with the default configuration or the settings you specify in the code.

---

## Algorithm

### Main Cycle Flowchart

```
START PRESET
  ↓
Initialize (get starting balance, maxCycles=100)
  ↓
┌──── CYCLE LOOP (repeat up to maxCycles) 
│                                             
│ STEP 1: Analyze Market Conditions           
│   → Get current tick (bid/ask/spread)       
│   → Calculate volatility (spread × 10)      
│   → Check UTC time for news                 
│   → Check spread for breakout signal        
│   → Determine MarketCondition enum          
│                                             
│ STEP 2: Select Orchestrator                 
│   → News mode? → NewsStraddleOrchestrator   
│   → Breakout? → PendingBreakoutOrchestrator 
│   → Low vol? → GridTradingOrchestrator      
│   → Med vol? → SimpleScalpingOrchestrator   
│   → High vol? → QuickHedgeOrchestrator      
│                                             
│ STEP 3: Execute Selected Orchestrator       
│   → await selectedOrchestrator.ExecuteAsync()
│                                             
│ STEP 4: Track Results                       
│   → Add cycle P/L to totalProfit            
│   → Increment cyclesRun counter             
│   → Display cycle summary                   
│                                             
│ STEP 5: Safety Check                        
│   → If totalProfit < -BaseRiskAmount × 5    
│   → STOP (max loss exceeded)                
│                                             
│ STEP 6: Pause Between Cycles                
│   → Wait 30 seconds (prevent overtrading)   
│                                             
│ If cyclesRun < maxCycles → Loop back        
└─────────────────────────────────────────────
  ↓
Display Final Results & Exit
END PRESET
```

### Market Analysis Algorithm

```csharp
private async Task<MarketCondition> AnalyzeMarketConditions()
{
    // STEP 1: Get current market data
    var tick = await _service.SymbolInfoTickAsync(Symbol);
    var point = await _service.GetPointAsync(Symbol);

    // STEP 2: Calculate spread in points
    var spreadPoints = (tick.Ask - tick.Bid) / point;

    // STEP 3: Estimate volatility (simplified demo formula)
    var avgRangePoints = spreadPoints * 10;  // ⚠️ Production: use ATR

    // STEP 4: Priority 1 - Check news time
    if (EnableNewsMode && IsNewsTime())
        return MarketCondition.News;

    // STEP 5: Priority 2 - Check breakout signal
    if (spreadPoints > 3.0)
        return MarketCondition.Breakout;

    // STEP 6: Classify by volatility
    if (avgRangePoints < LowVolatilityThreshold)
        return MarketCondition.Grid;
    else if (avgRangePoints < HighVolatilityThreshold)
        return MarketCondition.Scalping;
    else
        return MarketCondition.HighVolatility;
}
```

**Priority Order**:

1. **News** - Highest priority (scheduled events)
2. **Breakout** - High priority (unusual spread)
3. **Volatility** - Normal priority (Grid → Scalping → Hedge)

---

## Strategy Visualization

### Example Cycle 1: Medium Volatility → Scalping

```
T=0  Cycle #1 starts
       ↓
     Analyze Market:
       Spread: 0.00015 (1.5 pts)
       Volatility: 1.5 × 10 = 15 pts
       Time: 10:00 UTC (no news)
       Spread: 1.5 pts (no breakout)
       ↓
     Condition: MEDIUM VOLATILITY (15 pts)
       ↓
     Selected: SimpleScalpingOrchestrator
       Parameters:
         - RiskAmount: $20
         - SL: 15 pts, TP: 25 pts
         - Direction: BUY (random)
       ↓
T=1  Execute SimpleScalpingOrchestrator
       → Open BUY position
       → Hold 60 seconds
       → TP triggered at +17s
       → Profit: +$25
       ↓
T=2  Cycle complete
       Total profit: $25
       Cycles run: 1
       ↓
     Wait 30 seconds
       ↓
T=3  Start Cycle #2...
```

### Example Cycle 2: News Time → News Straddle

```
T=0    Cycle #2 starts
         ↓
       Analyze Market:
         Time: 08:28 UTC
         News at 08:30 UTC (2 min away)
         EnableNewsMode: true
         MinutesBeforeNews: 5
         ↓
       Condition: NEWS EVENT
         ↓
       Selected: NewsStraddleOrchestrator
         Parameters:
           - StraddleDistance: 15 pts
           - Volume: 0.02 lots
           - SecondsBeforeNews: 30s
         ↓
T=0.5  Execute NewsStraddleOrchestrator
         → Wait 30 seconds countdown
         → Place BUY STOP above
         → Place SELL STOP below
         → Wait for breakout
         → BUY STOP triggered
         → Cancel SELL STOP
         → TP hit at +45s
         → Profit: +$40
         ↓
T=3    Cycle complete
         Total profit: $65 ($25 + $40)
         Cycles run: 2
         ↓
       Wait 30 seconds...
```

### Example Cycle 3: High Volatility → Hedge

```
T=0    Cycle #3 starts
         ↓
       Analyze Market:
         Spread: 0.00045 (4.5 pts)
         Volatility: 4.5 × 10 = 45 pts
         ↓
       Condition: HIGH VOLATILITY (45 pts > 40)
         ↓
       Selected: QuickHedgeOrchestrator
         Parameters:
           - RiskAmount: $20 × 0.7 = $14 (reduced!)
           - SL: 25 pts, TP: 40 pts
           - HedgeTrigger: 15 pts
         ↓
T=0.5  Execute QuickHedgeOrchestrator
         → Open SELL position
         → Monitor price movement
         → Price moves -18 pts (adverse)
         → Hedge triggered! Open BUY
         → Hold both 30 seconds
         → Close all
         → Profit: -$12 (limited loss)
         ↓
T=2    Cycle complete
         Total profit: $53 ($65 - $12)
         Cycles run: 3
         ↓
       Continue...
```

---

## Volatility Analysis Method

### Demo Formula (Simplified)

```csharp
var spreadPoints = (tick.Ask - tick.Bid) / point;
var avgRangePoints = spreadPoints * 10;  // Simple multiplier

if (avgRangePoints < 15)
    return "Low Volatility";
else if (avgRangePoints < 40)
    return "Medium Volatility";
else
    return "High Volatility";
```

**Why this works**:

- Spread widens when volatility increases.
- Multiplier (10×) amplifies small spread changes into meaningful volatility estimates.
- Fast calculation without historical data.

**Limitations**:

- ⚠️ **Not suitable for production** - too simplistic.
- Doesn't account for recent price movements.
- Sensitive to broker spread changes.

### Production Recommendation

```csharp
// Use ATR (Average True Range) for real volatility
var bars = await _service.GetBarsAsync(Symbol, Timeframe.M5, count: 20);
var atr = CalculateATR(bars, period: 14);
var avgRangePoints = atr / point;

// Now classify based on ATR
if (avgRangePoints < 15)
    return MarketCondition.Grid;
// ...
```

---

## News Detection Schedule

### Default UTC Schedule

| Time (UTC) | Event Types |
|-----------|-------------|
| **08:30** | NFP, CPI, Retail Sales, Jobless Claims |
| **12:30** | Midday economic reports, Fed speeches |
| **14:00** | FOMC statements, GDP, Consumer Confidence |
| **18:00** | ECB press conferences, Eurozone data |
| **19:00** | Evening economic indicators |

### Detection Logic

```csharp
private bool IsNewsTime()
{
    var now = DateTime.UtcNow;
    var currentHourMinute = now.Hour * 60 + now.Minute;

    int[] newsMinutes = {
        8 * 60 + 30,   // 08:30
        12 * 60 + 30,  // 12:30
        14 * 60,       // 14:00
        18 * 60,       // 18:00
        19 * 60        // 19:00
    };

    foreach (var newsMin in newsMinutes)
    {
        var diff = Math.Abs(currentHourMinute - newsMin);
        if (diff <= MinutesBeforeNews)  // Default: 5 minutes
            return true;
    }

    return false;
}
```

**Trigger Window**: 5 minutes before scheduled time
- Example: For 08:30 news, triggers from 08:25 to 08:30.

---

## Safety Features

### 1. Stop-Loss Protection

```csharp
if (totalProfit < -BaseRiskAmount * 5)
{
    Console.WriteLine($"🛑 STOP: Total loss exceeds ${BaseRiskAmount * 5:F2}");
    break;  // Exit preset
}
```

**Default**: Halts if total loss exceeds $100 (5 × $20 base risk).

### 2. Cycle Limit

```csharp
int maxCycles = 100;  // Maximum 100 cycles per run

for (int cycle = 1; cycle <= maxCycles; cycle++)
{
    // Execute cycle...
}
```

**Purpose**: Prevents infinite loops, ensures eventual termination.

### 3. Inter-Cycle Pause

```csharp
await Task.Delay(30000, ct);  // 30 seconds between cycles
```

**Purpose**:

- Prevents overtrading
- Gives market time to develop
- Reduces commission costs

### 4. Emergency Close

```csharp
catch (Exception ex)
{
    Console.WriteLine($"✗ Error in cycle {cycle}: {ex.Message}");

    try {
        await _service.CloseAll(Symbol);  // Close all positions
    } catch { }

    // Continue to next cycle
}
```

**Purpose**: Closes all positions on unexpected error, then continues.

---

## Risk Management

### Adaptive Risk Sizing

```
CONDITION          BASE RISK    ACTUAL RISK    REASON
──────────────────────────────────────────────────────
Grid               $20          $20 (100%)     Normal risk
Scalping           $20          $20 (100%)     Normal risk
High Volatility    $20          $14 (70%)      ⚠️ REDUCED!
News Straddle      $20          $20 (100%)     Controlled breakout
Breakout           $20          $20 (100%)     Pending orders
```

**Key Feature**: Risk automatically reduced in high volatility to preserve capital.

### Maximum Loss Calculation

```
Given:
- BaseRiskAmount: $20
- Safety multiplier: 5×
- Max cycles: 100

Worst-case scenarios:

1. All cycles lose (impossible but theoretical):
   100 cycles × $20 = $2000 max loss

2. Safety stop triggers:
   5 cycles × $20 = $100 max loss (realistic limit)

3. High volatility cycles:
   5 cycles × $14 = $70 max loss (reduced risk)
```

### Win Rate Analysis

```
Assume:
- 40% win rate
- 100 cycles
- Average win: +$30
- Average loss: -$20

Results:
Wins: 40 × $30 = +$1200
Losses: 60 × -$20 = -$1200
Net: $0 (break-even)

With 45% win rate:
Wins: 45 × $30 = +$1350
Losses: 55 × -$20 = -$1100
Net: +$250 profit

Conclusion: 45% win rate = profitable!
```

---

## Console Output

### Example Full Cycle Output

```
+============================================================+
|  ADAPTIVE MARKET MODE PRESET                              |
+============================================================+

  Symbol: EURUSD
  Base Risk: $20.00 per cycle
  Starting Balance: $10000.00
  Running up to 100 cycles...

══════════════════════════════════════════════════════════════
  CYCLE #1
══════════════════════════════════════════════════════════════

  📊 Market Analysis:
  Spread: 1.5 points
  Estimated Volatility: 15 points
  Condition: MEDIUM VOLATILITY → SimpleScalpingOrchestrator

+============================================================+
|  SIMPLE SCALPING ORCHESTRATOR                             |
+============================================================+

  Starting balance: $10000.00
  Symbol: EURUSD
  Direction: BUY
  Risk: $20.00
  SL: 15 pts | TP: 25 pts
  Max hold: 60s

  Opening position...
  ✓ Position opened: #123456789
  Volume: 0.18 lots

  ⏳ Holding for 60s...

  ✓ Position closed automatically (SL/TP hit)

  Final balance: $10025.00
  Profit/Loss: $25.00

+============================================================+

  ✅ Cycle #1 complete
  Cycle P/L: $25.00
  Total Profit: $25.00
  Cycles Run: 1 / 100

══════════════════════════════════════════════════════════════

  ⏸ Waiting 30 seconds before next cycle...

══════════════════════════════════════════════════════════════
  CYCLE #2
══════════════════════════════════════════════════════════════

  📊 Market Analysis:
  Time: 08:28 UTC
  News detected at 08:30 UTC
  Condition: NEWS EVENT → NewsStraddleOrchestrator

[... NewsStraddleOrchestrator output ...]

  ✅ Cycle #2 complete
  Cycle P/L: $40.00
  Total Profit: $65.00
  Cycles Run: 2 / 100

══════════════════════════════════════════════════════════════

[... more cycles ...]

+============================================================+
|  FINAL RESULTS                                            |
+============================================================+
  Initial Balance: $10000.00
  Final Balance: $10350.00
  Total Profit: $350.00
  Cycles Run: 15 / 100
  Stopped: User cancelled (or max cycles/safety stop)
+============================================================+
```

---

## Usage Examples

### Example 1: Conservative Profile

```csharp
var service = new MT5Service(account);

var conservative = new AdaptiveMarketModePreset(service)
{
    Symbol = "EURUSD",
    BaseRiskAmount = 10.0,          // Lower risk
    LowVolatilityThreshold = 12.0,  // Stricter grid entry
    HighVolatilityThreshold = 45.0, // Stay in scalping longer
    EnableNewsMode = false          // Disable news trading
};

await conservative.ExecuteAsync();
```

### Example 2: Aggressive Profile

```csharp
var aggressive = new AdaptiveMarketModePreset(service)
{
    Symbol = "GBPUSD",
    BaseRiskAmount = 50.0,          // Higher risk
    LowVolatilityThreshold = 20.0,  // More grid opportunities
    HighVolatilityThreshold = 30.0, // Trigger hedge earlier
    EnableNewsMode = true
};

await aggressive.ExecuteAsync();
```

### Example 3: News-Only Mode

```csharp
var newsOnly = new AdaptiveMarketModePreset(service)
{
    Symbol = "EURUSD",
    BaseRiskAmount = 30.0,
    LowVolatilityThreshold = 1.0,   // Never trigger grid
    HighVolatilityThreshold = 1000.0, // Never trigger hedge
    EnableNewsMode = true,
    MinutesBeforeNews = 10          // Earlier news detection
};

// This will primarily trade NewsStraddleOrchestrator
await newsOnly.ExecuteAsync();
```

---

## When to Use Adaptive Preset

### ✅ Suitable Conditions

- **24/7 automated trading**: Set and forget
- **Uncertain market conditions**: Don't know which strategy to use
- **Learning/backtesting**: Test multiple strategies simultaneously
- **Diversification**: Spread risk across different approaches
- **Medium-term trading**: Run for days/weeks

### ❌ Unsuitable Conditions

- **Strong trending markets**: Better to use single directional strategy
- **Expert trader with clear setup**: Use specific orchestrator directly
- **Very small account**: Risk management may be challenging
- **Need for manual control**: Preset is fully automated

---

## Optimization

### Possible Improvements

1. **Replace volatility formula with ATR**:
   ```csharp
   var bars = await _service.GetBarsAsync(Symbol, Timeframe.M5, 20);
   var atr = CalculateATR(bars, period: 14);
   var avgRangePoints = atr / point;
   ```

2. **Add machine learning for strategy selection**:
   ```csharp
   var prediction = await MLModel.Predict(marketFeatures);
   return prediction.BestStrategy;
   ```

3. **Dynamic risk adjustment based on performance**:
   ```csharp
   if (winRate > 0.60)
       BaseRiskAmount *= 1.2;  // Increase risk
   else if (winRate < 0.40)
       BaseRiskAmount *= 0.8;  // Decrease risk
   ```

4. **Add custom news calendar API**:
   ```csharp
   var upcomingNews = await NewsAPI.GetUpcoming(Symbol);
   if (upcomingNews.Any(n => n.Impact == "High"))
       return MarketCondition.News;
   ```

---

## Related Strategies

- **[GridTradingOrchestrator](../Orchestrators_EN/GridTradingOrchestrator.md)**: Used in low volatility.
- **[SimpleScalpingOrchestrator](../Orchestrators_EN/SimpleScalpingOrchestrator.md)**: Used in medium volatility.
- **[QuickHedgeOrchestrator](../Orchestrators_EN/QuickHedgeOrchestrator.md)**: Used in high volatility.
- **[NewsStraddleOrchestrator](../Orchestrators_EN/NewsStraddleOrchestrator.md)**: Used during news events.
- **[PendingBreakoutOrchestrator](../Orchestrators_EN/PendingBreakoutOrchestrator.md)**: Used on breakout signals.

---

## Summary

**AdaptiveMarketModePreset** is an intelligent multi-strategy system:

✅ **Pros**:

- **Fully automated** - no manual strategy selection needed
- **Adaptive** - automatically adjusts to market conditions
- **Diversified** - uses 5 different approaches
- **Risk-managed** - reduced risk in high volatility, safety stops
- **24/7 capable** - designed for continuous operation
- **Educational** - demonstrates strategy coordination

❌ **Cons**:

- **Simplified volatility** - demo formula not production-ready
- **Static news schedule** - doesn't use real-time news feed
- **No machine learning** - simple rule-based logic
- **Commission costs** - frequent trading in some conditions
- **Requires monitoring** - safety stops may trigger unexpectedly

**Recommendation**: 

Excellent for learning how to combine multiple strategies into one system. The preset demonstrates intelligent orchestrator coordination and adaptive strategy selection. For production use, replace volatility calculation with ATR and integrate real-time news API.

**⚠️ DEMO WARNING**:

 This preset uses simplified market analysis (`spread × 10`) for educational purposes. For real trading, implement proper volatility measurement (ATR) and use live news calendar API.
