"""
Questions that can be answered by the Bayes net.
"""
from colorama import Fore, Style


class Questions:
    def __init__(self, naka_white, naka_black,
                 caru_white, caru_black,
                 giri_white, giri_black,
                 blue_white, blue_black,
                 sind_white, sind_black,
                 wei_white, wei_black,
                 esip_white, esip_black,
                 prag_white, prag_black):
        self.models = {
            ("Nakamura", "White"): naka_white,
            ("Nakamura", "Black"): naka_black,
            ("Caruana", "White"): caru_white,
            ("Caruana", "Black"): caru_black,
            ("Giri", "White"): giri_white,
            ("Giri", "Black"): giri_black,
            ("Bluebaum", "White"): blue_white,
            ("Bluebaum", "Black"): blue_black,
            ("Sindarov", "White"): sind_white,
            ("Sindarov", "Black"): sind_black,
            ("Wei", "White"): wei_white,
            ("Wei", "Black"): wei_black,
            ("Esipenko", "White"): esip_white,
            ("Esipenko", "Black"): esip_black,
            ("Praggnanandhaa", "White"): prag_white,
            ("Praggnanandhaa", "Black"): prag_black,
        }


    def caruana_spanish_losing_streak(self):
        """I am playing Caruana with the black pieces. He is on a losing streak.
        What is the probability I win if he plays the Spanish opening?"""
        print(f"{Fore.MAGENTA}{self.caruana_spanish_losing_streak.__doc__}{Style.RESET_ALL}")

        model = self.models[("Caruana", "White")]
        result = model.query(["Result"], evidence={
            "BigECO": "C60-C99 Ruy Lopez (Spanish opening)",
            "WhiteStreak": "Negative",
        })
        print(result)
        print(f"{Fore.GREEN}0.4. Good chances, even though the spanish and Caruana are both solid")


    def bluebaum_best_opening_for_draw_or_win(self):
        """I only need a draw to win the tournament. I am playing Bluebaum with
        the white pieces. What opening gives the highest P(win or draw)?"""
        print(f"{Fore.MAGENTA}{self.bluebaum_best_opening_for_draw_or_win.__doc__}{Style.RESET_ALL}")

        model = self.models[("Bluebaum", "White")]
        bigeco_cpd = model.model.get_cpds("BigECO")
        openings = bigeco_cpd.state_names["BigECO"]

        best = None
        best_prob = 0
        for opening in openings:
            result = model.query(["Result"], evidence={"BigECO": opening})
            states = result.state_names["Result"]
            prob = result.values[states.index("1-0")] + result.values[states.index("1/2-1/2")]
            if prob > best_prob:
                best_prob = prob
                best = opening
        print(f"  {best}: P(win or draw) = {best_prob:.4f}")
        print(f"{Fore.GREEN}Iterate through all openings to find this answer. Found a really good option: Queen's pawn for a 90% chance{Style.RESET_ALL}")


    def giri_losing_english(self):
        """Giri is playing white with the English opening. He is on a losing streak.
        Should I create an imbalance to throw him off even more?"""
        print(f"{Fore.MAGENTA}{self.giri_losing_english.__doc__}{Style.RESET_ALL}")

        model = self.models[("Giri", "White")]
        evidence = {
            "BigECO": "A10-A39 English opening",
            "WhiteStreak": "Negative",
        }

        print("  Balanced:")
        print(model.query(["Result"], evidence={**evidence, "Balanced": True}))
        print("  Unbalanced:")
        print(model.query(["Result"], evidence={**evidence, "Balanced": False}))
        print(f"{Fore.GREEN}Chance of a win (0-1) increases by 11%, but chance of a loss also increases by 23%! Use when a loss doesn't matter. Maybe if you need a win to win the tournament.{Style.RESET_ALL}")


    def sindarov_unbalance_or_draw(self):
        """Nakamura is playing black and tries to draw by trading queens.
        Castling is already balanced. He is on a losing streak.
        Should we risk creating an imbalance to try to win, or is he good at drawing here?"""
        print(f"{Fore.MAGENTA}{self.sindarov_unbalance_or_draw.__doc__}{Style.RESET_ALL}")

        model = self.models[("Nakamura", "Black")]
        base_evidence = {
            "QueenTraded": True,
            "CastleBalance": True,
            "BlackStreak": "Negative",
        }

        print("  Balanced (let him draw):")
        print(model.query(["Result"], evidence={**base_evidence, "Balanced": True}))
        print("  Unbalanced (push for win):")
        print(model.query(["Result"], evidence={**base_evidence, "Balanced": False}))
        print(f"{Fore.GREEN}If we create an imbalance chance of winning (1-0) increase by 20% but chance of losing only increases by 14%. In contrast to the last question, we should create an imbalance. {Style.RESET_ALL}")


    def worst_on_losing_streak(self):
        """Which player performs the worst when on a losing streak?
        Compare P(loss) for each player when their streak is Negative."""
        print(f"{Fore.MAGENTA}{self.worst_on_losing_streak.__doc__}{Style.RESET_ALL}")

        players = ["Nakamura", "Caruana", "Giri", "Bluebaum",
                   "Sindarov", "Wei", "Esipenko", "Praggnanandhaa"]

        results = []

        # remember check both black and white
        for player in players:
            # white: loss = 0-1, streak = WhiteStreak Negative
            white_model = self.models[(player, "White")]
            white_result = white_model.query(["Result"], evidence={"WhiteStreak": "Negative"})
            white_states = white_result.state_names["Result"]
            white_loss = white_result.values[white_states.index("0-1")]

            # black: loss = 1-0, streak = BlackStreak Negative
            black_model = self.models[(player, "Black")]
            black_result = black_model.query(["Result"], evidence={"BlackStreak": "Negative"})
            black_states = black_result.state_names["Result"]
            black_loss = black_result.values[black_states.index("1-0")]

            avg_loss = (white_loss + black_loss) / 2
            results.append((player, white_loss, black_loss, avg_loss))

        # some formatting
        results.sort(key=lambda x: x[3], reverse=True)
        for player, wl, bl, avg in results:
            print(f"  {player:<15} P(loss|white,losing)={wl:.4f}  P(loss|black,losing)={bl:.4f}  avg={avg:.4f}")

        print(f"{Fore.GREEN}Caruana is impacted the most psychologically when on a losing streak. This makes sense based on the first question{Style.RESET_ALL}")
