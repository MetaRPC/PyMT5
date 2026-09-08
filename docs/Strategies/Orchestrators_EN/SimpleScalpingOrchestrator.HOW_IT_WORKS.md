# HOW SimpleScalpingOrchestrator WORKS - Detailed Analysis

## 🎯 Document Purpose

Show **WHAT** the orchestrator consists of and **HOW EXACTLY** it works at the code, methods and data level. Special attention is paid to risk-sizing and automatic position size calculation.

---

## 📦 What the orchestrator is made of

### 1. Class structure (lines 13-27)

```csharp
public class SimpleScalpingOrchestrator
{
    
    // │  SINGLE DEPENDENCY                      
    // └─────────────────────────────────────────
    private readonly MT5Service _service;

    
    // │  6 CONFIGURABLE PARAMETERS              
    // └─────────────────────────────────────────
    public string Symbol { get; set; } = "EURUSD";
    public double RiskAmount { get; set; } = 20.0;      // $20 risk
    public int StopLossPoints { get; set; } = 10;
    public int TakeProfitPoints { get; set; } = 20;
    public bool IsBuy { get; set; } = true;
    public int MaxHoldSeconds { get; set; } = 60;       // 60 seconds

    
    // │  DEPENDENCY INJECTION                   
    // └─────────────────────────────────────────
    public SimpleScalpingOrchestrator(MT5Service service)
    {
        _service = service;  // ← Get MT5Service from outside
    }
}
```

### Dependency visualization

```

│        SimpleScalpingOrchestrator                          
│    
│  │  private readonly MT5Service _service                  
│  └───────────────────────────────────────────────────── 
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

### Phase 1: Initialization (lines 30-41)

```csharp
public async Task<double> ExecuteAsync(CancellationToken ct = default)
{
    
    // │  STEP 1: Output header                              
    // └─────────────────────────────────────────────────────
    Console.WriteLine("\n+============================================================+");
    Console.WriteLine("|  SIMPLE SCALPING ORCHESTRATOR                             |");
    Console.WriteLine("+============================================================+\n");

    
    // │  STEP 2: Get initial balance                        
    // └─────────────────────────────────────────────────────
    var initialBalance = await _service.GetBalanceAsync();

    
    // │  STEP 3: Output strategy parameters                 
    // └─────────────────────────────────────────────────────
    Console.WriteLine($"  Starting balance: ${initialBalance:F2}");
    Console.WriteLine($"  Symbol: {Symbol}");
    Console.WriteLine($"  Direction: {(IsBuy ? "BUY" : "SELL")}");
    Console.WriteLine($"  Risk: ${RiskAmount:F2}");
    Console.WriteLine($"  SL: {StopLossPoints} pts | TP: {TakeProfitPoints} pts");
    Console.WriteLine($"  Max hold: {MaxHoldSeconds}s\n");
}
```

---

### Phase 2: Opening position with risk-sizing (lines 43-77)

```csharp
try
{
    
    // │  Opening market position                            
    // └─────────────────────────────────────────────────────
    Console.WriteLine("  Opening position...");
    OrderSendData result;

    
    // │  DIRECTION CHOICE: BUY or SELL                      
    // └─────────────────────────────────────────────────────
    if (IsBuy)
    {
        // ═══════════════════════════════════════════════════
        // BUY: Use BuyMarketByRisk
        // ═══════════════════════════════════════════════════
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
        // ═══════════════════════════════════════════════════
        // SELL: Use SellMarketByRisk
        // ═══════════════════════════════════════════════════
        result = await _service.SellMarketByRisk(
            symbol: Symbol,
            stopPoints: StopLossPoints,
            riskMoney: RiskAmount,
            tpPoints: TakeProfitPoints,
            comment: "Scalper"
        );
    }

    
    // │  RESULT CHECK                                       
    // └─────────────────────────────────────────────────────
    if (result.ReturnedCode != 10009)  // 10009 = TRADE_RETCODE_DONE
    {
        Console.WriteLine($"  ✗ Order failed: {result.Comment}");
        return 0;  // ← EMERGENCY EXIT
    }

    Console.WriteLine($"  ✓ Position opened: #{result.Order}");
    Console.WriteLine($"  Volume: {result.Volume:F2} lots\n");
}
```

#### How BuyMarketByRisk() works internally

```csharp
// MT5Sugar.cs (extension method)
public static async Task<OrderSendData> BuyMarketByRisk(
    this MT5Service service,
    string symbol,
    int stopPoints,      // ← RECEIVES 10
    double riskMoney,    // ← RECEIVES $20
    int tpPoints = 0,
    string comment = ""
)
{
    
    // │  STEP 1: Get symbol information                     
    // └─────────────────────────────────────────────────────
    var symbolInfo = await service.SymbolInfoAsync(symbol);

    // EURUSD SymbolInfo:
    // - Point = 0.00001 (point size)
    // - Trade_Contract_Size = 100000 (contract size)
    // - Digits = 5 (decimal places)

   
    // │  STEP 2: Calculate value of ONE point              
    // │  for standard lot (1.0)                             
    // └─────────────────────────────────────────────────────
    double pointValue = symbolInfo.Trade_Contract_Size * symbolInfo.Point;

    // For EURUSD:
    // pointValue = 100000 × 0.00001 = 1.0

    // BUT! This is for base currency (EUR).
    // Need to convert to USD (account currency).

    
    // │  STEP 3: Get current price for conversion          
    // └─────────────────────────────────────────────────────
    var tick = await service.SymbolInfoTickAsync(symbol);
    double currentPrice = tick.Ask;  // For BUY use Ask

    // EURUSD @ 1.10000:
    // 1 point for 1.0 lot = 1 EUR = 1.10000 USD ≈ $1.10
    // (in reality MT5 uses special conversion tables)

    // For simplicity, for major pairs:
    // EURUSD, GBPUSD, AUDUSD, NZDUSD: ~$10 per point for 1.0 lot
    double pointValueUSD = 10.0;  // Simplified for example

    
    // │  STEP 4: KEY CALCULATION - Position size           
    // │                                                     
    // │  Risk-sizing formula:                               
    // │  Volume = RiskMoney / (StopPoints × PointValueUSD)  
    // └─────────────────────────────────────────────────────
    double volume = riskMoney / (stopPoints * pointValueUSD);

    // For our parameters:
    // riskMoney = $20
    // stopPoints = 10
    // pointValueUSD = $10
    //
    // volume = $20 / (10 × $10)
    //        = $20 / $100
    //        = 0.2 lots

    
    // │  STEP 5: Round to allowed volume step              
    // └─────────────────────────────────────────────────────
    double volumeStep = symbolInfo.Volume_Step;  // Usually 0.01
    volume = Math.Round(volume / volumeStep) * volumeStep;

    // 0.2 → round to 0.01 step → 0.20

    
    // │  STEP 6: Check minimum/maximum volume              
    // └─────────────────────────────────────────────────────
    double minVolume = symbolInfo.Volume_Min;  // Usually 0.01
    double maxVolume = symbolInfo.Volume_Max;  // Usually 100.0

    if (volume < minVolume) volume = minVolume;
    if (volume > maxVolume) volume = maxVolume;

    
    // │  STEP 7: Calculate SL and TP in absolute prices    
    // └─────────────────────────────────────────────────────
    double point = symbolInfo.Point;

    double sl = stopPoints > 0
        ? currentPrice - (stopPoints * point)  // For BUY: SL below
        : 0;

    double tp = tpPoints > 0
        ? currentPrice + (tpPoints * point)    // For BUY: TP above
        : 0;

    // For BUY @ 1.10000:
    // sl = 1.10000 - (10 × 0.00001) = 1.09990
    // tp = 1.10000 + (20 × 0.00001) = 1.10020

    
    // │  STEP 8: Call low-level BuyMarketAsync              
    // └─────────────────────────────────────────────────────
    return await service.BuyMarketAsync(
        symbol: symbol,      // "EURUSD"
        volume: volume,      // 0.20 (CALCULATED!)
        sl: sl,              // 1.09990
        tp: tp,              // 1.10020
        comment: comment     // "Scalper"
    );
}
```

#### Complete call chain for BuyMarketByRisk

```

│  USER CODE (SimpleScalpingOrchestrator.cs:51)                  
│  await _service.BuyMarketByRisk(                               
│      symbol: "EURUSD",                                         
│      stopPoints: 10,         ← SL POINTS                       
│      riskMoney: 20.0,        ← RISK IN DOLLARS                 
│      tpPoints: 20,           ← TP POINTS                       
│      comment: "Scalper"                                        
│  )                                                             
└──────────────────────────┬─────────────────────────────────────
                           │
                           ▼

   MT5Sugar.BuyMarketByRisk() (extension method)                 
│    
│  │ 1. SymbolInfoAsync() → get symbol info                    
│  │    - Point = 0.00001                                       
│  │    - Trade_Contract_Size = 100000                          
│  │    - Volume_Step = 0.01                                    
│  │                                                            
│  │ 2. SymbolInfoTickAsync() → get Ask price                  
│  │    - Ask = 1.10000                                         
│  │                                                            
│  │ 3. CALCULATE PointValue:                                   
│  │    pointValue = 100000 × 0.00001 = 1.0 (base currency)     
│  │    pointValueUSD ≈ $10 (for major pairs)                   
│  │                                                            
│  │ 4. KEY CALCULATION Volume:                                 
│  │    volume = riskMoney / (stopPoints × pointValueUSD)       
│  │           = $20 / (10 × $10)                               
│  │           = $20 / $100                                     
│  │           = 0.2 lots                                       
│  │                                                            
│  │ 5. Rounding: 0.2 → 0.20 (step 0.01)                       
│  │                                                            
│  │ 6. Calculate SL/TP:                                        
│  │    sl = 1.10000 - (10 × 0.00001) = 1.09990                 
│  │    tp = 1.10000 + (20 × 0.00001) = 1.10020                 
│  └──────────────────────────────────────────────────────────  
│  await service.BuyMarketAsync(                                 
│      symbol: "EURUSD",                                         
│      volume: 0.20,        ← AUTOMATICALLY CALCULATED!          
│      sl: 1.09990,                                              
│      tp: 1.10020,                                              
│      comment: "Scalper"                                        
│  )                                                             
└──────────────────────────┬─────────────────────────────────────
                           │
                           ▼

│  MT5Service.BuyMarketAsync()                                   
│  return await _account.BuyMarketAsync(...)                     
└──────────────────────────┬─────────────────────────────────────
                           │
                           ▼

│  MT5Account.BuyMarketAsync()                                   
│    
│  │ var request = new OrderSendRequest {                       
│  │     Symbol = "EURUSD",                                     
│  │     Volume = 0.20,        ← CALCULATED volume              
│  │     Type = ORDER_TYPE_BUY,  // = 0                        
│  │     Price = 0,  // Market order (no price specified)      
│  │     Sl = 1.09990,                                          
│  │     Tp = 1.10020,                                          
│  │     Comment = "Scalper"                                    
│  │ }                                                          
│  └──────────────────────────────────────────────────────────  
│  var response = await _client.OrderSendAsync(request);         
└──────────────────────────┬─────────────────────────────────────
                           │
                           ▼
                    
                    │  gRPC NETWORK
                    └──────┬───────
                           │
                           ▼
                  
                  │   MT5 Terminal     
                  │    
                  │  │ Opens          
                  │  │ BUY 0.20       
                  │  │ @ 1.10000      
                  │  │ SL: 1.09990    
                  │  │ TP: 1.10020    
                  │  │ Ticket:        
                  │  │  123456789     
                  │  └──────────────  
                  └────────┬───────────
                           │
                           ▼
                    
                    │  RESPONSE    
                    │ OrderSendData
                    │ {            
                    │   ReturnedCode
                    │   = 10009,   
                    │   Order =    
                    │   123456789, 
                    │   Volume =   
                    │   0.20        ← CALCULATED!
                    │   Price =    
                    │   1.10000    
                    │ }            
                    └──────┬───────
                           │
                           ▼
         
         │  BACK to SimpleScalpingOrchestrator 
         │  var result = OrderSendData {       
         │      ReturnedCode = 10009           
         │      Order = 123456789              
         │      Volume = 0.20                   ← See calculated volume!
         │  }                                  
         └─────────────────────────────────────
```

---

### Phase 3: Holding position (lines 79-81)

```csharp

// │  Wait MaxHoldSeconds (default 60 seconds)               
// └─────────────────────────────────────────────────────────
Console.WriteLine($"  ⏳ Holding for {MaxHoldSeconds}s...\n");

await Task.Delay(MaxHoldSeconds * 1000, ct);

// MaxHoldSeconds = 60 → Task.Delay(60000 ms) = 60 seconds
```

**What happens during these 60 seconds**:

```
T=0      Position opened BUY 0.20 @ 1.10000
         SL: 1.09990, TP: 1.10020
         │
         ├─► MT5 Terminal AUTOMATICALLY monitors price
         │
T=5s     Price: 1.10005 (+5 pts in profit)
T=10s    Price: 1.10012 (+12 pts in profit)
T=15s    Price: 1.10020 (TP REACHED!)
         │
         └─► MT5 Terminal AUTOMATICALLY closes position
             Profit: +20 pts × 0.20 = +$40

OR

T=5s     Price: 1.09995 (-5 pts in loss)
T=8s     Price: 1.09990 (SL REACHED!)
         │
         └─► MT5 Terminal AUTOMATICALLY closes position
             Loss: -10 pts × 0.20 = -$20 (exactly riskMoney!)

OR

T=60s    Price: 1.10008 (+8 pts in profit)
         Neither SL nor TP triggered
         → Proceed to next phase (status check)
```

---

### Phase 4: Checking position status (lines 83-104)

```csharp

// │  Get list of OPEN POSITIONS                             
// └─────────────────────────────────────────────────────────
var tickets = await _service.OpenedOrdersTicketsAsync();

bool stillOpen = false;


// │  Check: is our position in the list?                    
// └─────────────────────────────────────────────────────────
foreach (var ticket in tickets.OpenedPositionTickets)  // ← POSITIONS, not ORDERS!
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
    // ═══════════════════════════════════════════════════════
    // SCENARIO 1: Position NOT closed after 60 seconds
    // ═══════════════════════════════════════════════════════
    Console.WriteLine($"  Position still open after {MaxHoldSeconds}s - closing manually...");

    
    // │  Manual close at current market price           
    // └─────────────────────────────────────────────────
    await _service.CloseByTicket(result.Order);

    Console.WriteLine("  ✓ Position closed");
}
else
{
    // ═══════════════════════════════════════════════════════
    // SCENARIO 2: Position ALREADY closed
    // ═══════════════════════════════════════════════════════
    Console.WriteLine("  ✓ Position closed automatically (SL/TP hit)");
}
```

#### Visualization of status check

```text
AFTER Task.Delay(60 seconds):

MT5 Terminal state — SCENARIO 1 (position still open):
┌──────────────────┬────────────────────────────────────────┐
│  PENDING ORDERS  │  OPEN POSITIONS                        │
├──────────────────┼────────────────────────────────────────┤
│  (empty)         │  123456789: BUY 0.20 EURUSD @ 1.10000  │
│                  │             (in profit +8 pts)         │
└──────────────────┴────────────────────────────────────────┘

OpenedOrdersTicketsAsync() returns:
{
    OpenedOrdersTickets: [],
    OpenedPositionTickets: [123456789]  ← OUR POSITION FOUND!
}

foreach (var ticket in tickets.OpenedPositionTickets)
{
    // ticket = 123456789
    if (ticket == 123456789) stillOpen = true;  ← TRUE!
}

if (stillOpen)  ← TRUE → Manual close
{
    CloseByTicket(123456789);
}

─────────────────────────────────────────────────────────────

MT5 Terminal state — SCENARIO 2 (position already closed):
┌──────────────────┬────────────────────────────────────────┐
│  PENDING ORDERS  │  OPEN POSITIONS                        │
├──────────────────┼────────────────────────────────────────┤
│  (empty)         │  (empty)                               │
└──────────────────┴────────────────────────────────────────┘
                     ↑
                     Position closed (TP triggered @ T=15s)

OpenedOrdersTicketsAsync() returns:
{
    OpenedOrdersTickets: [],
    OpenedPositionTickets: []  ← POSITION NOT FOUND!
}

foreach (var ticket in tickets.OpenedPositionTickets)
{
    // Empty list → loop doesn't execute
}

stillOpen = false;  ← Remains false

if (stillOpen)  ← FALSE → Skip manual close
else
{
    Console.WriteLine("Position closed automatically (SL/TP hit)");
}
```

---

### Phase 5: Finalization (lines 106-113)

```csharp

// │  Get final balance                                      
// └─────────────────────────────────────────────────────────
var finalBalance = await _service.GetBalanceAsync();


// │  Calculate profit/loss                                  
// └─────────────────────────────────────────────────────────
var profit = finalBalance - initialBalance;

Console.WriteLine($"\n  Final balance: ${finalBalance:F2}");
Console.WriteLine($"  Profit/Loss: ${profit:F2}");


// │  Return profit as result of ExecuteAsync()              
// └─────────────────────────────────────────────────────────
return profit;
```

---

## 🎭 Complete Life Cycle (TP triggered scenario)

### Execution timeline

```
T=0      START ExecuteAsync()
         │
         ├─► GetBalanceAsync()           → $10000.00
         │
T=1s     ├─► BuyMarketByRisk(risk=$20, SL=10pts, TP=20pts)
         │   │
         │   ├─► SymbolInfoAsync("EURUSD")
         │   │   └─► Point=0.00001, ContractSize=100000
         │   │
         │   ├─► SymbolInfoTickAsync("EURUSD")
         │   │   └─► Ask=1.10000
         │   │
         │   ├─► CALCULATE Volume:
         │   │   volume = $20 / (10 × $10) = 0.2 lots
         │   │
         │   ├─► CALCULATE SL/TP:
         │   │   sl = 1.10000 - (10 × 0.00001) = 1.09990
         │   │   tp = 1.10000 + (20 × 0.00001) = 1.10020
         │   │
         │   └─► BuyMarketAsync(volume=0.2, sl=1.09990, tp=1.10020)
         │       └─► gRPC → MT5 Terminal
         │
T=2s     ├─► MT5 Terminal: Position opened!
         │   
         │   │ BUY 0.20 EURUSD @ 1.10000        
         │   │ SL: 1.09990                      
         │   │ TP: 1.10020                      
         │   │ Ticket: 123456789                
         │   └──────────────────────────────────
         │
         │   result.ReturnedCode = 10009 ✓
         │   result.Order = 123456789
         │   result.Volume = 0.20
         │
T=3s     ├─► Task.Delay(60000) START
         │   "Holding for 60s..."
         │
         │   MARKET: Price moves...
         │   1.10000 → 1.10005 → 1.10012 → 1.10020...
         │
T=15s    │   MT5 Terminal: Price reached 1.10020!
         │   TP TRIGGERED!
         │   
         │   │ Position closed automatically    
         │   │ Entry: 1.10000                   
         │   │ Exit:  1.10020                   
         │   │ Profit: +20 pts × 0.20 = +$40    
         │   └──────────────────────────────────
         │
         │   MT5 Terminal state:
         │   ┌──────────────────┬──────────────┐
         │   │ PENDING ORDERS   │ POSITIONS    │
         │   ├──────────────────┼──────────────┤
         │   │ (empty)          │ (empty)      │
         │   └──────────────────┴──────────────┘
         │
T=63s    ├─► Task.Delay(60000) END
         │
         ├─► OpenedOrdersTicketsAsync()
         │   └─► OpenedPositionTickets = []
         │
         ├─► foreach (var ticket in [])  ← Empty list
         │   └─► stillOpen = false
         │
         ├─► if (stillOpen) → FALSE
         │   else → "Position closed automatically (SL/TP hit)"
         │
T=64s    ├─► GetBalanceAsync()           → $10040.00
         ├─► profit = 10040.00 - 10000.00 = +$40.00
         │
         └─► RETURN profit = 40.00
```

---

## 📊 What the result is made of

### Profit calculation (TP triggered)

```
INITIAL BALANCE: $10000.00

POSITION:
- Direction: BUY
- Volume: 0.20 lots (AUTOMATICALLY CALCULATED!)
- Entry: 1.10000
- SL: 1.09990 (-10 pts)
- TP: 1.10020 (+20 pts)

TP TRIGGERED @ T=15s:
- Exit: 1.10020
- Pips: (1.10020 - 1.10000) / 0.00001 = 20 points

PROFIT CALCULATION:
- Profit = Pips × Point Value × Volume
- Point Value for EURUSD (0.20 lots) = 0.20 × $10 = $2 per point
- Profit = 20 × $2 = +$40

FINAL BALANCE: $10040.00
PROFIT = $40.00

return 40.00;
```

### Loss calculation (SL triggered)

```
SL TRIGGERED @ T=8s:
- Exit: 1.09990
- Pips: (1.09990 - 1.10000) / 0.00001 = -10 points

LOSS CALCULATION:
- Loss = -10 × $2 = -$20

FINAL BALANCE: $9980.00
PROFIT = -$20.00

CRITICALLY IMPORTANT:
Loss EXACTLY = riskMoney ($20)!
This proves correctness of Volume calculation through risk-sizing!
```

---

## 🧩 Components and their roles

### 1. SimpleScalpingOrchestrator

**Role**: Scalping strategy coordinator

**Tasks**:

- Stores parameters (Symbol, RiskAmount, SL, TP, IsBuy, MaxHoldSeconds)
- Manages life cycle
- Chooses direction (BUY/SELL)
- **Does NOT calculate Volume** (delegates to BuyMarketByRisk)
- Monitors holding time
- Checks position status
- Closes manually if needed
- Returns result

### 2. MT5Sugar (extension methods)

**Role**: **KEY** component for risk-sizing

**Tasks**:

- `BuyMarketByRisk()` - **AUTOMATICALLY calculates Volume**
- `SellMarketByRisk()` - **AUTOMATICALLY calculates Volume**
- `CloseByTicket()` - universal close

### 3. Risk-sizing formula

```

│  VOLUME CALCULATION FORMULA:                                
│                                                             
│  Volume = RiskMoney / (StopPoints × PointValueUSD)          
│                                                             
│  Where:                                                     
│  - RiskMoney: Maximum risk in dollars ($20)                 
│  - StopPoints: SL size in points (10)                    
│  - PointValueUSD: Value of 1 point for 1.0 lot ($10)        
└─────────────────────────────────────────────────────────────

EXAMPLES:

Example 1: Tight SL
  RiskMoney = $20
  StopPoints = 5  ← Very close SL
  PointValueUSD = $10

  Volume = $20 / (5 × $10) = $20 / $50 = 0.4 lots
  ↑ LARGER volume to compensate small SL!

Example 2: Wide SL
  RiskMoney = $20
  StopPoints = 20  ← Wide SL
  PointValueUSD = $10

  Volume = $20 / (20 × $10) = $20 / $200 = 0.1 lots
  ↑ SMALLER volume to keep risk at $20!

Example 3: High risk
  RiskMoney = $50  ← Increased risk
  StopPoints = 10
  PointValueUSD = $10

  Volume = $50 / (10 × $10) = $50 / $100 = 0.5 lots
  ↑ Proportionally larger volume!
```

---

## 🎯 Summary

**SimpleScalpingOrchestrator is made of**:

1. **1 dependency**: `MT5Service _service`
2. **6 parameters**: Symbol, **RiskAmount**, StopLossPoints, TakeProfitPoints, IsBuy, MaxHoldSeconds
3. **3 key methods**:
   - `BuyMarketByRisk` / `SellMarketByRisk` ← **AUTOMATIC Volume calculation!**
   - `OpenedOrdersTicketsAsync` ← Position status check
   - `CloseByTicket` ← Manual close

**Works through**:

- Market entry with automatic risk-sizing
- Holding position for MaxHoldSeconds seconds
- Check: did position close automatically (SL/TP)?
- Manual close if position still open

**Returns**:

- `double profit` - difference between final and initial balance

**Key insight**:

All the magic of the orchestrator is in **delegating Volume calculation to BuyMarketByRisk method**. Orchestrator only specifies RISK ($20), and position volume is calculated automatically based on StopLoss size. This ensures **constant risk** regardless of SL parameter changes!

**Success formula**:
```
CONSTANT RISK = RiskMoney
VARIABLE VOLUME = f(RiskMoney, StopPoints)

If SL increases → Volume decreases
If SL decreases → Volume increases
Risk ALWAYS remains = $20!
```
