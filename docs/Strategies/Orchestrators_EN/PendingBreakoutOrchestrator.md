# PendingBreakoutOrchestrator - Level Breakouts

## Description

**PendingBreakoutOrchestrator** is an orchestrator for catching breakouts in any direction. It places two pending orders simultaneously: Buy Stop above the current price and Sell Stop below the current price. When the price breaks a level in either direction, the corresponding order triggers and the opposite one is canceled.

**Principle**: OCO strategy (One Cancels Other) - when one order triggers, the second is automatically canceled. This allows catching directional movements without predicting the direction in advance.

**File**: `Examples\Orchestrators\PendingBreakoutOrchestrator.cs`

---

## Architecture

```
PENDING BREAKOUT ORCHESTRATOR
    ↓
MT5Service Instance
    ↓
Three main operations:
  → BuyStopPoints (above price)
  → SellStopPoints (below price)
  → CloseByTicket (cancel order)
```

### Dependencies

- **MT5Service**: Service layer for MT5
- **MT5Sugar Extension Methods**: `BuyStopPoints`, `SellStopPoints`, `CloseByTicket`
- **mt5_term_api**: gRPC types (`OrderSendData`, `SymbolInfoTickData`, `OpenedOrdersTicketsData`)

---

## Configuration Parameters

| Parameter | Type | Default | Description |
|----------|-----|--------------|----------|
| `Symbol` | string | `"EURUSD"` | Trading instrument |
| `BreakoutDistancePoints` | int | `25` | Distance from current price to place orders (in points) |
| `StopLossPoints` | int | `15` | Stop loss in points |
| `TakeProfitPoints` | int | `30` | Take profit in points |
| `Volume` | double | `0.01` | Volume in lots |
| `MaxWaitMinutes` | int | `30` | Maximum waiting time for breakout |

### Configuration example

```csharp
var breakoutOrchestrator = new PendingBreakoutOrchestrator(service)
{
    Symbol = "GBPUSD",
    BreakoutDistancePoints = 30,   // Orders at 30 points distance
    StopLossPoints = 20,            // SL = 20 points
    TakeProfitPoints = 50,          // TP = 50 points (R:R = 1:2.5)
    Volume = 0.02,                  // 0.02 lots
    MaxWaitMinutes = 45             // Wait 45 minutes
};
```

---

## Algorithm

### Flowchart

```
START
  │
  ├─► Get initial balance
  │
  ├─► Get current price (Bid/Ask)
  │
  ├─► BuyStopPoints(+BreakoutDistancePoints)
  │    └─► If error → return 0
  │
  ├─► SellStopPoints(-BreakoutDistancePoints)
  │    └─► If error → cancel BuyStop, return 0
  │
  ├─► MONITORING (every 3 sec, max MaxWaitMinutes)
  │    │
  │    ├─► OpenedOrdersTicketsAsync()
  │    │
  │    ├─► Check: BuyStop still pending?
  │    ├─► Check: SellStop still pending?
  │    │
  │    └─► CONDITIONS:
  │         ├─► If BuyStop executed, SellStop pending
  │         │    → Upward breakout → cancel SellStop → break
  │         │
  │         ├─► If SellStop executed, BuyStop pending
  │         │    → Downward breakout → cancel BuyStop → break
  │         │
  │         ├─► If both executed/canceled → break
  │         │
  │         └─► If timeout → cancel both → break
  │
  ├─► Get final balance
  │
  └─► Return profit
END
```

### Step-by-step description

#### 1. Initialization (lines 35-46)

```csharp
var initialBalance = await _service.GetBalanceAsync();
var tick = await _service.SymbolInfoTickAsync(Symbol);

Console.WriteLine($"  Starting balance: ${initialBalance:F2}");
Console.WriteLine($"  Current: Bid={tick.Bid:F5}, Ask={tick.Ask:F5}");
```

**What happens**:

- Initial balance is saved
- Current price is obtained for display

#### 2. Placing Buy Stop (lines 48-65)

```csharp
var buyStopResult = await _service.BuyStopPoints(
    symbol: Symbol,                         // "EURUSD"
    volume: Volume,                         // 0.01
    priceOffsetPoints: BreakoutDistancePoints,  // +25 (POSITIVE!)
    slPoints: StopLossPoints,               // 15
    tpPoints: TakeProfitPoints,             // 30
    comment: "Breakout-Buy"
);

if (buyStopResult.ReturnedCode != 10009)
{
    Console.WriteLine($"  ✗ BUY STOP failed: {buyStopResult.Comment}");
    return 0;  // Emergency exit
}
```

**Critically important**:

- `priceOffsetPoints` = **POSITIVE** value (`+25`)
- `BuyStopPoints` places order **ABOVE** current price
- Buy Stop = buy order on upward breakout

**Calculation example**:
```
Current Ask price: 1.10000
BreakoutDistancePoints: 25
point: 0.00001

BuyStop price = 1.10000 + (25 × 0.00001) = 1.10025

When Ask price reaches 1.10025 → order executes → BUY position opens
```

#### 3. Placing Sell Stop (lines 67-86)

```csharp
var sellStopResult = await _service.SellStopPoints(
    symbol: Symbol,
    volume: Volume,
    priceOffsetPoints: -BreakoutDistancePoints,  // -25 (NEGATIVE!)
    slPoints: StopLossPoints,
    tpPoints: TakeProfitPoints,
    comment: "Breakout-Sell"
);

if (sellStopResult.ReturnedCode != 10009)
{
    Console.WriteLine($"  ✗ SELL STOP failed: {sellStopResult.Comment}");
    Console.WriteLine("  Canceling BUY STOP...");
    await _service.CloseByTicket(buyStopResult.Order);  // ← Cancel first order!
    return 0;
}
```

**Critically important**:

- `priceOffsetPoints` = **NEGATIVE** value (`-25`)
- `SellStopPoints` places order **BELOW** current price
- Sell Stop = sell order on downward breakout
- If placement fails → **cancel BuyStop** to not leave hanging order

**Calculation example**:
```
Current Bid price: 1.10000
BreakoutDistancePoints: 25 (but we use -25)
point: 0.00001

SellStop price = 1.10000 + (-25 × 0.00001) = 1.09975

When Bid price falls to 1.09975 → order executes → SELL position opens
```

#### 4. Monitoring for breakout (lines 89-129)

```csharp
var startTime = DateTime.UtcNow;
var timeout = TimeSpan.FromMinutes(MaxWaitMinutes);
ulong? executedOrder = null;
ulong? cancelOrder = null;

while (DateTime.UtcNow - startTime < timeout && !ct.IsCancellationRequested)
{
    await Task.Delay(3000, ct);  // Every 3 seconds

    
    // │  Get list of OPEN PENDING ORDERS                   
    // └─────────────────────────────────────────────────────
    var tickets = await _service.OpenedOrdersTicketsAsync();

    bool buyStillPending = false;
    bool sellStillPending = false;

    
    // │  Check if our orders are in the list                
    // └─────────────────────────────────────────────────────
    foreach (var ticket in tickets.OpenedOrdersTickets)
    {
        if (ticket == (long)buyStopResult.Order) buyStillPending = true;
        if (ticket == (long)sellStopResult.Order) sellStillPending = true;
    }

    
    // │  BREAKOUT DETECTION LOGIC                           
    // └─────────────────────────────────────────────────────

    // CASE 1: BuyStop executed (not in list), SellStop still pending
    if (!buyStillPending && sellStillPending)
    {
        Console.WriteLine("  🚀 BUY STOP EXECUTED! Upward breakout!");
        executedOrder = buyStopResult.Order;
        cancelOrder = sellStopResult.Order;  // ← Cancel opposite
        break;
    }

    // CASE 2: SellStop executed, BuyStop still pending
    else if (buyStillPending && !sellStillPending)
    {
        Console.WriteLine("  🚀 SELL STOP EXECUTED! Downward breakout!");
        executedOrder = sellStopResult.Order;
        cancelOrder = buyStopResult.Order;   // ← Cancel opposite
        break;
    }

    // CASE 3: Both disappeared from list (rare case)
    else if (!buyStillPending && !sellStillPending)
    {
        Console.WriteLine("  ✓ Both orders executed or canceled");
        break;
    }

    // CASE 4: Both still pending → continue waiting
}
```

**Key logic**:

- `OpenedOrdersTicketsAsync()` returns only **PENDING** orders
- If order executed → it becomes **position** and disappears from list
- Check for our tickets' presence in list
- If one disappeared and other still there → breakout happened!

#### 5. Canceling opposite order (lines 131-145)

```csharp
if (cancelOrder.HasValue)
{
    
    // │  One order executed → cancel opposite               
    // └─────────────────────────────────────────────────────
    Console.WriteLine($"  Canceling opposite order #{cancelOrder.Value}...");
    await _service.CloseByTicket(cancelOrder.Value);
    Console.WriteLine("  ✓ Canceled");
}
else
{
    
    // │  Timeout → cancel BOTH orders                       
    // └─────────────────────────────────────────────────────
    Console.WriteLine($"  ⏱ Timeout after {MaxWaitMinutes} minutes - canceling both orders...");
    await _service.CloseByTicket(buyStopResult.Order);
    await _service.CloseByTicket(sellStopResult.Order);
    Console.WriteLine("  ✓ Both canceled");
}
```

**Two scenarios**:

1. **Breakout happened** → cancel one opposite order
2. **Timeout** → cancel both orders (breakout didn't occur)

---

## Strategy Visualization

### Order placement

```
Price direction: ▲

1.10025 → BUY STOP (+25 pts from Ask)
          TP: 1.10055 (+30 pts)
          SL: 1.10010 (-15 pts)

          If price goes UP:
            → BuyStop triggers
            → SellStop cancels

1.10000 → CURRENT PRICE (Bid/Ask middle)

          If price goes DOWN:
            → SellStop triggers
            → BuyStop cancels

1.09975 → SELL STOP (-25 pts from Bid)
          TP: 1.09945 (-30 pts)
          SL: 1.09990 (+15 pts)

Price direction: ▼
```

### Scenario 1: Upward breakout

```
T=0      Placed:
         BuyStop @ 1.10025
         SellStop @ 1.09975

T=5min   Price: 1.10015 (moving up)
         Both orders still pending

T=8min   Price: 1.10026 (breakout!)
         
         │  BuyStop @ 1.10025 EXECUTED!      
         │  Opened position: BUY 0.01 lots   
         │  Entry: 1.10025                   
         │  SL: 1.10010                      
         │  TP: 1.10055                      
         └───────────────────────────────────

T=8min   Orchestrator detects:
+3s      buyStillPending = false (disappeared from list)
         sellStillPending = true (still in list)

         → UPWARD BREAKOUT!
         → Cancel SellStop @ 1.09975

T=15min  Price: 1.10056
         TP triggered → position closed
         Profit: +30 points = +$3.00
```

### Scenario 2: Downward breakout

```
T=0      Placed:
         BuyStop @ 1.10025
         SellStop @ 1.09975

T=3min   Price: 1.09990 (moving down)
         Both orders still pending

T=6min   Price: 1.09974 (breakout!)
         
         │  SellStop @ 1.09975 EXECUTED!     
         │  Opened position: SELL 0.01 lots  
         │  Entry: 1.09975                   
         │  SL: 1.09990                      
         │  TP: 1.09945                      
         └───────────────────────────────────

T=6min   Orchestrator detects:
+3s      sellStillPending = false
         buyStillPending = true

         → DOWNWARD BREAKOUT!
         → Cancel BuyStop @ 1.10025

T=10min  Price: 1.09944
         TP triggered → position closed
         Profit: +30 points = +$3.00
```

### Scenario 3: Timeout (breakout didn't happen)

```
T=0      Placed:
         BuyStop @ 1.10025
         SellStop @ 1.09975

T=5min   Price: 1.10005 (flat)
T=10min  Price: 1.09995 (flat)
T=15min  Price: 1.10008 (flat)
...
T=30min  TIMEOUT!
         Both orders still pending

         → Cancel BuyStop
         → Cancel SellStop
         → Profit: $0.00
```

---

## How to Run

You can execute this orchestrator using several command variations:

```bash
# Option 1: By number
dotnet run 11

# Option 2: By short name
dotnet run breakout

# Option 3: By full name
dotnet run pendingbreakout
```

All three commands will launch the **PendingBreakoutOrchestrator** with the default configuration or the settings you specify in the code.

---

## Used MT5Sugar Methods

### 1. BuyStopPoints

```csharp
public static async Task<OrderSendData> BuyStopPoints(
    this MT5Service service,
    string symbol,
    double volume,
    int priceOffsetPoints,  // POSITIVE for above price
    int slPoints = 0,
    int tpPoints = 0,
    string comment = ""
)
```

**Purpose**: Places pending Buy Stop order (buy order on upward breakout).

**Parameters in PendingBreakoutOrchestrator**:

- `priceOffsetPoints`: **POSITIVE** value (`+25`)
- Placed **ABOVE** current Ask price
- Triggers on upward price movement

**Price calculation**:
```csharp
var tick = await service.SymbolInfoTickAsync(symbol);
double askPrice = tick.Ask;  // For BUY use Ask

double price = askPrice + (priceOffsetPoints × point);
// 1.10000 + (25 × 0.00001) = 1.10025
```

### 2. SellStopPoints

```csharp
public static async Task<OrderSendData> SellStopPoints(
    this MT5Service service,
    string symbol,
    double volume,
    int priceOffsetPoints,  // NEGATIVE for below price
    int slPoints = 0,
    int tpPoints = 0,
    string comment = ""
)
```

**Purpose**: Places pending Sell Stop order (sell order on downward breakout).

**Parameters in PendingBreakoutOrchestrator**:

- `priceOffsetPoints`: **NEGATIVE** value (`-25`)
- Placed **BELOW** current Bid price
- Triggers on downward price movement

**Price calculation**:
```csharp
var tick = await service.SymbolInfoTickAsync(symbol);
double bidPrice = tick.Bid;  // For SELL use Bid

double price = bidPrice + (priceOffsetPoints × point);
// 1.10000 + (-25 × 0.00001) = 1.09975
```

### 3. CloseByTicket

```csharp
public static async Task CloseByTicket(
    this MT5Service service,
    ulong ticket
)
```

**Purpose**: Closes position or cancels pending order by ticket number.

**Usage in orchestrator**:

- Cancel opposite order on breakout (line 135)
- Cancel both orders on timeout (lines 142-143)
- Emergency BuyStop cancellation if SellStop placement failed (line 82)

### 4. OpenedOrdersTicketsAsync

```csharp
public async Task<OpenedOrdersTicketsData> OpenedOrdersTicketsAsync()
```

**Purpose**: Gets list of tickets for all **PENDING** orders (not positions!).

**Returns**:
```csharp
public class OpenedOrdersTicketsData
{
    public List<long> OpenedOrdersTickets { get; set; }  // Pending orders
    public List<long> OpenedPositionTickets { get; set; } // Open positions
}
```

**Usage**:

- Check order presence in list (lines 103-107)
- If order disappeared from list → it executed

---

## Risk Management

### Maximum risk calculation

```
Risk per trade = Volume × StopLossPoints × ValueOfPoint

For EURUSD (ValueOfPoint = $10 for 1.0 lot):
- Volume = 0.01
- StopLossPoints = 15
- Risk = 0.01 × 15 × $10 = $1.50

Potential profit:
- TakeProfitPoints = 30
- Profit = 0.01 × 30 × $10 = $3.00

Risk/Reward Ratio = 1.50 / 3.00 = 1:2
```

### Recommendations

1. **SL/TP ratio**:
   - Default: SL=15, TP=30 (R:R = 1:2)
   - Excellent ratio for breakout strategies
   - Even 40% win rate will be profitable

2. **Breakout distance**:
   - `BreakoutDistancePoints` should account for volatility
   - Too close → false breakouts (noise)
   - Too far → miss real breakouts
   - Recommendation: 0.3-0.5 of ATR (Average True Range)

3. **Wait time**:
   - `MaxWaitMinutes` depends on timeframe
   - M5-M15: 15-30 minutes
   - H1: 60-120 minutes
   - If breakout didn't happen → cancel (flat market)

4. **Position size**:
   - No more than 1-2% of deposit at risk
   - Minimum lot (0.01) for testing

---

## Usage Examples

### Example 1: Conservative breakout on EURUSD

```csharp
var service = new MT5Service(account);

var conservativeBreakout = new PendingBreakoutOrchestrator(service)
{
    Symbol = "EURUSD",
    BreakoutDistancePoints = 20,  // Close to price
    StopLossPoints = 12,           // Tight SL
    TakeProfitPoints = 24,         // R:R = 1:2
    Volume = 0.01,
    MaxWaitMinutes = 20
};

var profit = await conservativeBreakout.ExecuteAsync();
Console.WriteLine($"Breakout completed: ${profit:F2}");
```

### Example 2: Aggressive breakout on GBPUSD

```csharp
var aggressiveBreakout = new PendingBreakoutOrchestrator(service)
{
    Symbol = "GBPUSD",
    BreakoutDistancePoints = 35,  // Further (volatile instrument)
    StopLossPoints = 20,
    TakeProfitPoints = 60,         // R:R = 1:3
    Volume = 0.02,
    MaxWaitMinutes = 40
};

var profit = await aggressiveBreakout.ExecuteAsync();
```

### Example 3: News strategy

```csharp
// Before news release (e.g., NFP)
var newsBreakout = new PendingBreakoutOrchestrator(service)
{
    Symbol = "EURUSD",
    BreakoutDistancePoints = 50,  // Wide (expecting strong movement)
    StopLossPoints = 30,
    TakeProfitPoints = 100,        // R:R = 1:3.3
    Volume = 0.01,
    MaxWaitMinutes = 10            // Short time (news soon)
};

var profit = await newsBreakout.ExecuteAsync();
```

---

## Error Handling

### Critical points

#### 1. BuyStop placement error (lines 59-63)

```csharp
if (buyStopResult.ReturnedCode != 10009)
{
    Console.WriteLine($"  ✗ BUY STOP failed: {buyStopResult.Comment}");
    return 0;  // Emergency exit, nothing to cancel (nothing placed)
}
```

**Possible causes**:

- Insufficient funds
- Market closed
- Incorrect price (too close to current)

#### 2. SellStop placement error (lines 78-84)

```csharp
if (sellStopResult.ReturnedCode != 10009)
{
    Console.WriteLine($"  ✗ SELL STOP failed: {sellStopResult.Comment}");
    Console.WriteLine("  Canceling BUY STOP...");
    await _service.CloseByTicket(buyStopResult.Order);  // ← IMPORTANT!
    return 0;
}
```

**Critically important**:

- If second order placement failed → **cancel first one**
- Otherwise hanging BuyStop will remain without pair
- Strategy requires BOTH orders simultaneously

#### 3. Exception in main block (lines 156-161)

```csharp
catch (Exception ex)
{
    Console.WriteLine($"\n  ✗ Error: {ex.Message}");
    // NO emergency closing - orders may remain!
    return 0;
}
```

**Improvement**:

```csharp
catch (Exception ex)
{
    Console.WriteLine($"\n  ✗ Error: {ex.Message}");

    // Attempt to cancel orders
    try
    {
        if (buyStopResult != null && buyStopResult.ReturnedCode == 10009)
            await _service.CloseByTicket(buyStopResult.Order);

        if (sellStopResult != null && sellStopResult.ReturnedCode == 10009)
            await _service.CloseByTicket(sellStopResult.Order);
    }
    catch { }

    return 0;
}
```

---

## Console Output

### Output example (upward breakout)

```
+============================================================+
|  PENDING BREAKOUT ORCHESTRATOR                            |
+============================================================+

  Starting balance: $10000.00
  Symbol: EURUSD
  Breakout distance: 25 pts
  Volume: 0.01 lots
  SL: 15 pts | TP: 30 pts

  Current: Bid=1.10000, Ask=1.10002

  Placing BUY STOP order...
  ✓ BUY STOP placed: #123456789

  Placing SELL STOP order...
  ✓ SELL STOP placed: #123456790

  ⏳ Waiting up to 30 minutes for breakout...

  🚀 BUY STOP EXECUTED! Upward breakout!
  Canceling opposite order #123456790...
  ✓ Canceled

  Final balance: $10003.00
  Profit/Loss: $3.00

+============================================================+
```

### Output example (timeout)

```
+============================================================+
|  PENDING BREAKOUT ORCHESTRATOR                            |
+============================================================+

  Starting balance: $10000.00
  Symbol: EURUSD
  Breakout distance: 25 pts
  Volume: 0.01 lots
  SL: 15 pts | TP: 30 pts

  Current: Bid=1.10000, Ask=1.10002

  Placing BUY STOP order...
  ✓ BUY STOP placed: #123456789

  Placing SELL STOP order...
  ✓ SELL STOP placed: #123456790

  ⏳ Waiting up to 30 minutes for breakout...

  ⏱ Timeout after 30 minutes - canceling both orders...
  ✓ Both canceled

  Final balance: $10000.00
  Profit/Loss: $0.00

+============================================================+
```

---

## When to Use Pending Breakout

### ✅ Suitable Conditions

- **Before important news**: NFP, central bank decisions, CPI
- **At key levels**: Support/resistance, round numbers
- **Consolidation**: Narrow range before breakout
- **Triangles/flags**: Technical breakout patterns
- **Asian session → London**: Expecting volatility

### ❌ Unsuitable Conditions

- **Strong trend**: One order triggers immediately, second is useless
- **High volatility**: Both orders may trigger
- **Wide spread**: Worsens R:R ratio
- **Flat market without direction**: Timeout, waste of time

---

## Optimization

### Possible improvements

1. **Dynamic distance based on ATR**:
   ```csharp
   var atr = await GetATR(Symbol, period: 14);
   BreakoutDistancePoints = (int)(atr * 0.4);  // 40% of ATR
   ```

2. **Trailing after breakout**:
   ```csharp
   if (executedOrder.HasValue)
   {
       // Wait for movement into profit
       await Task.Delay(5000);
       await _service.TrailStart(executedOrder.Value, trailPoints: 10);
   }
   ```

3. **Partial closing**:
   ```csharp
   // After breakout close 50% at first TP, trail the rest
   var positions = await _service.PositionsAsync(Symbol);
   if (positions.Count > 0)
   {
       await _service.ClosePartial(positions[0].Ticket, percent: 50);
       await _service.TrailStart(positions[0].Ticket, trailPoints: 15);
   }
   ```

4. **Time filter**:
   ```csharp
   var hour = DateTime.UtcNow.Hour;
   if (hour < 7 || hour > 16)  // Only London/NY sessions
   {
       Console.WriteLine("Outside trading hours");
       return 0;
   }
   ```

---

## Related Orchestrators

- **[GridTradingOrchestrator](GridTradingOrchestrator.md)**: For flat markets (opposite strategy).

- **[NewsStraddleOrchestrator](NewsStraddleOrchestrator.md)**: Specialization for news.

- **[SimpleScalpingOrchestrator](SimpleScalpingOrchestrator.md)**: Single trades after breakout.

---

## Summary

**PendingBreakoutOrchestrator** is an elegant OCO strategy for breakouts:

✅ **Pros**:

- No need to predict direction
- Excellent R:R ratio (1:2 and better)
- Automatic opposite order cancellation
- Safe error handling for placement

❌ **Cons**:

- May have many timeouts (flat market)
- False breakouts (whipsaw)
- Requires correct BreakoutDistancePoints distance

**Recommendation**:
 Use before important events (news, session openings) on instruments with predictable volatility. Combine with technical analysis to identify key levels.
