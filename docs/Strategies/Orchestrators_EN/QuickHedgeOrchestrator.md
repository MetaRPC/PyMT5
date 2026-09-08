# QuickHedgeOrchestrator - Protective Hedging

## Description

**QuickHedgeOrchestrator** is an orchestrator for protective hedging of a position when price moves unfavorably. It opens a primary position (BUY or SELL), then monitors the price. If the price moves against us by a specified number of points, it automatically opens an opposite position (hedge) of the same volume to lock in the loss.

**Operating Principle**: "Capital Protection" - capital protection through hedging. The primary position has SL/TP. If the price moves against us by more than `HedgeTriggerPoints`, an opposite position with the same volume is opened, which locks in further losses (positions neutralize each other).

**File**: `Examples\Orchestrators\QuickHedgeOrchestrator.cs`

---

## Architecture

```
QUICK HEDGE ORCHESTRATOR
    ↓
MT5Service Instance
    ↓
  ┌─────┼─────┐
  ↓     ↓     ↓
BuyMarket SellMarket CloseAll
ByRisk    Async      (close)
(primary) (hedge)
```

### Dependencies

- **MT5Service**: Service layer for MT5
- **MT5Sugar Extension Methods**: `BuyMarketByRisk`, `SellMarketByRisk`, `BuyMarketAsync`, `SellMarketAsync`, `CloseAll`
- **mt5_term_api**: gRPC types (`OrderSendData`, `SymbolInfoTickData`)

---

## Configuration Parameters

| Parameter | Type | Default | Description |
|----------|-----|--------------|----------|
| `Symbol` | string | `"EURUSD"` | Trading instrument |
| `RiskAmount` | double | `30.0` | Risk in dollars for primary position |
| `StopLossPoints` | int | `25` | SL for primary position |
| `TakeProfitPoints` | int | `40` | TP for primary position |
| `OpenBuyFirst` | bool | `true` | Primary position direction (true=BUY, false=SELL) |
| `HedgeTriggerPoints` | int | `15` | Hedge trigger: adverse movement in points |

### Configuration Example

```csharp
var hedgeOrchestrator = new QuickHedgeOrchestrator(service)
{
    Symbol = "GBPUSD",
    RiskAmount = 50.0,          // Risk $50
    StopLossPoints = 30,        // SL = 30 points
    TakeProfitPoints = 60,      // TP = 60 points (R:R = 1:2)
    OpenBuyFirst = true,        // Open BUY first
    HedgeTriggerPoints = 20     // Hedge if -20 points
};
```

---

## How to Run

You can run this orchestrator using any of the following commands:

```bash
dotnet run 12
dotnet run hedge
dotnet run quickhedge
```

---

## Algorithm

### Flowchart

```
START
  ↓
Get initial balance
  ↓
CONDITION: OpenBuyFirst == true?
  YES → BuyMarketByRisk(risk, SL, TP)
  NO → SellMarketByRisk(risk, SL, TP)
  ↓
Save entryPrice, Volume
  ↓
MONITORING (max 5 minutes)
  Every 2 seconds:
    → SymbolInfoTickAsync()
    → Calculate priceMovementPoints
    → Check: movement against us?
    → If against >= HedgeTriggerPoints:
         → Open opposite position (same Volume, WITHOUT SL/TP)
         → break (exit monitoring)
  Timeout → "No hedge needed"
  ↓
Task.Delay(30000)  // Hold for 30 sec
  ↓
CloseAll(Symbol)
  ↓
Return profit
END
```

### Step-by-Step Description

#### 1. Initialization (lines 35-40)

```csharp
var initialBalance = await _service.GetBalanceAsync();

Console.WriteLine($"  Starting balance: ${initialBalance:F2}");
Console.WriteLine($"  Symbol: {Symbol}");
Console.WriteLine($"  Initial direction: {(OpenBuyFirst ? "BUY" : "SELL")}");
Console.WriteLine($"  Risk: ${RiskAmount:F2}");
Console.WriteLine($"  Hedge trigger: {HedgeTriggerPoints} pts adverse");
```

#### 2. Opening primary position (lines 44-77)

```csharp
Console.WriteLine($"  Opening initial {(OpenBuyFirst ? "BUY" : "SELL")} position...");
OrderSendData initialOrder;

if (OpenBuyFirst)
{
    
    // │  PRIMARY POSITION with risk sizing                  
    // │  Has SL and TP for protection                       
    // └─────────────────────────────────────────────────────
    initialOrder = await _service.BuyMarketByRisk(
        symbol: Symbol,             // "EURUSD"
        stopPoints: StopLossPoints, // 25 points
        riskMoney: RiskAmount,      // $30
        tpPoints: TakeProfitPoints, // 40 points
        comment: "Hedge-Primary"
    );
}
else
{
    initialOrder = await _service.SellMarketByRisk(
        symbol: Symbol,
        stopPoints: StopLossPoints,
        riskMoney: RiskAmount,
        tpPoints: TakeProfitPoints,
        comment: "Hedge-Primary"
    );
}

if (initialOrder.ReturnedCode != 10009)
{
    Console.WriteLine($"  ✗ Initial order failed: {initialOrder.Comment}");
    return 0;
}

Console.WriteLine($"  ✓ Initial position: #{initialOrder.Order}");
Console.WriteLine($"  Entry price: {initialOrder.Price:F5}");
Console.WriteLine($"  Volume: {initialOrder.Volume:F2} lots");


// │  SAVE CRITICALLY IMPORTANT DATA                         
// └─────────────────────────────────────────────────────────
var entryPrice = initialOrder.Price;  // For movement calculation
var point = await _service.GetPointAsync(Symbol);  // Point size
```

**Critically important**:
- Uses **BuyMarketByRisk** / **SellMarketByRisk** with SL/TP
- Saves `entryPrice` for monitoring movement
- Saves `initialOrder.Volume` for hedging the same volume

#### 3. Monitoring for hedge trigger (lines 82-133)

```csharp
Console.WriteLine($"  Monitoring price for hedge trigger...");

bool hedgePlaced = false;
ulong? hedgeTicket = null;
var monitorStart = DateTime.UtcNow;
var maxMonitorTime = TimeSpan.FromMinutes(5);


// │  MONITORING LOOP (every 2 sec, max 5 minutes)          
// └─────────────────────────────────────────────────────────
while (DateTime.UtcNow - monitorStart < maxMonitorTime && !ct.IsCancellationRequested)
{
    await Task.Delay(2000, ct);  // Every 2 seconds

    
    // │  STEP 1: Get current price                      
    // └─────────────────────────────────────────────────
    var tick = await _service.SymbolInfoTickAsync(Symbol);

    // For BUY position watch Bid (closing price)
    // For SELL position watch Ask (closing price)
    var currentPrice = OpenBuyFirst ? tick.Bid : tick.Ask;

    
    // │  STEP 2: Calculate movement in points           
    // └─────────────────────────────────────────────────
    var priceMovementPoints = Math.Abs((currentPrice - entryPrice) / point);

    
    // │  STEP 3: Check movement direction               
    // └─────────────────────────────────────────────────
    // For BUY: adverse = price BELOW entry (currentPrice < entryPrice)
    // For SELL: adverse = price ABOVE entry (currentPrice > entryPrice)
    var isAdverse = OpenBuyFirst ? (currentPrice < entryPrice) : (currentPrice > entryPrice);

    
    // │  STEP 4: KEY CHECK - Hedge trigger?                 
    // └─────────────────────────────────────────────────────
    if (isAdverse && priceMovementPoints >= HedgeTriggerPoints)
    {
        Console.WriteLine($"\n  ⚠️  Price moved {priceMovementPoints:F1} pts against us!");
        Console.WriteLine($"  Opening hedge {(OpenBuyFirst ? "SELL" : "BUY")} position...");

        
        // │  OPENING HEDGE POSITION                     
        // │  IMPORTANT: WITHOUT SL/TP, same Volume!     
        // └─────────────────────────────────────────────
        OrderSendData hedgeOrder;
        if (OpenBuyFirst)
        {
            // Primary was BUY → hedge SELL
            hedgeOrder = await _service.SellMarketAsync(
                symbol: Symbol,
                volume: initialOrder.Volume,  // ← SAME VOLUME!
                comment: "Hedge-Protection"
                // WITHOUT sl and tp parameters!
            );
        }
        else
        {
            // Primary was SELL → hedge BUY
            hedgeOrder = await _service.BuyMarketAsync(
                symbol: Symbol,
                volume: initialOrder.Volume,  // ← SAME VOLUME!
                comment: "Hedge-Protection"
            );
        }

        if (hedgeOrder.ReturnedCode == 10009)
        {
            hedgeTicket = hedgeOrder.Order;
            hedgePlaced = true;
            Console.WriteLine($"  ✓ Hedge placed: #{hedgeOrder.Order}\n");
            break;  // Exit monitoring
        }
        else
        {
            Console.WriteLine($"  ✗ Hedge failed: {hedgeOrder.Comment}\n");
        }
    }
}

if (!hedgePlaced)
{
    Console.WriteLine("  ✓ No hedge needed - price moved favorably\n");
}
```

**Key logic**:

1. **Movement calculation**:
   ```
   Example for BUY:
   entryPrice = 1.10000
   currentPrice = 1.09985
   point = 0.00001

   priceMovementPoints = |1.09985 - 1.10000| / 0.00001 = 15 points
   isAdverse = 1.09985 < 1.10000 → true (price lower)
   ```

2. **Hedge trigger**:
   ```
   HedgeTriggerPoints = 15

   if (isAdverse && priceMovementPoints >= 15)
   {
       // 15 >= 15 → TRUE → open hedge!
   }
   ```

3. **Hedge without SL/TP**:

   - Hedge position does **NOT have** SL and TP
   - Hedge purpose is to **freeze the loss**, not to make profit
   - Same Volume as primary position → **full hedging**

#### 4. Holding and closing (lines 140-146)

```csharp

// │  Hold positions for 30 seconds                          
// └─────────────────────────────────────────────────────────
Console.WriteLine("  ⏳ Holding positions for 30 seconds...\n");
await Task.Delay(30000, ct);


// │  Close ALL positions simultaneously                     
// └─────────────────────────────────────────────────────────
Console.WriteLine("  Closing all positions...");
await _service.CloseAll(Symbol);
Console.WriteLine("  ✓ All closed");
```

**What happens**:

- If hedge placed → closes **BOTH** positions (primary + hedge)
- If hedge NOT placed → closes only primary position

---

## Strategy Visualization

### Scenario 1: Hedge triggered (loss limited)

```
T=0      BuyMarketByRisk(risk=$30, SL=25pts, TP=40pts)
         │
         ├─► Volume calculation: $30 / (25 × $10) = 0.12 lots
         │
         ├─► Opened BUY position 0.12 lots @ 1.10000
         │   SL: 1.09975 (-25 pts)
         │   TP: 1.10040 (+40 pts)
         │   HedgeTrigger: -15 pts (@ 1.09985)
         │
         │   Price moves:
         │   1.10000 → 1.09995 → 1.09990 → 1.09985...
         │
T=10s    ├─► currentPrice = 1.09985
         │   priceMovementPoints = |1.09985 - 1.10000| / 0.00001 = 15
         │   isAdverse = true (1.09985 < 1.10000)
         │
         │   HEDGE TRIGGER! (15 >= 15)
         │
         ├─► SellMarketAsync(volume=0.12, NO SL/TP)
         │   └─► Opened SELL 0.12 lots @ 1.09985
         │
         │   STATE:
         │   
         │   │ BUY  0.12 @ 1.10000 (loss -15 pts)   
         │   │ SELL 0.12 @ 1.09985                  
         │   │ ────────────────────────────────────  
         │   │ NET: HEDGE (positions neutralize)    
         │   └──────────────────────────────────────
         │
         │   Price continues to fall:
         │   1.09985 → 1.09980 → 1.09975 → 1.09970...
         │
T=15s    ├─► currentPrice = 1.09970
         │
         │   BUY position:  1.10000 → 1.09970 = -30 pts
         │   SELL position: 1.09985 → 1.09970 = +15 pts
         │   ────────────────────────────────────────
         │   Total: -30 + 15 = -15 pts (FROZEN!)
         │
T=40s    ├─► Task.Delay(30000) finished
         │
         ├─► CloseAll("EURUSD")
         │   ├─► Closed BUY position
         │   └─► Closed SELL position
         │
         │   Final P/L:
         │   BUY:  -30 pts × 0.12 = -$36
         │   SELL: +15 pts × 0.12 = +$18
         │   ────────────────────────
         │   TOTAL: -$18
         │
         └─► Result: Loss -$18 instead of -$36 WITHOUT hedge!

WITHOUT HEDGE: Loss would be -30 pts × 0.12 = -$36
WITH HEDGE:    Loss only -15 pts × 0.12 = -$18
SAVED: $18 (50% less loss!)
```

### Scenario 2: Hedge NOT needed (price goes in our direction)

```
T=0      BuyMarketByRisk(risk=$30, SL=25pts, TP=40pts)
         │
         ├─► Opened BUY position 0.12 lots @ 1.10000
         │   HedgeTrigger: -15 pts
         │
         │   Price moves UP:
         │   1.10000 → 1.10010 → 1.10025 → 1.10040...
         │
T=20s    ├─► currentPrice = 1.10040
         │   priceMovementPoints = |1.10040 - 1.10000| / 0.00001 = 40
         │   isAdverse = false (1.10040 > 1.10000) ← IN OUR FAVOR!
         │
         │   Hedge does NOT trigger (favorable movement)
         │
         ├─► TP HIT! (1.10040)
         │   Position closed automatically
         │
T=5min   ├─► Monitoring finished (timeout)
         │   └─► "No hedge needed - price moved favorably"
         │
T=5min   ├─► Task.Delay(30000) finished
+30s     │
         ├─► CloseAll("EURUSD")
         │   └─► Position already closed (TP hit earlier)
         │
         │   Final P/L:
         │   BUY: +40 pts × 0.12 = +$48
         │
         └─► Result: Profit +$48

HEDGE NOT NEEDED → got full profit from TP!
```

### Scenario 3: SL hit BEFORE hedge trigger

```
T=0      BuyMarketByRisk(risk=$30, SL=25pts, TP=40pts)
         │
         ├─► Opened BUY position 0.12 lots @ 1.10000
         │   SL: 1.09975 (-25 pts)
         │   HedgeTrigger: 1.09985 (-15 pts)
         │
         │   Price moves SLOWLY down:
         │   1.10000 → 1.09990 (-10 pts, hedge not triggered)
         │
T=30s    ├─► Then SHARPLY falls:
         │   1.09990 → 1.09975 (SL reached!)
         │
         ├─► SL HIT!
         │   Position closed automatically
         │   Loss: -25 pts × 0.12 = -$30 (exactly riskMoney!)
         │
T=40s    ├─► Monitoring continues...
         │   But position is gone → do nothing
         │
T=5min   ├─► Monitoring timeout
+30s     │
         ├─► CloseAll("EURUSD")
         │   └─► Position already closed
         │
         └─► Result: Loss -$30 (as planned)

HEDGE NOT TRIGGERED → SL closed position faster than trigger reached
```

---

## Used MT5Sugar Methods

### 1. BuyMarketByRisk / SellMarketByRisk

**Usage**: Opening **primary** position with SL and TP.

```csharp
initialOrder = await _service.BuyMarketByRisk(
    symbol: Symbol,
    stopPoints: StopLossPoints,  // 25 points
    riskMoney: RiskAmount,       // $30
    tpPoints: TakeProfitPoints,  // 40 points
    comment: "Hedge-Primary"
);
```

**Why this method**:

- Automatically calculates Volume based on risk
- Sets SL and TP for protection
- Returns `initialOrder.Volume` for hedge

### 2. BuyMarketAsync / SellMarketAsync

**Usage**: Opening **hedge** position WITHOUT SL/TP.

```csharp
hedgeOrder = await _service.SellMarketAsync(
    symbol: Symbol,
    volume: initialOrder.Volume,  // ← SAME volume as primary
    comment: "Hedge-Protection"
    // WITHOUT sl and tp!
);
```

**Why WITHOUT SL/TP**:

- Hedge is designed to **lock in the loss**, not to make profit
- SL on hedge could close it prematurely
- Both positions closed simultaneously via `CloseAll()`

### 3. GetPointAsync

```csharp
var point = await _service.GetPointAsync(Symbol);
```

**Purpose**: Get point size for the symbol.

**Usage**:

- Calculate price movement in points (line 95)

### 4. SymbolInfoTickAsync

```csharp
var tick = await _service.SymbolInfoTickAsync(Symbol);
var currentPrice = OpenBuyFirst ? tick.Bid : tick.Ask;
```

**Usage**:

- Monitor current price every 2 seconds
- For BUY use **Bid** (BUY closing price)
- For SELL use **Ask** (SELL closing price)

### 5. CloseAll

```csharp
await _service.CloseAll(Symbol);
```

**Usage**:

- Close **all** positions for the symbol simultaneously
- Closes both primary and hedge position

---

## Hedging Mathematics

### Full hedging (same Volume)

```
Primary position: BUY 0.12 lots @ 1.10000
Hedge:            SELL 0.12 lots @ 1.09985

When price moves:
┌───────────┬──────────────┬──────────────┬────────────
│ Price     │ BUY P/L      │ SELL P/L     │ Total      
├───────────┼──────────────┼──────────────┼────────────
│ 1.10000   │ 0 pts        │ +15 pts      │ +15 pts    
│ 1.09995   │ -5 pts       │ +10 pts      │ +5 pts     
│ 1.09990   │ -10 pts      │ +5 pts       │ -5 pts     
│ 1.09985   │ -15 pts      │ 0 pts        │ -15 pts     ← Hedge point
│ 1.09980   │ -20 pts      │ -5 pts       │ -15 pts     ← FROZEN!
│ 1.09975   │ -25 pts      │ -10 pts      │ -15 pts     ← FROZEN!
│ 1.09970   │ -30 pts      │ -15 pts      │ -15 pts     ← FROZEN!
└───────────┴──────────────┴──────────────┴────────────

CONCLUSION: After hedge placement, total P/L FROZEN at -15 pts!
```

### Partial hedging (smaller Volume)

```
Primary position: BUY 0.12 lots @ 1.10000
Hedge:            SELL 0.06 lots @ 1.09985 (50% hedge)

When price moves:
┌───────────┬──────────────┬──────────────┬────────────
│ Price     │ BUY P/L      │ SELL P/L     │ Total      
├───────────┼──────────────┼──────────────┼────────────
│ 1.09985   │ -15 pts      │ 0 pts        │ -15 pts    
│ 1.09980   │ -20 pts      │ -2.5 pts     │ -22.5 pts   ← Continues to grow!
│ 1.09975   │ -25 pts      │ -5 pts       │ -30 pts    
└───────────┴──────────────┴──────────────┴────────────

CONCLUSION: Partial hedge only SLOWS loss, but doesn't freeze it!
```

**QuickHedgeOrchestrator uses FULL hedging (100%).**

---

## Risk Management

### Choosing HedgeTriggerPoints

```
Rule: HedgeTriggerPoints should be LESS than StopLossPoints

Example:
- StopLossPoints = 25
- HedgeTriggerPoints = 15  ✓ (less than SL)

If HedgeTriggerPoints >= StopLossPoints:
- Hedge will never trigger (SL closes position first)

Recommendation:
HedgeTriggerPoints = StopLossPoints × 0.5 - 0.7
25 pts SL → 12-18 pts hedge trigger
```

### Savings through hedging

```
Scenario WITHOUT hedge:
- Price goes against us -30 pts
- Loss: -30 pts × 0.12 = -$36

Scenario WITH hedge (trigger 15 pts):
- Price -15 pts → hedge opened
- Price continues to fall to -30 pts
- Loss: -15 pts × 0.12 = -$18

SAVED: $36 - $18 = $18 (50%!)
```

### Recommendations

1. **HedgeTriggerPoints**:
   - Not too close (avoid false triggers from noise)
   - Not too far (otherwise lose too much before hedge)
   - Optimal: 50-70% of StopLossPoints

2. **MaxMonitorTime**:
   - Default 5 minutes is enough
   - For volatile instruments: 2-3 minutes
   - For low volatility: 10 minutes

3. **When to use**:
   - Before important news (high volatility)
   - When uncertain about direction
   - For capital protection in aggressive strategies

4. **When NOT to use**:
   - On trending markets (hedge prevents profit)
   - With low spreads and commissions (hedging cost)
   - For long-term positions (swap accumulates on both sides)

---

## Usage Examples

### Example 1: Conservative hedging

```csharp
var conservativeHedge = new QuickHedgeOrchestrator(service)
{
    Symbol = "EURUSD",
    RiskAmount = 20.0,
    StopLossPoints = 20,
    TakeProfitPoints = 40,    // R:R = 1:2
    OpenBuyFirst = true,
    HedgeTriggerPoints = 10   // Quick hedge (50% of SL)
};

var profit = await conservativeHedge.ExecuteAsync();
```

### Example 2: Aggressive hedging

```csharp
var aggressiveHedge = new QuickHedgeOrchestrator(service)
{
    Symbol = "GBPUSD",
    RiskAmount = 50.0,
    StopLossPoints = 30,
    TakeProfitPoints = 90,    // R:R = 1:3
    OpenBuyFirst = false,     // SELL
    HedgeTriggerPoints = 20   // Late hedge (67% of SL)
};

var profit = await aggressiveHedge.ExecuteAsync();
```

### Example 3: News hedging

```csharp
// Before NFP or other volatile news release
var newsHedge = new QuickHedgeOrchestrator(service)
{
    Symbol = "EURUSD",
    RiskAmount = 30.0,
    StopLossPoints = 40,      // Wide SL (volatility)
    TakeProfitPoints = 80,
    OpenBuyFirst = true,
    HedgeTriggerPoints = 25   // Medium trigger
};

var profit = await newsHedge.ExecuteAsync();
```

---

## Error Handling

### Exception with emergency close (lines 158-168)

```csharp
catch (Exception ex)
{
    Console.WriteLine($"\n  ✗ Error: {ex.Message}");

    
    // │  EMERGENCY CLOSE ALL POSITIONS                  
    // └─────────────────────────────────────────────────
    try
    {
        await _service.CloseAll(Symbol);
    }
    catch { }  // Ignore errors during emergency close

    return 0;
}
```

**Correct approach**:
- On any error → try to close all positions
- Closes both primary and hedge (if any)

---

## Console Output

### Output example (hedge triggered)

```
+============================================================+
|  QUICK HEDGE ORCHESTRATOR                                 |
+============================================================+

  Starting balance: $10000.00
  Symbol: EURUSD
  Initial direction: BUY
  Risk: $30.00
  Hedge trigger: 15 pts adverse

  Opening initial BUY position...
  ✓ Initial position: #123456789
  Entry price: 1.10000
  Volume: 0.12 lots

  Monitoring price for hedge trigger...

  ⚠️  Price moved 15.2 pts against us!
  Opening hedge SELL position...
  ✓ Hedge placed: #123456790

  ⏳ Holding positions for 30 seconds...

  Closing all positions...
  ✓ All closed

  Final balance: $9982.00
  Net Profit/Loss: -$18.00
  Hedged trade

+============================================================+
```

### Output example (hedge NOT needed)

```
+============================================================+
|  QUICK HEDGE ORCHESTRATOR                                 |
+============================================================+

  Starting balance: $10000.00
  Symbol: EURUSD
  Initial direction: BUY
  Risk: $30.00
  Hedge trigger: 15 pts adverse

  Opening initial BUY position...
  ✓ Initial position: #123456789
  Entry price: 1.10000
  Volume: 0.12 lots

  Monitoring price for hedge trigger...
  ✓ No hedge needed - price moved favorably

  ⏳ Holding positions for 30 seconds...

  Closing all positions...
  ✓ All closed

  Final balance: $10048.00
  Net Profit/Loss: $48.00
  Unhedged trade

+============================================================+
```

---

## When to Use Quick Hedge

### ✅ Suitable Conditions

- **Before important news**: NFP, central bank decisions, CPI
- **High uncertainty**: Unclear market direction
- **Capital protection**: Priority is not to lose, not to earn
- **Volatile sessions**: London/New York open
- **Learning**: Stress reduction for beginners

### ❌ Unsuitable Conditions

- **Strong trend**: Hedge prevents full profit
- **Low volatility**: Hedge unlikely to be needed
- **High commissions**: Double positions = double costs
- **Long-term trading**: Swap accumulates on both sides

---

## Optimization

### Possible improvements

1. **Partial hedging**:
   ```csharp
   hedgeOrder = await _service.SellMarketAsync(
       symbol: Symbol,
       volume: initialOrder.Volume * 0.5,  // 50% hedge
       comment: "Hedge-Partial"
   );
   ```

2. **Close hedge on recovery**:
   ```csharp
   // If price returns to entry point
   if (!isAdverse && priceMovementPoints < 5 && hedgePlaced)
   {
       await _service.CloseByTicket(hedgeTicket.Value);
       hedgePlaced = false;
   }
   ```

3. **Dynamic trigger based on ATR**:
   ```csharp
   var atr = await GetATR(Symbol, period: 14);
   HedgeTriggerPoints = (int)(atr * 0.4);
   ```

---

## Related Orchestrators

- **[SimpleScalpingOrchestrator](SimpleScalpingOrchestrator.md)**: Without hedging.

- **[PendingBreakoutOrchestrator](PendingBreakoutOrchestrator.md)**: OCO instead of hedge.

- **[NewsStraddleOrchestrator](NewsStraddleOrchestrator.md)**: Two-sided pending orders.

---

## Summary

**QuickHedgeOrchestrator** is a capital protection strategy through hedging:

✅ **Pros**:

- Protection from strong adverse movements
- Freezes loss at trigger level
- Psychological comfort (less stress)
- Suitable for news trading

❌ **Cons**:

- Double commissions and spread
- May limit profit on reversal
- Swap accumulates on both positions
- More complex for beginners to understand

**Recommendation**: 
Use during periods of high uncertainty or before important events. Don't use on trending markets. Hedge is **protection**, not a way to earn.
