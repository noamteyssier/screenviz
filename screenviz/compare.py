# screenviz.compare

import sys
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio

pio.templates.default = "plotly_white"


def classify(x):
    if x.is_significant_a and x.is_significant_b:
        return "Significant in both"
    elif x.is_significant_a:
        return "Significant in A"
    elif x.is_significant_b:
        return "Significant in B"
    else:
        return "Not significant"


class CompareScreens:
    def __init__(
        self,
        filename_a: str,
        filename_b: str,
        merge_column_a: str = "gene",
        merge_column_b: str = "gene",
        variable_column_a: str = "pvalue",
        variable_column_b: str = "pvalue",
        threshold_column_a: str = "fdr",
        threshold_column_b: str = "fdr",
        threshold: float = 0.1,
        log_transform_a: bool = True,
        log_transform_b: bool = True,
    ):
        self.filename_a = filename_a
        self.filename_b = filename_b
        self.merge_column_a = merge_column_a
        self.merge_column_b = merge_column_b
        self.variable_column_a = variable_column_a
        self.variable_column_b = variable_column_b
        self.threshold_column_a = threshold_column_a
        self.threshold_column_b = threshold_column_b
        self.threshold = threshold
        self.log_transform_a = log_transform_a
        self.log_transform_b = log_transform_b

        self.df_a = self.load_dataframe(
            filename_a, merge_column_a, variable_column_a, threshold_column_a, "a"
        )
        self.df_b = self.load_dataframe(
            filename_b, merge_column_b, variable_column_b, threshold_column_b, "b"
        )
        self.df = pd.merge(
            self.df_a,
            self.df_b,
            left_on=f"{merge_column_a}_a",
            right_on=f"{merge_column_b}_b",
        )
        self.df = self.classify_dataframe(self.df)

    def load_dataframe(
        self,
        filename: str,
        merge_column: str,
        variable_column: str,
        threshold_column: str,
        suffix: str,
    ) -> pd.DataFrame:
        dataframe = pd.read_csv(filename, sep="\t")
        assert (
            merge_column in dataframe.columns
        ), f"Column {merge_column} not found in {filename}"
        assert (
            variable_column in dataframe.columns
        ), f"Column {variable_column} not found in {filename}"
        assert (
            threshold_column in dataframe.columns
        ), f"Column {threshold_column} not found in {filename}"
        dataframe = dataframe.loc[
            :, [merge_column, variable_column, threshold_column]
        ].rename(
            columns={
                merge_column: f"{merge_column}_{suffix}",
                variable_column: f"{variable_column}_{suffix}",
                threshold_column: f"{threshold_column}_{suffix}",
            }
        )

        if variable_column == threshold_column:
            dataframe = dataframe.iloc[:, :-1]

        return dataframe

    def classify_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df["is_significant_a"] = df[f"{self.threshold_column_a}_a"] < self.threshold
        df["is_significant_b"] = df[f"{self.threshold_column_b}_b"] < self.threshold
        df["classification"] = df.apply(lambda x: classify(x), axis=1)
        df["sizing"] = df.apply(
            lambda x: 10 if x.is_significant_a or x.is_significant_b else 5, axis=1
        )
        return df

    def plot_volcano(self, output: str = "comparison.html"):
        variable_name_x = f"{self.variable_column_a}_a"
        variable_name_y = f"{self.variable_column_b}_b"

        if self.log_transform_a:
            self.df[f"log_{self.variable_column_a}_a"] = -np.log10(
                self.df[f"{self.variable_column_a}_a"]
            )
            variable_name_x = f"log_{self.variable_column_a}_a"

        if self.log_transform_b:
            self.df[f"log_{self.variable_column_b}_b"] = -np.log10(
                self.df[f"{self.variable_column_b}_b"]
            )
            variable_name_y = f"log_{self.variable_column_b}_b"

        fig = px.scatter(
            self.df,
            x=variable_name_x,
            y=variable_name_y,
            color="classification",
            size="sizing",
            hover_name=f"{self.merge_column_a}_a",
            hover_data=[
                f"{self.variable_column_a}_a",
                f"{self.threshold_column_a}_a",
                f"{self.variable_column_b}_b",
                f"{self.threshold_column_b}_b",
            ],
            color_discrete_map={
                "Significant in both": "#003d99",
                "Significant in A": "#66194d",
                "Significant in B": "#006600",
                "Not significant": "#808080",
            },
        )
        fig.update_layout(
            height=1400,
            width=1400,
            title="Comparison of two screen results",
        )

        print(f"Saving comparison plot to: {output}", file=sys.stderr)
        fig.write_html(output)
