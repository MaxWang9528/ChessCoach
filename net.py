"""
Bayesian Network construction and inference using pgmpy.
One net per opponent per color.
"""

from pgmpy.models import DiscreteBayesianNetwork as BayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.inference import VariableElimination
import pandas as pd

EDGES = [
    ("Player", "BigECO"),
    ("Player", "QueenTraded"),
    ("Player", "Balanced"),
    ("Player", "CastleBalance"),
    ("Player", "Result"),
    ("BigECO", "QueenTraded"),
    ("BigECO", "Balanced"),
    ("BigECO", "CastleBalance"),
    ("QueenTraded", "Result"),
    ("Balanced", "Result"),
    ("CastleBalance", "Result"),
    ("WhiteStreak", "Result"),
    ("BlackStreak", "Result"),
]


class Net:
    def __init__(self, df, player, color):
        """
        Build and fit a Bayes net for a given player and color.

        :param df: full dataframe
        :param player: the opponent's name
        :param color: "White" or "Black" — the color the opponent is playing
        """
        self.player = player
        self.color = color

        subset = df[df[color] == player].copy()
        cols = ["BigECO", "QueenTraded", "Balanced", "CastleBalance",
                "WhiteStreak", "BlackStreak", "Result"]
        subset = subset[cols].dropna()
        subset["Player"] = player

        self.model = BayesianNetwork(EDGES)
        self.model.fit(subset, estimator=MaximumLikelihoodEstimator)

    def query(self, variables, evidence):
        """
        Query the Bayes net.
        ["Result"], {"BigECO": "B20-B99 Sicilian defence"}
        """
        infer = VariableElimination(self.model)
        return infer.query(variables, evidence=evidence)

    def print_cpds(self, path=None):
        """Print all conditional probability tables. Save full untruncated version if path is given."""
        output = "\n".join(f"--- {cpd.variable} ---\n{cpd}\n" for cpd in self.model.get_cpds())
        print(output)

        # manually iterate through rows of vars since calling model.get_cpds() will return a truncated version
        if path:
            with open(path, "w") as f:
                for cpd in self.model.get_cpds():
                    f.write(f"--- {cpd.variable} ---\n")
                    values = cpd.get_values()
                    var = cpd.variable
                    parents = cpd.variables[1:]
                    row_labels = [f"{var}({s})" for s in cpd.state_names[var]]
                    if not parents:
                        for label, val in zip(row_labels, values.flatten()):
                            f.write(f"  {label}: {val:.6}\n")
                    else:
                        from itertools import product as iter_product
                        parent_states = [cpd.state_names[p] for p in parents]
                        for col_idx, combo in enumerate(iter_product(*parent_states)):
                            col_label = ", ".join(f"{p}={v}" for p, v in zip(parents, combo))
                            f.write(f"  [{col_label}]\n")
                            for row_idx, label in enumerate(row_labels):
                                f.write(f"    {label}: {values[row_idx][col_idx]:.6f}\n")
                    f.write("\n")
