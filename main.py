"""Slow-momentum cbBTC paper-trading bot for make.fun bars-replay/v1.

Strategy (long only, one position, full size):
  - Track the 60-minute return of the close: r = (c[t] - c[t-60]) / c[t-60].
  - Enter (buy 100% of cash) when r stays above +55 bps for 2 closes in a row.
    The persistence filter keeps the bot flat through 1-minute noise and only
    trades a real multi-hour drift.
  - Exit (sell everything) when r falls below -25 bps, i.e. the drift that
    carried the position has reversed; or sooner if the close falls 150 bps
    below the entry close (catastrophic guard for a sharp reversal).
  - Orders fill at the next bar's open, so every decision is made on closes
    the bot has already seen: no lookahead, no wall clock, no network.
  - Pure integer arithmetic on the wire scales; the run is fully
    deterministic: same bars in, same orders out.
"""

import json
import sys
from collections import deque

SYMBOL = "CBBTC"

# Strategy constants (basis points, bars).
LOOKBACK = 60          # minutes of close history the return is measured over
ENTER_BPS = 55         # 60-min return above this starts an entry count
ENTER_BARS = 2         # consecutive closes above ENTER_BPS to buy
EXIT_BPS = -25         # 60-min return below this sells the position
ENTRY_SL_BPS = 150      # catastrophic guard: sell if the close falls this
                        # far below the close the position was entered on
MAX_SLIPPAGE_BPS = 200  # cap on fill vs the close the order was decided on


def main():
    closes = deque(maxlen=LOOKBACK + 1)  # integer closes at price_scale
    entry_count = 0
    entry_close = None  # close of the bar the position was entered on
    order_no = 0
    price_scale = 5
    qty_scale = 8
    quote_scale = 6

    out = sys.stdout
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        msg = json.loads(line)
        mtype = msg.get("type")
        if mtype == "done":
            break
        if mtype == "hello":
            for s in msg.get("symbols", []):
                if s.get("symbol") == SYMBOL:
                    price_scale = int(s["price_scale"])
                    qty_scale = int(s["qty_scale"])
            quote_scale = int(msg["capital"]["quote_scale"])
            continue
        if mtype != "batch":
            continue

        seq = int(msg["seq"])
        bars = msg.get("bars") or []
        bar = None
        for b in bars:
            if b.get("symbol") == SYMBOL:
                bar = b
                break
        account = msg.get("account") or {}
        cash = int(account.get("cash_quote_units") or 0)
        position_qty = 0
        for p in account.get("positions") or []:
            if p.get("symbol") == SYMBOL:
                position_qty = int(p["qty"])
                break

        orders = []
        if bar is not None:
            close = int(bar["c"])
            closes.append(close)
            if len(closes) > LOOKBACK:
                prev = closes[0]
                # r in bps, compared exactly: r > ENTER_BPS means
                # (close - prev) * 10000 > ENTER_BPS * prev.
                diff_bps_num = (close - prev) * 10000
                if position_qty == 0:
                    if diff_bps_num > ENTER_BPS * prev:
                        entry_count += 1
                    else:
                        entry_count = 0
                    if entry_count >= ENTER_BARS and cash > 0:
                        order_no += 1
                        entry_close = close
                        orders.append({
                            "side": "buy",
                            "client_id": "buy-%d" % order_no,
                            "symbol": SYMBOL,
                            "notional_quote_units": str(cash),
                            "max_slippage_bps": MAX_SLIPPAGE_BPS,
                        })
                        entry_count = 0
                else:
                    entry_count = 0
                    trend_reversed = diff_bps_num < EXIT_BPS * prev
                    stopped_out = (
                        entry_close is not None
                        and close * 10000 <= entry_close * (10000 - ENTRY_SL_BPS)
                    )
                    if trend_reversed or stopped_out:
                        order_no += 1
                        entry_close = None
                        orders.append({
                            "side": "sell",
                            "client_id": "sell-%d" % order_no,
                            "symbol": SYMBOL,
                            "qty": str(position_qty),
                            "max_slippage_bps": MAX_SLIPPAGE_BPS,
                        })
        out.write(json.dumps({"type": "reply", "seq": seq, "orders": orders}) + "\n")
        out.flush()


if __name__ == "__main__":
    main()
