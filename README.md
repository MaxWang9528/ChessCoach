# ChessCoach

A Bayesian network that coaches a player preparing for the **2026 Candidates Tournament**. The network is learned from each opponent's game history. It answers practical questions such as "what are my chances against this player in this opening?" or "should I make the position unbalanced or let it stay quiet?"

There are 16 networks: one per opponent per color. The eight opponents are Nakamura, Caruana, Giri, Bluebaum, Sindarov, Wei Yi, Esipenko and Praggnanandhaa.

---

## Data

| | |
|---|---|
| Source | 8 PGN files, one per player (`data/*.pgn`) |
| Raw games | 16,337 (`data/all_games_original.csv`) |
| Removed | 221 Chess960 games, 28 games with no round number |
| Clean games | **16,088** (`data/all_games.csv`) |
| Date range | 1997 – March 2026 |

Overall results: 44.6% draws, 32.6% White wins, 22.8% Black wins.

### Per-player record (all games in the dataset)

| Player | Games | Win% | Draw% | Loss% |
|---|---:|---:|---:|---:|
| Sindarov | 930 | **42.2** | 38.5 | 19.4 |
| Nakamura | 3,857 | 39.1 | 43.5 | 17.4 |
| Esipenko | 1,468 | 37.0 | 44.8 | 18.3 |
| Wei Yi | 1,382 | 37.0 | 46.2 | 16.9 |
| Caruana | 3,647 | 36.6 | 41.4 | 22.0 |
| Bluebaum | 1,496 | 36.5 | 45.5 | 17.9 |
| Praggnanandhaa | 1,336 | 35.8 | 41.1 | **23.1** |
| Giri | 3,018 | 27.1 | **54.5** | 18.4 |

Giri draws the most by a wide margin. Sindarov wins the most, though from the smallest sample.

### Engineered features

Each game is replayed with `python-chess` (`modify_data.py`) to compute these features:

| Variable | Meaning | Share of games |
|---|---|---|
| `BigECO` | ECO code grouped into ~65 opening families (e.g. B20–B99 Sicilian) | — |
| `QueenTraded` | Both queens are off the board at some point | 57.9% |
| `Balanced` | Material was never unequal for 4+ consecutive plies (the last 10 plies are ignored) | 24.7% |
| `CastleBalance` | Both sides castled to the same side | 73.5% |
| `WhiteStreak` / `BlackStreak` | Each player's streak going into the game: `Positive`, `Negative` or `Neutral` | — |
| `Result` | `1-0`, `0-1`, `1/2-1/2` | — |

---

## Network structure

```
Player ──► BigECO ──► QueenTraded ──┐
   │          ├─────► Balanced ─────┼──► Result ◄── WhiteStreak
   │          └─────► CastleBalance ┘            ◄── BlackStreak
   └──► (QueenTraded, Balanced, CastleBalance, Result)
```

The networks are built with `pgmpy` (`net.py`). The CPDs are fitted by maximum likelihood, and queries are answered by variable elimination. The full CPD tables for every network are in `data/cpd_<player>_<color>.txt`.

A hand-worked enumeration of one query is in `enumeration.tex` and `data/enumeration_example.txt`. The query is P(Result = 1-0 | Nakamura is White, Sicilian, White on a losing streak, Black on a winning streak). It shows how the hidden variables QT, Bal and CB are summed out.

---

## Findings

All numbers below come from running `main.py` (`questions.py`). *n* is the number of games that match the evidence.

### 1. Caruana as White, on a losing streak, plays the Spanish (I'm Black)

| Result | P |
|---|---:|
| 1-0 (Caruana wins) | 0.401 |
| 1/2-1/2 | 0.333 |
| 0-1 (**I win**) | **0.267** |

*n = 72.* My chance of winning is about **27%**. Even on a losing streak, Caruana is still the favourite in his main opening.

> ⚠️ The comment in `questions.py` reads 0.40 as "my" win probability. That number is the `1-0` entry, which is Caruana's win. The correct answer for Black is 0.267.

### 2. I need only a draw against Bluebaum and I'm White. Which opening is best?

The code reports **A45–A46 Queen's pawn game, P(win or draw) = 0.90**. That query uses the *Bluebaum-as-White* network, though, and it sums `1-0 + draw`. That gives P(*Bluebaum* doesn't lose), not P(*I* don't lose). The sample is also only 11 games.

The same search on the correct network (Bluebaum as **Black**, summing `1-0 + draw`) gives:

| Opening (≥ 20 games) | n | P(I win or draw) |
|---|---:|---:|
| C42–C43 Petrov's defence | 27 | **0.743** |
| D02 Queen's pawn game | 22 | 0.712 |
| D30–D42 Queen's Gambit Declined | 89 | 0.700 |
| A10–A39 English | 66 | 0.695 |
| A04–A09 Réti | 58 | 0.691 |

Openings with fewer games score higher (0.92 for the Neo-Grünfeld, n = 4), but those numbers are noise. The **Queen's Gambit Declined** is the most reliable choice: it scores about 70% on a large sample.

### 3. Giri as White, on a losing streak, plays the English. Should I make the position unbalanced?

| | Giri wins (1-0) | Draw | I win (0-1) |
|---|---:|---:|---:|
| Balanced | 0.122 | **0.774** | 0.104 |
| Unbalanced | 0.354 | 0.428 | **0.217** |
| Change | **+23 pp** | −35 pp | +11 pp |

*n = 31 (9 balanced, 22 unbalanced).* Making the position unbalanced roughly doubles my winning chances, but it nearly triples Giri's. **Do it only when a draw is as bad as a loss**, for example when I must win to take first place.

### 4. Nakamura as Black, on a losing streak, has traded queens and castled the same side as me. Should I push?

| | I win (1-0) | Draw | Nakamura wins (0-1) |
|---|---:|---:|---:|
| Balanced | 0.061 | **0.716** | 0.223 |
| Unbalanced | **0.267** | 0.370 | 0.363 |
| Change | **+21 pp** | −35 pp | +14 pp |

*n = 141 (25 balanced, 116 unbalanced).* Here making the position unbalanced is worth it. My winning chances rise more than my losing chances, so **push for the imbalance**. This is the opposite of the Giri case.

### 5. Who handles a losing streak worst?

P(loss | the player is on a losing streak), for each color:

| Player | as White | as Black | Average |
|---|---:|---:|---:|
| **Caruana** | 0.264 | 0.359 | **0.311** |
| Praggnanandhaa | 0.289 | 0.298 | 0.294 |
| Sindarov | 0.178 | 0.295 | 0.236 |
| Esipenko | 0.151 | 0.320 | 0.236 |
| Giri | 0.187 | 0.276 | 0.231 |
| Nakamura | 0.166 | 0.248 | 0.207 |
| Wei Yi | 0.162 | 0.216 | 0.189 |
| **Bluebaum** | 0.132 | 0.174 | **0.153** |

**Caruana** is hit hardest by a losing streak. His loss rate goes from 22% overall to about 31%. **Bluebaum** is the most resilient: he loses *less* often after a loss (15%) than his overall rate (18%). Praggnanandhaa already has the highest base loss rate, and it rises further.

> Note: `questions.py` says this result "makes sense based on the first question." Once question 1 is read correctly, Caruana is still the favourite in that position. The two findings are consistent with each other, but question 1 doesn't confirm this one.

---

## Limitations

- **Sparse CPDs.** `Result` has six parents, and the dataset has 65 opening families and 3 streak states. Many parent combinations have only a handful of games, and some have none. Maximum likelihood estimation gives 0% or 100% probabilities for these, as in rows 7–8 of the enumeration example. Smoothing the counts (e.g. a Bayesian estimator with a BDeu prior) would make these estimates more reliable.
- **Streaks are computed within each player's own file.** The streak is built from the games in the dataset, ordered by date and round. Missing games and date gaps across tournaments are not accounted for.
- **"Balanced" is a material heuristic.** It counts material only and does not look at the position, so a positional imbalance with equal material counts as balanced.
- **Opponent strength is not modelled.** A loss to a 2800 player and a loss to a 2500 player look the same.

---

## Running

```bash
pip install pandas python-chess colorama pgmpy
python main.py          # builds the 16 networks and prints the 5 questions
```

To rebuild the CSVs from the PGNs, uncomment `prep_data()` in `main.py`. This overwrites `data/all_games*.csv`.

> `net.py` passes `estimator=MaximumLikelihoodEstimator` as a class. Recent pgmpy releases reject this and require an instance (`estimator=MLE()`). Either pin an older pgmpy or change that line.

### Files

| File | Purpose |
|---|---|
| `pgn_to_csv.py` | Combines the PGNs into `all_games_original.csv` |
| `modify_data.py` | Cleans the data and adds the engineered features |
| `utils_pandas.py` | Descriptive statistics |
| `net.py` | Bayes net definition, fitting, querying and CPD export |
| `questions.py` | The five coaching questions |
| `main.py` | Entry point |
| `probability4e.py`, `utils4e.py` | AIMA reference code |
