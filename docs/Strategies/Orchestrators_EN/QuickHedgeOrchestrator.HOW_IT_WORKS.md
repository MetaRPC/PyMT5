# HOW QuickHedgeOrchestrator WORKS - Detailed Analysis

## 🎯 Document Purpose

Show **WHAT** the orchestrator consists of and **HOW EXACTLY** it works at the code, methods and data level. Special attention is paid to the hedge trigger logic and the mathematics of loss locking.

---

## 📦 What the orchestrator is made of

### 1. Class structure (lines 13-27)

```csharp
public class QuickHedgeOrchestrator
{
    
    // │  SINGLE DEPENDENCY                      
    // └─────────────────────────────────────────
    private readonly MT5Service _service;

    
    // │  6 CONFIGURABLE PARAMETERS              
    // └─────────────────────────────────────────
    public string Symbol { get; set; } = "EURUSD";
    public double RiskAmount { get; set; } = 30.0;
    public int StopLossPoints { get; set; } = 25;
    public int TakeProfitPoints { get; set; } = 40;
    public bool OpenBuyFirst { get; set; } = true;
    public int HedgeTriggerPoints { get; set; } = 15;   // ← KEY parameter!

    public QuickHedgeOrchestrator(MT5Service service)
    {
        _service = service;
    }
}
```

### Dependency visualization

```

│          QuickHedgeOrchestrator                            
│    
│  │  private readonly MT5Service _service                  
│  └──────────────────────┬───────────────────────────────  
└─────────────────────────┼──────────────────────────────────
                          │
                          ▼
        
        │         MT5Service                  
        │    
        │  │  private MT5Account _account    
        │  └──────────────┬────────────────  
        └─────────────────┼────────────────────
                          │
                          ▼
                
                │      MT5Account         
                │    
                │  │  gRPC Client        
                │  └───────────────────  
                └─────────────────────────
                          │
                          ▼
                    [MT5 Terminal]
```

---

## 🔄 How ExecuteAsync() works - step by step

### Phase 1: Initialization (lines 35-40)

```csharp
public async Task<double> ExecuteAsync(CancellationToken ct = default)
{
    var initialBalance = await _service.GetBalanceAsync();

    Console.WriteLine($"  Starting balance: ${initialBalance:F2}");
    Console.WriteLine($"  Symbol: {Symbol}");
    Console.WriteLine($"  Initial direction: {(OpenBuyFirst ? "BUY" : "SELL")}");
    Console.WriteLine($"  Risk: ${RiskAmount:F2}");
    Console.WriteLine($"  Hedge trigger: {HedgeTriggerPoints} pts adverse");
}
```

### Phase 2: Opening primary position (lines 44-77)

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

### Phase 3: Monitoring for hedge trigger (lines 82-133)

This is **the most important part** of the orchestrator - the logic for determining adverse movement and placing the hedge.

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

### Phase 4: Holding and closing (lines 140-146)

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

## Summary

**QuickHedgeOrchestrator is made of**:

1. **1 dependency**: `MT5Service _service`
2. **6 parameters**: Symbol, RiskAmount, StopLossPoints, TakeProfitPoints, OpenBuyFirst, **HedgeTriggerPoints**
3. **Key logic**:

   - Primary position: with SL/TP, risk sizing
   - Hedge: **SAME Volume**, **WITHOUT SL/TP**
   - Monitoring every 2 seconds
   - Trigger: `isAdverse && priceMovementPoints >= HedgeTriggerPoints`

**Works through**:

- Opening primary position with BuyMarketByRisk
- Monitoring adverse movement (SymbolInfoTickAsync)
- Calculating movement in points (GetPointAsync)
- Placing opposite position on trigger
- Closing both positions simultaneously (CloseAll)

**Returns**:

- `double profit` - difference between final and initial balance

**Key insight**:

Hedge is **NOT** designed to make profit. Its purpose is to **FREEZE the loss** at the HedgeTriggerPoints level. After placing the hedge, the total P/L is frozen regardless of further price movement!

**Mathematical guarantee**:
```
Maximum loss after hedge = HedgeTriggerPoints × Volume × PointValue

Example:
15 pts × 0.12 lots × $10 = $18

Even if price falls -100 pts, loss stays at $18!
```
