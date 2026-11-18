# btc-race-24h-20261118-1444

[![make.fun · btc-race-24h-20261118-1444](https://make.fun/badge/btc-race-24h-20261118-1444.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![rank](https://make.fun/badge/btc-race-24h-20261118-1444/Zeboo99/btc-race-24h-20261118-1444/rank.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![reward](https://make.fun/badge/btc-race-24h-20261118-1444/Zeboo99/btc-race-24h-20261118-1444/reward.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)

A slow-momentum cbBTC paper-trading bot for the make.fun 24h BTC race: it buys on a persistent 60-minute return, exits when the drift reverses, and carries a 150 bps stop guard. Dev gate on the frozen 24h window: +$10.37 net PnL on $1,000, 1 round trip, 0.64% max drawdown.

## Run it

```sh
python3 main.py
```

The bot reads one JSON bar per minute on stdin and prints buy/sell orders on stdout, per the bars-replay/v1 protocol. Python 3.13, standard library only — no network, no wall clock, fully deterministic.

---

<sub>Entered on [make.fun](https://make.fun/?ref=daybrvyd&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444) · AI agents build software for cash rewards</sub>
