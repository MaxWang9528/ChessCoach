# ChessCoach

## Overview

This program uses a Bayesian network as a coaching tool for chess players. This focuses on the 8 players in the 2026 candidates tournament. Repertoires change depending on not only the player, but also what color that player is playing. Because of this, I've chosen to build one net per color, per player, for a total of 16 nets.

### Nodes

- **Player**: Who's games are we looking at
- **BigECO**: Chess openings are classified into categories called ECO codes. I've combined many similar openings into a broader code system called BigECO.
- **QueenTraded**: True if both player's queens are off the board
- **Balance**: True if material has been unequal for 4+ consecutive moves, excluding the last 10 moves.
- **CastleBalance**: True if both players castle to the same side.
- **WhiteStreak**: Positive, neutral, or negative depending on white's current winning streak
- **BlackStreak**: Positive, neutral, or negative depending on black's current winning streak
- **Result**: "1-0" if white wins, "1/2-1/2" if draw, and "0-1" if black wins.

### Structure

```
Player → bigECO
Player → QueenTraded
Player → Balance
Player → Castle
Player → Result

bigECO → QueenTraded
bigECO → Balance
bigECO → Castle

queenTraded → Result
Balance → Result
Castle → Result
whiteStreak → Result
blackStreak → Result
```

Result is a function of who you're playing, game dynamics (QueenTraded, Balance, CastleBalance), and psychology (WhiteStreak, BlackStreak).

## Code

**`main.py`**
Where the script begins running. Handles some file I/O, calls other functions to prepare data, and tests that require code are also in main.

**`modify_data.py`**
Manipulates data from `all_games_original.csv` and saves to `all_games.csv` (adding columns, removing entries, checking valid entries, etc)

**`net.py`**
Constructs the bayes net with pgmpy. Questions answered through query function

**`pgn_to_csv.py`**
Combines all games from original 8 files into one large csv file.

**`utils_pandas.py`**
Utilities to help with designing the bayes net.

**`questions.py`**
`Questions()` is a class with all 16 bayes nets as class variables. Every function answers a question a chess player might have pulling from whatever bayes nets are needed. Although I'm using pgmpy and not AIMA, the process is similar to HW3. Find probabilities given a list of variables and a dictionary of evidence.

`prep_data()` only needs to be called once. This creates `all_games.csv`. The code then creates a pandas dataframe which pgmpy needs (along with a list of edges) to construct a bayes net.

Python packages used: Numpy, Pandas, python-chess, Colorama, pgmpy
Chess data from 365chess.com



### Result

I computed one manually using enumeration from the CPDs. The result matches when I query with code.

## Finding Result from CPDs

### Query

$$P(\text{Result} = \text{1-0} \mid \text{BigECO} = \text{B20-B99},\ \text{WS} = \text{Neg},\ \text{BS} = \text{Pos})$$

Solve with enumeration example

### Numerator

$$\sum_{QT}\sum_{Bal}\sum_{CB} P(\text{Naka}) \cdot P(\text{B20-B99} \mid \text{Naka}) \cdot P(QT \mid \text{Naka}, \text{B20-B99}) \cdot P(Bal \mid \text{Naka}, \text{B20-B99}) \cdot P(CB \mid \text{Naka}, \text{B20-B99}) \cdot P(\text{Neg}) \cdot P(\text{Pos}) \cdot P(\text{1-0} \mid QT, Bal, CB, \text{Naka}, \text{Neg}, \text{Pos})$$

### Denominator

$$\sum_{R}\sum_{QT}\sum_{Bal}\sum_{CB} P(\text{Naka}) \cdot P(\text{B20-B99} \mid \text{Naka}) \cdot P(QT \mid \text{Naka}, \text{B20-B99}) \cdot P(Bal \mid \text{Naka}, \text{B20-B99}) \cdot P(CB \mid \text{Naka}, \text{B20-B99}) \cdot P(\text{Neg}) \cdot P(\text{Pos}) \cdot P(R \mid QT, Bal, CB, \text{Naka}, \text{Neg}, \text{Pos})$$

We find:

$$P(\text{1-0} \mid \text{evidence}) = \frac{\sum_i w_i \, P(\text{1-0} \mid i)}{\sum_i w_i}$$

Since $P(\text{1-0}) + P(\text{0-1}) + P(\tfrac{1}{2}\text{-}\tfrac{1}{2}) = 1$, the denominator simplifies to: $\sum_i w_i = 1$. and $P(\text{1-0} \mid \text{evidence}) = \sum_i w_i \, P(\text{1-0} \mid i)$.

### Weights

$$w_i = P(QT_i)\, P(Bal_i)\, P(CB_i)$$

| QT | Bal | CB | $w_i$ |
|:-:|:-:|:-:|---:|
| F | F | F | 0.1268 |
| F | F | T | 0.2180 |
| F | T | F | 0.0417 |
| F | T | T | 0.0717 |
| T | F | F | 0.1500 |
| T | F | T | 0.2578 |
| T | T | F | 0.0493 |
| T | T | T | 0.0848 |

### Result Probabilities

| QT | Bal | CB | P(1-0) |
|:-:|:-:|:-:|---:|
| F | F | F | 0.3750 |
| F | F | T | 0.3913 |
| F | T | F | 0.3333 |
| F | T | T | 0.4000 |
| T | F | F | 0.4000 |
| T | F | T | 0.4348 |
| T | T | F | 0.5000 |
| T | T | T | 0.2500 |

### Plugging in numbers

$$
\begin{aligned}
P(\text{1-0} \mid \text{evidence}) &= \sum_i w_i \, P(\text{1-0} \mid i) \\
&= 0.1268(0.3750) + 0.2180(0.3913) + 0.0417(0.3333) \\
&\quad + 0.0717(0.4000) + 0.1500(0.4000) + 0.2578(0.4348) \\
&\quad + 0.0493(0.5000) + 0.0848(0.2500) \\
&= 0.3934
\end{aligned}
$$

```
+-----------------+---------------+
| Result          |   phi(Result) |
+=================+===============+
| Result(0-1)     |        0.2442 |
+-----------------+---------------+
| Result(1-0)     |        0.3933 |
+-----------------+---------------+
| Result(1/2-1/2) |        0.3624 |
+-----------------+---------------+
```

## Results

Output in terminal:

```
I am playing Caruana with the black pieces. He is on a losing streak.
What is the probability I win if he plays the Spanish opening?
+-----------------+---------------+
| Result          |   phi(Result) |
+=================+===============+
| Result(0-1)     |        0.2666 |
+-----------------+---------------+
| Result(1-0)     |        0.4009 |
+-----------------+---------------+
| Result(1/2-1/2) |        0.3325 |
+-----------------+---------------+
0.4. Good chances, even though the spanish and Caruana are both solid
I only need a draw to win the tournament. I am playing Bluebaum with
the white pieces. What opening gives the highest P(win or draw)?
  A45-A46 Queen's pawn game: P(win or draw) = 0.9010
Iterate through all openings to find this answer. Found a really good option: Queen's pawn for a 90% chance
Giri is playing white with the English opening. He is on a losing streak.
Should I create an imbalance to throw him off even more?
  Balanced:
+-----------------+---------------+
| Result          |   phi(Result) |
+=================+===============+
| Result(0-1)     |        0.1039 |
+-----------------+---------------+
| Result(1-0)     |        0.1219 |
+-----------------+---------------+
| Result(1/2-1/2) |        0.7742 |
+-----------------+---------------+
  Unbalanced:
+-----------------+---------------+
| Result          |   phi(Result) |
+=================+===============+
| Result(0-1)     |        0.2174 |
+-----------------+---------------+
| Result(1-0)     |        0.3541 |
+-----------------+---------------+
| Result(1/2-1/2) |        0.4284 |
+-----------------+---------------+
Chance of a win (0-1) increases by 11%, but chance of a loss also increases by 23%! Use when a loss doesn't matter. Maybe if you need a win to win the tournament.

Nakamura is playing black and tries to draw by trading queens.
Castling is already balanced. He is on a losing streak.
Should we risk creating an imbalance to try to win, or is he good at drawing here?
  Balanced (let him draw):
+-----------------+---------------+
| Result          |   phi(Result) |
+=================+===============+
| Result(0-1)     |        0.2232 |
+-----------------+---------------+
| Result(1-0)     |        0.0610 |
+-----------------+---------------+
| Result(1/2-1/2) |        0.7158 |
+-----------------+---------------+
  Unbalanced (push for win):
+-----------------+---------------+
| Result          |   phi(Result) |
+=================+===============+
| Result(0-1)     |        0.3627 |
+-----------------+---------------+
| Result(1-0)     |        0.2673 |
+-----------------+---------------+
| Result(1/2-1/2) |        0.3700 |
+-----------------+---------------+
If we create an imbalance chance of winning (1-0) increase by 20% but chance of losing only increases by 14%. In contrast to the last question, we should create an imbalance.
Which player performs the worst when on a losing streak?
Compare P(loss) for each player when their streak is Negative.
  Caruana         P(loss|white,losing)=0.2638  P(loss|black,losing)=0.3586  avg=0.3112
  Praggnanandhaa  P(loss|white,losing)=0.2893  P(loss|black,losing)=0.2980  avg=0.2937
  Sindarov        P(loss|white,losing)=0.1776  P(loss|black,losing)=0.2949  avg=0.2363
  Esipenko        P(loss|white,losing)=0.1514  P(loss|black,losing)=0.3202  avg=0.2358
  Giri            P(loss|white,losing)=0.1872  P(loss|black,losing)=0.2755  avg=0.2313
  Nakamura        P(loss|white,losing)=0.1659  P(loss|black,losing)=0.2477  avg=0.2068
  Wei             P(loss|white,losing)=0.1624  P(loss|black,losing)=0.2156  avg=0.1890
  Bluebaum        P(loss|white,losing)=0.1318  P(loss|black,losing)=0.1742  avg=0.1530
Caruana is impacted the most psychologically when on a losing streak. This makes sense based on the first question
```

kely looking at historical data to analyze strengths and weaknesses of opponents, and then telling their players what playstyle they should go for at any point in the game.
