# GridTradingOrchestrator - Grid Trading

## Description

**GridTradingOrchestrator** is an orchestrator for grid trading that places multiple pending orders at equal intervals above and below the current price. The strategy is designed for flat (sideways) markets where price oscillates within a range.

**Principle**: A "grid" is created from Buy Limit orders below current price and Sell Limit orders above current price. When price moves down, buys trigger. When price moves up, sells trigger. When price returns to range, positions close with profit.

**File**: `Examples\Orchestrators\GridTradingOrchestrator.cs`

---

## Architecture

```
GRID TRADING ORCHESTRATOR
    ↓
MT5Service Instance
    ↓
  ┌─────┼─────┐
  ↓     ↓     ↓
BuyLimit SellLimit CloseAll
Points   Points   (emergency)
(below)  (above)
```

### Dependencies

- **MT5Service**: Service layer for MT5
- **MT5Sugar Extension Methods**: `BuyLimitPoints`, `SellLimitPoints`, `CloseAll`
- **mt5_term_api**: gRPC types (`OrderSendData`, `SymbolInfoTickData`)

---

## Configuration Parameters

| Parameter | Type | Default | Description |
|----------|-----|--------------|----------|
| `Symbol` | string | `"EURUSD"` | Trading instrument |
| `GridLevels` | int | `3` | Number of levels in each direction |
| `GridSpacingPoints` | int | `20` | Distance between levels in points |
| `VolumePerLevel` | double | `0.01` | Volume (lots) for each level |
| `StopLossPoints` | int | `50` | Stop loss in points for each order |
| `TakeProfitPoints` | int | `30` | Take profit in points for each order |
| `MaxRunMinutes` | int | `15` | Maximum running time in minutes |

### Configuration example

```csharp
var gridOrchestrator = new GridTradingOrchestrator(service)
{
    Symbol = "GBPUSD",
    GridLevels = 5,              // 5 Buy + 5 Sell = 10 orders
    GridSpacingPoints = 30,      // Every 30 points
    VolumePerLevel = 0.02,       // 0.02 lots per level
    StopLossPoints = 80,         // SL 80 points
    TakeProfitPoints = 40,       // TP 40 points
    MaxRunMinutes = 30           // Run for 30 minutes
};
```

---

## How to Run

You can execute this orchestrator using several command variations:

```bash
# Option 1: By number
dotnet run 9

# Option 2: By short name
dotnet run grid

# Option 3: By full name
dotnet run gridtrading
```

All three commands will launch the **GridTradingOrchestrator** with the default configuration or the settings you specify in the code.

---

## Algorithm

### Flowchart

```
START
  ↓
Get initial balance
  ↓
Get current price (Bid/Ask)
  ↓
LOOP: i from 1 to GridLevels
  → Calculate offsetPoints = -(i × GridSpacingPoints)
  → BuyLimitPoints(symbol, volume, offsetPoints, SL, TP)
     → If success → add to placedOrders list
  ↓
LOOP: i from 1 to GridLevels
  → Calculate offsetPoints = +(i × GridSpacingPoints)
  → SellLimitPoints(symbol, volume, offsetPoints, SL, TP)
     → If success → add to placedOrders list
  ↓
MONITORING (MaxRunMinutes minutes)
  → Every 5 seconds: display current profit
  ↓
Time expired → CloseAll(Symbol)
  ↓
Return profit
END
```

### Step-by-step description

#### 1. Initialization (lines 36-46)

```csharp
var initialBalance = await _service.GetBalanceAsync();
var tick = await _service.SymbolInfoTickAsync(Symbol);
```

**What happens**:
- Initial balance is saved for P/L calculation
- Current Bid/Ask price is obtained for visualization

#### 2. Placing Buy Limit levels (lines 50-73)

```csharp
for (int i = 1; i <= GridLevels; i++)
{
    var pointsBelow = -(i * GridSpacingPoints);  // NEGATIVE value!

    var result = await _service.BuyLimitPoints(
        symbol: Symbol,
        volume: VolumePerLevel,
        priceOffsetPoints: pointsBelow,  // For example: -20, -40, -60
        slPoints: StopLossPoints,
        tpPoints: TakeProfitPoints,
        comment: $"Grid-Buy-{i}"
    );
}
```

**Critically important**:

- `pointsBelow` has **NEGATIVE** value (`-20`, `-40`, `-60`)
- `BuyLimitPoints` uses `priceOffsetPoints` parameter which:
  - With negative value → places order **BELOW** current price
  - With positive value → places order **ABOVE** current price

**Example with GridLevels=3, GridSpacingPoints=20**:
```
Current Ask price: 1.10000

Level 1: BuyLimit @ 1.09980  (Ask - 20 pts)  → pointsBelow = -20
Level 2: BuyLimit @ 1.09960  (Ask - 40 pts)  → pointsBelow = -40
Level 3: BuyLimit @ 1.09940  (Ask - 60 pts)  → pointsBelow = -60
```

#### 3. Placing Sell Limit levels (lines 77-100)

```csharp
for (int i = 1; i <= GridLevels; i++)
{
    var pointsAbove = i * GridSpacingPoints;  // POSITIVE value!

    var result = await _service.SellLimitPoints(
        symbol: Symbol,
        volume: VolumePerLevel,
        priceOffsetPoints: pointsAbove,  // For example: +20, +40, +60
        slPoints: StopLossPoints,
        tpPoints: TakeProfitPoints,
        comment: $"Grid-Sell-{i}"
    );
}
```

**Example with GridLevels=3, GridSpacingPoints=20**:
```
Current Bid price: 1.10000

Level 1: SellLimit @ 1.10020  (Bid + 20 pts)  → pointsAbove = +20
Level 2: SellLimit @ 1.10040  (Bid + 40 pts)  → pointsAbove = +40
Level 3: SellLimit @ 1.10060  (Bid + 60 pts)  → pointsAbove = +60
```

#### 4. Monitoring (lines 105-114)

```csharp
var endTime = DateTime.UtcNow.AddMinutes(MaxRunMinutes);
while (DateTime.UtcNow < endTime && !ct.IsCancellationRequested)
{
    await Task.Delay(5000, ct);  // Every 5 seconds

    var currentBalance = await _service.GetBalanceAsync();
    var currentProfit = currentBalance - initialBalance;
    Console.WriteLine($"  Current P/L: ${currentProfit:F2}");
}
```

**What happens**:

- Every 5 seconds current balance is checked
- Current profit/loss is displayed
- Runs until `MaxRunMinutes` expires or cancellation via `CancellationToken`

#### 5. Closing all orders (lines 117-119)

```csharp
await _service.CloseAll(Symbol);
```

**What happens**:

- Closes **ALL** open positions for symbol
- Cancels **ALL** unfilled pending orders
- This guarantees no hanging orders after orchestrator completes

---

## Grid Visualization

### Scenario with GridLevels=3, GridSpacingPoints=20

```
1.10060 → SELL LIMIT Level 3  (TP: 1.10030, SL: 1.10110)
          +60 pts from current

1.10040 → SELL LIMIT Level 2  (TP: 1.10010, SL: 1.10090)
          +40 pts from current

1.10020 → SELL LIMIT Level 1  (TP: 1.09990, SL: 1.10070)
          +20 pts from current

1.10000 → CURRENT PRICE (Bid/Ask middle)

1.09980 → BUY LIMIT Level 1   (TP: 1.10010, SL: 1.09930)
          -20 pts from current

1.09960 → BUY LIMIT Level 2   (TP: 1.09990, SL: 1.09910)
          -40 pts from current

1.09940 → BUY LIMIT Level 3   (TP: 1.09970, SL: 1.09890)
          -60 pts from current
```

### Working scenario

**Scenario 1: Price falls and returns**

```
1. Price falls to 1.09970
   → BUY LIMIT Level 1 @ 1.09980 triggers
   → Opens position BUY 0.01 lots

2. Price continues falling to 1.09950
   → BUY LIMIT Level 2 @ 1.09960 triggers
   → Opens position BUY 0.01 lots
   → Total: 2 positions of 0.01 lots in BUY

3. Price returns to 1.10010
   → TP of first position (1.10010) triggers → profit +30 points
   → Second position in profit (+50 points, but TP not reached yet)

4. Price reaches 1.09990
   → TP of second position triggers → profit +30 points
```

**Scenario 2: Price rises and returns**

```
1. Price rises to 1.10030
   → SELL LIMIT Level 1 @ 1.10020 triggers
   → Opens position SELL 0.01 lots

2. Price falls to 1.09990
   → TP of position (1.09990) triggers → profit +30 points
```

---

## Used MT5Sugar Methods

### 1. BuyLimitPoints

```csharp
public static async Task<OrderSendData> BuyLimitPoints(
    this MT5Service service,
    string symbol,
    double volume,
    int priceOffsetPoints,  // NEGATIVE for below, POSITIVE for above
    int slPoints = 0,
    int tpPoints = 0,
    string comment = ""
)
```

**Purpose**: Places pending Buy Limit order with offset in points.

**Parameters in GridTradingOrchestrator**:

- `symbol`: Trading instrument (e.g., "EURUSD")
- `volume`: `VolumePerLevel` (e.g., 0.01)
- `priceOffsetPoints`: **NEGATIVE** value (e.g., -20, -40)
- `slPoints`: `StopLossPoints` (e.g., 50)
- `tpPoints`: `TakeProfitPoints` (e.g., 30)
- `comment`: "Grid-Buy-1", "Grid-Buy-2", ...

**Returns**: `OrderSendData` with `ReturnedCode` field:

- `10009` = success
- Other = error (see `Comment`)

### 2. SellLimitPoints

```csharp
public static async Task<OrderSendData> SellLimitPoints(
    this MT5Service service,
    string symbol,
    double volume,
    int priceOffsetPoints,  // POSITIVE for above, NEGATIVE for below
    int slPoints = 0,
    int tpPoints = 0,
    string comment = ""
)
```

**Purpose**: Places pending Sell Limit order with offset in points.

**Parameters in GridTradingOrchestrator**:

- `priceOffsetPoints`: **POSITIVE** value (e.g., +20, +40)

### 3. CloseAll

```csharp
public static async Task CloseAll(
    this MT5Service service,
    string symbol
)
```

**Purpose**: Closes all open positions and cancels all pending orders for symbol.

**Usage**:

- At end of orchestrator (line 118)
- In `catch` block for emergency close (line 136)

---

## Risk Management

### Maximum risk calculation

```
Maximum risk per level = VolumePerLevel × StopLossPoints × ValueOfPoint

For EURUSD (ValueOfPoint = $10 for 1.0 lot):
- VolumePerLevel = 0.01
- StopLossPoints = 50
- Risk per level = 0.01 × 50 × $10 = $5

Total risk (if all orders trigger):
- GridLevels = 3 Buy + 3 Sell = 6 orders
- Maximum risk = 6 × $5 = $30
```

### Recommendations

1. **SL/TP ratio**:
   - Default: SL=50, TP=30 (ratio 1.67:1)
   - This is **not** classic risk/reward ratio
   - Strategy relies on frequency of TP triggers in flat market

2. **Grid size**:
   - Start with small `GridLevels` values (3-5)
   - Increase as you understand market behavior

3. **Distance between levels**:
   - For volatile instruments: 30-50 points
   - For low volatility: 15-25 points
   - Consider ATR (Average True Range) of instrument

4. **Volume**:
   - Use minimum lots (0.01) for testing
   - Increase only after strategy confirmation

---

## Usage Examples

### Example 1: Conservative grid on EURUSD

```csharp
var service = new MT5Service(account);

var conservativeGrid = new GridTradingOrchestrator(service)
{
    Symbol = "EURUSD",
    GridLevels = 3,
    GridSpacingPoints = 25,
    VolumePerLevel = 0.01,
    StopLossPoints = 60,
    TakeProfitPoints = 35,
    MaxRunMinutes = 20
};

var profit = await conservativeGrid.ExecuteAsync();
Console.WriteLine($"Grid trading completed with result: ${profit:F2}");
```

### Example 2: Aggressive grid on GBPUSD

```csharp
var aggressiveGrid = new GridTradingOrchestrator(service)
{
    Symbol = "GBPUSD",
    GridLevels = 6,              // 6 × 2 = 12 orders
    GridSpacingPoints = 20,
    VolumePerLevel = 0.02,
    StopLossPoints = 80,
    TakeProfitPoints = 40,
    MaxRunMinutes = 30
};

var profit = await aggressiveGrid.ExecuteAsync();
```

### Example 3: Use in Preset

```csharp
public class GridPreset
{
    private readonly MT5Service _service;

    public async Task<double> ExecuteAsync()
    {
        // Phase 1: Small grid
        var smallGrid = new GridTradingOrchestrator(_service)
        {
            GridLevels = 3,
            GridSpacingPoints = 20,
            MaxRunMinutes = 10
        };
        var profit1 = await smallGrid.ExecuteAsync();

        // Phase 2: If profit > $10, run large grid
        if (profit1 > 10)
        {
            var largeGrid = new GridTradingOrchestrator(_service)
            {
                GridLevels = 5,
                GridSpacingPoints = 15,
                MaxRunMinutes = 15
            };
            var profit2 = await largeGrid.ExecuteAsync();
            return profit1 + profit2;
        }

        return profit1;
    }
}
```

---

## Error Handling

### try-catch block (lines 43-141)

```csharp
try
{
    // Main logic
}
catch (Exception ex)
{
    Console.WriteLine($"\n  ✗ Error: {ex.Message}");

    // EMERGENCY CLOSE
    try
    {
        await _service.CloseAll(Symbol);
    }
    catch { }  // Ignore errors during emergency close

    return 0;  // Return zero profit on error
}
```

### Possible errors

| Error | Cause | Solution |
|--------|---------|---------|
| `No connection` | No connection to MT5 | Check `MT5Account.ConnectAsync()` |
| `Market is closed` | Market closed | Work only during trading session |
| `Not enough money` | Insufficient funds | Reduce `VolumePerLevel` or `GridLevels` |
| `Invalid stops` | Incorrect SL/TP | Check minimum levels for symbol |
| `Freeze level` | Price too close | Increase `GridSpacingPoints` |

---

## Console Output

### Output example

```
+============================================================+
|  GRID TRADING ORCHESTRATOR                                |
+============================================================+

  Starting balance: $10000.00
  Symbol: EURUSD
  Grid: 3 levels × 20 pts
  Volume per level: 0.01 lots
  SL: 50 pts | TP: 30 pts

  Current: Bid=1.10000, Ask=1.10002

  Placing 3 BUY LIMIT levels...
    ✓ Level 1: #123456789 (-20 pts below)
    ✓ Level 2: #123456790 (-40 pts below)
    ✓ Level 3: #123456791 (-60 pts below)

  Placing 3 SELL LIMIT levels...
    ✓ Level 1: #123456792 (20 pts above)
    ✓ Level 2: #123456793 (40 pts above)
    ✓ Level 3: #123456794 (60 pts above)

  ✓ Grid placed: 6 pending orders
  ⏳ Running for 15 minutes...

  Current P/L: $0.00
  Current P/L: $3.50
  Current P/L: $7.80
  Current P/L: $12.30

  ⏱ Time expired - closing all remaining orders...
  ✓ All closed

  Final balance: $10012.30
  Total Profit/Loss: $12.30

+============================================================+
```

---

## When to Use Grid Trading

### ✅ Suitable Conditions

- **Flat market**: Price moves in sideways range
- **Low volatility**: Small price oscillations
- **Predictable support/resistance levels**
- **Asian session**: Often calmer
- **Forex weekends**: Cryptocurrencies in narrow range

### ❌ Unsuitable Conditions

- **Trending market**: Strong directional movement
- **High volatility**: News, volatile sessions
- **Level breakouts**: Risk of all SL triggering simultaneously
- **Low liquidity**: Wide spreads

---

## Optimization

### Possible improvements

1. **Dynamic grid distance**:
   ```csharp
   var atr = await GetATR(Symbol, period: 14);
   GridSpacingPoints = (int)(atr * 0.5);  // 50% of ATR
   ```

2. **Adaptive Volume**:
   ```csharp
   var balance = await _service.GetBalanceAsync();
   VolumePerLevel = balance * 0.0001;  // 0.01% of balance per level
   ```

3. **Limit number of open positions**:
   ```csharp
   var openPositions = await _service.PositionsCountAsync(Symbol);
   if (openPositions >= MaxPositions) return;  // Don't open new
   ```

4. **Trailing for profitable positions**:
   ```csharp
   if (currentProfit > TakeProfitPoints * 0.7)
   {
       await _service.TrailStart(ticket, trailPoints: 15);
   }
   ```

---

## Related Orchestrators

- **[SimpleScalpingOrchestrator](SimpleScalpingOrchestrator.md)**: Single fast trades
- **[PendingBreakoutOrchestrator](PendingBreakoutOrchestrator.md)**: Catches level breakouts
- **[QuickHedgeOrchestrator](QuickHedgeOrchestrator.md)**: Hedging on adverse movement

---

## Summary

**GridTradingOrchestrator** is a powerful tool for trading flat markets:

✅ **Pros**:

- Automation of placing multiple orders
- Catches price movement in both directions
- Profitable in sideways markets
- Ease of configuration and testing

❌ **Cons**:

- Dangerous in trending markets (all SL may trigger)
- Requires active monitoring
- High risk with incorrect settings

**Recommendation**: 
Use for short-term trading (15-30 minutes) on instruments with predictable behavior. Always test on demo account before real trading.
