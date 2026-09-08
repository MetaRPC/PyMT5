# SimpleScalpingOrchestrator - Fast Scalping

## Description

**SimpleScalpingOrchestrator** is an orchestrator for fast scalping with automatic position sizing based on risk. It opens a market position (BUY or SELL), holds it for maximum 60 seconds, then closes manually if SL/TP didn't trigger.

**Principle**: "Quick in, quick out" - fast market entry, tight stops (10 points SL), doubled profit (20 points TP), short holding time. Position size is calculated automatically based on specified risk in money.

**File**: `Examples\Orchestrators\SimpleScalpingOrchestrator.cs`

---

## Architecture

```
SIMPLE SCALPING ORCHESTRATOR
    ↓
MT5Service Instance
    ↓
  ┌─────┼─────┐
  ↓     ↓     ↓
BuyMarket SellMarket CloseBy
ByRisk    ByRisk     Ticket
(risk)    (risk)     (manual)
```

### Dependencies

- **MT5Service**: Service layer for MT5
- **MT5Sugar Extension Methods**: `BuyMarketByRisk`, `SellMarketByRisk`, `CloseByTicket`
- **mt5_term_api**: gRPC types (`OrderSendData`, `OpenedOrdersTicketsData`)

---

## Configuration Parameters

| Parameter | Type | Default | Description |
|----------|-----|--------------|----------|
| `Symbol` | string | `"EURUSD"` | Trading instrument |
| `RiskAmount` | double | `20.0` | Maximum risk in dollars ($20) |
| `StopLossPoints` | int | `10` | Stop loss in points |
| `TakeProfitPoints` | int | `20` | Take profit in points |
| `IsBuy` | bool | `true` | Direction: `true` = BUY, `false` = SELL |
| `MaxHoldSeconds` | int | `60` | Maximum position holding time (sec) |

### Configuration example

```csharp
var scalpingOrchestrator = new SimpleScalpingOrchestrator(service)
{
    Symbol = "GBPUSD",
    RiskAmount = 30.0,      // Risk $30 per trade
    StopLossPoints = 15,    // SL = 15 points
    TakeProfitPoints = 30,  // TP = 30 points (R:R = 1:2)
    IsBuy = false,          // SELL direction
    MaxHoldSeconds = 90     // Hold up to 90 seconds
};
```

---

## How to Run

You can execute this orchestrator using several command variations:

```bash
# Option 1: By number
dotnet run 13

# Option 2: By short name
dotnet run scalping

# Option 3: By full name
dotnet run simplescalping
```

All three commands will launch the **SimpleScalpingOrchestrator** with the default configuration or the settings you specify in the code.

---

## Algorithm

### Flowchart

```
START
  ↓
Get initial balance
  ↓
CONDITION: IsBuy == true?
  YES → BuyMarketByRisk(riskMoney, stopPoints, tpPoints)
  NO → SellMarketByRisk(riskMoney, stopPoints, tpPoints)
  ↓
If error → return 0
  ↓
Task.Delay(MaxHoldSeconds × 1000)  // Wait 60 sec
  ↓
OpenedOrdersTicketsAsync()
  ↓
CHECK: Position still open?
  YES → CloseByTicket(ticket)  // Manual close
  NO → "SL/TP already triggered"
  ↓
Get final balance
  ↓
Return profit
END
```

### Step-by-step description

#### 1. Initialization (lines 35-41)

```csharp
var initialBalance = await _service.GetBalanceAsync();

Console.WriteLine($"  Starting balance: ${initialBalance:F2}");
Console.WriteLine($"  Symbol: {Symbol}");
Console.WriteLine($"  Direction: {(IsBuy ? "BUY" : "SELL")}");
Console.WriteLine($"  Risk: ${RiskAmount:F2}");
Console.WriteLine($"  SL: {StopLossPoints} pts | TP: {TakeProfitPoints} pts");
Console.WriteLine($"  Max hold: {MaxHoldSeconds}s");
```

**What happens**:

- Initial balance is obtained to calculate P/L
- Strategy parameters are displayed

#### 2. Opening position with risk-sizing (lines 45-77)

```csharp
OrderSendData result;

if (IsBuy)
{
    
    // │  BUY: Use BuyMarketByRisk                           
    // │  Position size calculated AUTOMATICALLY             
    // └─────────────────────────────────────────────────────
    result = await _service.BuyMarketByRisk(
        symbol: Symbol,             // "EURUSD"
        stopPoints: StopLossPoints, // 10 points
        riskMoney: RiskAmount,      // $20
        tpPoints: TakeProfitPoints, // 20 points
        comment: "Scalper"
    );
}
else
{
    
    // │  SELL: Use SellMarketByRisk                         
    // └─────────────────────────────────────────────────────
    result = await _service.SellMarketByRisk(
        symbol: Symbol,
        stopPoints: StopLossPoints,
        riskMoney: RiskAmount,
        tpPoints: TakeProfitPoints,
        comment: "Scalper"
    );
}


// │  RESULT CHECK                                           
// └─────────────────────────────────────────────────────────
if (result.ReturnedCode != 10009)  // 10009 = TRADE_RETCODE_DONE
{
    Console.WriteLine($"  ✗ Order failed: {result.Comment}");
    return 0;  // Emergency exit
}

Console.WriteLine($"  ✓ Position opened: #{result.Order}");
Console.WriteLine($"  Volume: {result.Volume:F2} lots");
```

**Critically important**:

- Uses **BuyMarketByRisk** / **SellMarketByRisk** instead of fixed volume

- Method **automatically calculates** position size based on:

  - `riskMoney` = $20
  - `stopPoints` = 10 points
  - Current symbol price
- Result contains **calculated Volume** in `result.Volume` field

**Calculation example**:
```
Given:
- riskMoney = $20
- stopPoints = 10
- Symbol = EURUSD
- Point value for EURUSD (1.0 lot) = $10

Calculation:
riskPerPoint = riskMoney / stopPoints = $20 / 10 = $2 per point
Volume = riskPerPoint / pointValue = $2 / $10 = 0.2 lots

Result:
result.Volume = 0.20 lots
```

#### 3. Holding position (lines 79-81)

```csharp
Console.WriteLine($"  ⏳ Holding for {MaxHoldSeconds}s...\n");


// │  Wait MaxHoldSeconds (default 60 seconds)              
// │  SL or TP may trigger during this time                  
// └─────────────────────────────────────────────────────────
await Task.Delay(MaxHoldSeconds * 1000, ct);

// MaxHoldSeconds = 60 → Task.Delay(60000 ms) = 60 seconds
```

**What happens**:

- Orchestrator "sleeps" for 60 seconds
- During this time MT5 Terminal monitors the position
- If price reaches SL or TP → position automatically closes

#### 4. Checking position status (lines 83-104)

```csharp

// │  Get list of OPEN POSITIONS                             
// └─────────────────────────────────────────────────────────
var tickets = await _service.OpenedOrdersTicketsAsync();

bool stillOpen = false;


// │  Check: is our position in the list?                    
// └─────────────────────────────────────────────────────────
foreach (var ticket in tickets.OpenedPositionTickets)
{
    if (ticket == (long)result.Order)  // Compare ticket
    {
        stillOpen = true;
        break;
    }
}


// │  CONDITION: Position still open?                        
// └─────────────────────────────────────────────────────────
if (stillOpen)
{
    // SCENARIO 1: Position NOT closed after 60 seconds
    // SL/TP didn't trigger → close manually
    Console.WriteLine($"  Position still open after {MaxHoldSeconds}s - closing manually...");
    await _service.CloseByTicket(result.Order);
    Console.WriteLine("  ✓ Position closed");
}
else
{
    // SCENARIO 2: Position ALREADY closed
    // SL or TP triggered automatically
    Console.WriteLine("  ✓ Position closed automatically (SL/TP hit)");
}
```

**Key logic**:

- `OpenedOrdersTicketsAsync()` returns list of **OPEN positions**
- If our ticket is in the list → position still open → close manually
- If ticket not in the list → position already closed → do nothing

#### 5. Finalization (lines 106-113)

```csharp
var finalBalance = await _service.GetBalanceAsync();
var profit = finalBalance - initialBalance;

Console.WriteLine($"\n  Final balance: ${finalBalance:F2}");
Console.WriteLine($"  Profit/Loss: ${profit:F2}");

return profit;
```

---

## Strategy Visualization

### Scenario 1: TP triggered (profit)

```
T=0      BuyMarketByRisk(risk=$20, SL=10pts, TP=20pts)
         │
         ├─► Calculate Volume:
         │   riskPerPoint = $20 / 10 = $2
         │   Volume = $2 / $10 = 0.2 lots
         │
         ├─► Opened position BUY 0.2 lots @ 1.10000
         │   SL: 1.09990 (-10 pts)
         │   TP: 1.10020 (+20 pts)
         │
         │   Price moves:
         │   1.10000 → 1.10005 → 1.10012 → 1.10020...
         │
T=15s    ├─► Price reached 1.10020
         │   TP TRIGGERED!
         │   Position closed automatically
         │   Profit: 20 pts × 0.2 lots = +$40
         │
T=60s    ├─► Task.Delay finished
         │
         ├─► OpenedOrdersTicketsAsync()
         │   → ticket not found (position closed)
         │
         ├─► stillOpen = false
         │
         └─► "Position closed automatically (SL/TP hit)"

Result: Profit +$40
```

### Scenario 2: SL triggered (loss)

```
T=0      BuyMarketByRisk(risk=$20, SL=10pts, TP=20pts)
         │
         ├─► Opened position BUY 0.2 lots @ 1.10000
         │   SL: 1.09990 (-10 pts)
         │
         │   Price moves:
         │   1.10000 → 1.09998 → 1.09993 → 1.09990...
         │
T=8s     ├─► Price reached 1.09990
         │   SL TRIGGERED!
         │   Position closed automatically
         │   Loss: -10 pts × 0.2 lots = -$20
         │
T=60s    ├─► Task.Delay finished
         │
         ├─► OpenedOrdersTicketsAsync()
         │   → ticket not found (position closed)
         │
         ├─► stillOpen = false
         │
         └─► "Position closed automatically (SL/TP hit)"

Result: Loss -$20 (exactly riskMoney!)
```

### Scenario 3: Manual close (position in flat)

```
T=0      BuyMarketByRisk(risk=$20, SL=10pts, TP=20pts)
         │
         ├─► Opened position BUY 0.2 lots @ 1.10000
         │   SL: 1.09990
         │   TP: 1.10020
         │
         │   Price moves in range:
         │   1.10000 → 1.10003 → 1.09998 → 1.10005 → 1.10002...
         │
T=60s    ├─► Task.Delay finished
         │   Neither SL nor TP triggered
         │   Current price: 1.10005 (+5 pts in profit)
         │
         ├─► OpenedOrdersTicketsAsync()
         │   → ticket FOUND (position still open)
         │
         ├─► stillOpen = true
         │
         ├─► CloseByTicket(result.Order)
         │   → Close position at current price 1.10005
         │   Profit: +5 pts × 0.2 lots = +$10
         │
         └─► "Position still open after 60s - closing manually"

Result: Profit +$10 (less than TP, but still in profit)
```

---

## Used MT5Sugar Methods

### 1. BuyMarketByRisk

```csharp
public static async Task<OrderSendData> BuyMarketByRisk(
    this MT5Service service,
    string symbol,
    int stopPoints,      // SL in points
    double riskMoney,    // Risk in dollars
    int tpPoints = 0,
    string comment = ""
)
```

**Purpose**: Opens market BUY position with **automatic size calculation** based on risk.

**Calculation algorithm**:
```csharp
// 1. Get point value for symbol
var symbolInfo = await service.SymbolInfoAsync(symbol);
double pointValue = symbolInfo.Trade_Contract_Size * symbolInfo.Point;
// For EURUSD: 100000 × 0.00001 = $1 per point for 1.0 lot

// 2. Calculate risk per point
double riskPerPoint = riskMoney / stopPoints;
// $20 / 10 = $2 per point

// 3. Calculate Volume
double volume = riskPerPoint / pointValue;
// $2 / $1 = 2.0 lots (for 1.0 base lot)
// But for EURUSD with base $10 per point: $2 / $10 = 0.2 lots

// 4. Get current Ask price
var tick = await service.SymbolInfoTickAsync(symbol);
double askPrice = tick.Ask;

// 5. Calculate SL and TP
double sl = askPrice - (stopPoints × symbolInfo.Point);
double tp = tpPoints > 0 ? askPrice + (tpPoints × symbolInfo.Point) : 0;

// 6. Open position
return await service.BuyMarketAsync(symbol, volume, sl, tp, comment);
```

**Parameters in SimpleScalpingOrchestrator**:
- `symbol`: "EURUSD"
- `stopPoints`: 10 (SL = 10 points from entry price)
- `riskMoney`: $20 (maximum loss if SL triggers)
- `tpPoints`: 20 (TP = 20 points from entry price)
- `comment`: "Scalper"

**Returns**:
```csharp
OrderSendData {
    ReturnedCode = 10009,  // Success
    Order = 123456789,     // Position ticket
    Volume = 0.2,          // CALCULATED volume
    Price = 1.10000,       // Execution price
    Comment = "Request completed"
}
```

### 2. SellMarketByRisk

```csharp
public static async Task<OrderSendData> SellMarketByRisk(
    this MT5Service service,
    string symbol,
    int stopPoints,
    double riskMoney,
    int tpPoints = 0,
    string comment = ""
)
```

**Purpose**: Opens market SELL position with automatic size calculation.

**Differences from BuyMarketByRisk**:

- Uses **Bid** price instead of Ask
- SL **above** entry price (for SELL)
- TP **below** entry price (for SELL)

**SL/TP calculation for SELL**:
```csharp
double bidPrice = tick.Bid;
double sl = bidPrice + (stopPoints × point);  // ABOVE for SELL
double tp = tpPoints > 0 ? bidPrice - (tpPoints × point) : 0;  // BELOW for SELL
```

### 3. CloseByTicket

```csharp
public static async Task CloseByTicket(
    this MT5Service service,
    ulong ticket
)
```

**Purpose**: Closes position by ticket number.

**Usage in orchestrator**:

- Manual position close after `MaxHoldSeconds` expires (line 98)

### 4. OpenedOrdersTicketsAsync

```csharp
public async Task<OpenedOrdersTicketsData> OpenedOrdersTicketsAsync()
```

**Purpose**: Gets list of tickets for open positions and pending orders.

**Returns**:

```csharp
OpenedOrdersTicketsData {
    OpenedOrdersTickets: [list of pending orders],
    OpenedPositionTickets: [list of open positions]  ← USED IN ORCHESTRATOR
}
```

**Usage**:

- Check position presence in open list (lines 84-93)
- If ticket found → position still open
- If ticket not found → position closed (SL/TP triggered)

---

## Risk Management

### Main advantage: Constant risk

```
TRADITIONAL APPROACH (fixed Volume):
Position 1: 0.1 lots, SL=10pts → risk = 0.1 × 10 × $10 = $10
Position 2: 0.1 lots, SL=20pts → risk = 0.1 × 20 × $10 = $20
Position 3: 0.1 lots, SL=5pts  → risk = 0.1 × 5 × $10 = $5

PROBLEM: Risk changes depending on SL size!

───────────────────────────────────────────────────────────────

RISK-SIZING APPROACH (BuyMarketByRisk):
Position 1: riskMoney=$20, SL=10pts → Volume = $20/(10×$10) = 0.2 lots
Position 2: riskMoney=$20, SL=20pts → Volume = $20/(20×$10) = 0.1 lots
Position 3: riskMoney=$20, SL=5pts  → Volume = $20/(5×$10) = 0.4 lots

RESULT: Risk ALWAYS $20, regardless of SL size!
```

### R:R ratio calculation

```
Default:
- StopLossPoints = 10
- TakeProfitPoints = 20
- RiskAmount = $20

Risk/Reward Ratio:
Risk = $20 (if SL triggers)
Reward = $40 (if TP triggers)
R:R = 1:2 ✓

With 40% win rate:
- 6 trades: 4 losses (-$80) + 2 wins (+$80) = $0 (break-even)
- 7 trades: 4 losses (-$80) + 3 wins (+$120) = +$40 (profit)

Conclusion: 43% win rate sufficient for profitability!
```

### Recommendations

1. **Risk size**:
   - No more than 1-2% of deposit per trade
   - For $10000 deposit: recommended risk $100-200
   - Default $20 suitable for $1000-2000 deposit

2. **SL/TP ratio**:
   - Minimum 1:2 (as default)
   - Optimal 1:2.5 or 1:3
   - Never use 1:1 or worse

3. **Holding time**:
   - `MaxHoldSeconds = 60` for M1 scalping
   - `MaxHoldSeconds = 180` for M5 trading
   - `MaxHoldSeconds = 300` for M15 trading

4. **Direction selection**:
   - Use technical analysis to determine `IsBuy`
   - Don't trade against strong trend
   - Combine with indicators (MA, RSI, Stochastic)

---

## Usage Examples

### Example 1: Conservative scalping

```csharp
var service = new MT5Service(account);

var conservativeScalp = new SimpleScalpingOrchestrator(service)
{
    Symbol = "EURUSD",
    RiskAmount = 15.0,      // Low risk
    StopLossPoints = 8,     // Very tight SL
    TakeProfitPoints = 20,  // R:R = 1:2.5
    IsBuy = true,
    MaxHoldSeconds = 45     // Short time
};

var profit = await conservativeScalp.ExecuteAsync();
Console.WriteLine($"Scalping completed: ${profit:F2}");
```

### Example 2: Aggressive scalping

```csharp
var aggressiveScalp = new SimpleScalpingOrchestrator(service)
{
    Symbol = "GBPUSD",
    RiskAmount = 50.0,      // High risk
    StopLossPoints = 12,
    TakeProfitPoints = 36,  // R:R = 1:3
    IsBuy = false,          // SELL
    MaxHoldSeconds = 90
};

var profit = await aggressiveScalp.ExecuteAsync();
```

### Example 3: Use in loop (multiple trades)

```csharp
var totalProfit = 0.0;
var trades = 0;

for (int i = 0; i < 10; i++)
{
    // Determine direction (e.g., by indicator)
    bool direction = await GetTrendDirection("EURUSD");

    var scalper = new SimpleScalpingOrchestrator(service)
    {
        Symbol = "EURUSD",
        RiskAmount = 20.0,
        StopLossPoints = 10,
        TakeProfitPoints = 20,
        IsBuy = direction,
        MaxHoldSeconds = 60
    };

    var profit = await scalper.ExecuteAsync();
    totalProfit += profit;
    trades++;

    Console.WriteLine($"Trade {trades}: ${profit:F2}");

    // Pause between trades
    await Task.Delay(30000);  // 30 seconds
}

Console.WriteLine($"\nTotal: {trades} trades, ${totalProfit:F2} profit");
```

### Example 4: Adaptive risk based on balance

```csharp
var balance = await service.GetBalanceAsync();
var dynamicRisk = balance * 0.01;  // 1% of balance

var adaptiveScalp = new SimpleScalpingOrchestrator(service)
{
    Symbol = "EURUSD",
    RiskAmount = dynamicRisk,  // Automatically adapts to balance
    StopLossPoints = 10,
    TakeProfitPoints = 20,
    IsBuy = true,
    MaxHoldSeconds = 60
};

var profit = await adaptiveScalp.ExecuteAsync();
```

---

## Error Handling

### Position opening error (lines 70-74)

```csharp
if (result.ReturnedCode != 10009)
{
    Console.WriteLine($"  ✗ Order failed: {result.Comment}");
    return 0;  // Emergency exit
}
```

**Possible causes**:

- Insufficient funds (even after Volume calculation)
- Market closed
- Incorrect symbol
- Minimum/maximum lot exceeded

### Exception in main block (lines 115-120)

```csharp
catch (Exception ex)
{
    Console.WriteLine($"\n  ✗ Error: {ex.Message}");
    return 0;
}
```

**Problem**: No emergency position close!

**Improvement**:
```csharp
catch (Exception ex)
{
    Console.WriteLine($"\n  ✗ Error: {ex.Message}");

    // Attempt to close position on error
    if (result != null && result.ReturnedCode == 10009)
    {
        try
        {
            await _service.CloseByTicket(result.Order);
            Console.WriteLine("  Emergency close executed");
        }
        catch { }
    }

    return 0;
}
```

---

## Console Output

### Output example (TP triggered)

```
+============================================================+
|  SIMPLE SCALPING ORCHESTRATOR                             |
+============================================================+

  Starting balance: $10000.00
  Symbol: EURUSD
  Direction: BUY
  Risk: $20.00
  SL: 10 pts | TP: 20 pts
  Max hold: 60s

  Opening position...
  ✓ Position opened: #123456789
  Volume: 0.20 lots

  ⏳ Holding for 60s...

  ✓ Position closed automatically (SL/TP hit)

  Final balance: $10040.00
  Profit/Loss: $40.00

+============================================================+
```

### Output example (manual close)

```
+============================================================+
|  SIMPLE SCALPING ORCHESTRATOR                             |
+============================================================+

  Starting balance: $10000.00
  Symbol: EURUSD
  Direction: SELL
  Risk: $20.00
  SL: 10 pts | TP: 20 pts
  Max hold: 60s

  Opening position...
  ✓ Position opened: #123456790
  Volume: 0.20 lots

  ⏳ Holding for 60s...

  Position still open after 60s - closing manually...
  ✓ Position closed

  Final balance: $10010.00
  Profit/Loss: $10.00

+============================================================+
```

---

## When to Use Simple Scalping

### ✅ Suitable Conditions

- **M1-M5 timeframes**: Very short-term trading
- **High liquidity**: London/New York sessions
- **Narrow spreads**: EURUSD, GBPUSD, USDJPY in active hours
- **Clear signals**: Level breakout, support/resistance bounce
- **Low volatility**: Avoid news

### ❌ Unsuitable Conditions

- **Asian session**: Low volatility, wide spreads
- **Before/after news**: Unpredictable movements
- **Exotic pairs**: High commissions, low liquidity
- **H1+ timeframes**: Too long holding for scalping

---

## Optimization

### Possible improvements

1. **Dynamic SL based on ATR**:
   ```csharp
   var atr = await GetATR(Symbol, period: 14);
   StopLossPoints = (int)(atr * 0.5);  // 50% of ATR
   TakeProfitPoints = StopLossPoints * 2;  // Preserve R:R 1:2
   ```

2. **Partial closing**:
   ```csharp
   // After reaching 50% of TP
   await Task.Delay(30000);  // 30 sec
   var positions = await _service.PositionsAsync(Symbol);
   if (positions.Count > 0)
   {
       await _service.ClosePartial(positions[0].Ticket, percent: 50);
       await _service.MoveToBreakeven(positions[0].Ticket);
   }
   ```

3. **Trailing stop**:
   ```csharp
   await Task.Delay(30000);
   // If position in profit > 10 points
   await _service.TrailStart(result.Order, trailPoints: 5);
   ```

4. **Time filter**:
   ```csharp
   var hour = DateTime.UtcNow.Hour;
   if (hour >= 7 && hour <= 16)  // London/NY sessions
   {
       await ExecuteAsync();
   }
   ```

---

## Related Orchestrators

- **[GridTradingOrchestrator](GridTradingOrchestrator.md)**: Multiple levels instead of single trade.
- **[PendingBreakoutOrchestrator](PendingBreakoutOrchestrator.md)**: Pending orders instead of market entry.
- **[QuickHedgeOrchestrator](QuickHedgeOrchestrator.md)**: Adds hedging on adverse movement.

---

## Summary

**SimpleScalpingOrchestrator** is a basic fast scalping strategy with risk management:

✅ **Pros**:

- **Automatic risk-sizing** - position size always matches specified risk
- Excellent R:R ratio (1:2 by default)
- Ease of use and configuration
- Short holding time (minimize exposure)
- Suitable for automation

❌ **Cons**:

- Requires active market (narrow spreads)
- High frequency trades → commission accumulation
- Dependence on entry accuracy
- Not suitable for trending markets (better to use trailing)

**Recommendation**: 
Use as a basic building block for more complex strategies. Combine with technical analysis for direction selection. Always test on demo account before real trading.
