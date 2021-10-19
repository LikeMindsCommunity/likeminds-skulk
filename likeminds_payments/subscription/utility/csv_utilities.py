import pandas as pd


class CsvUtilities:

    def __init__(self, pd_dataframe_instance: pd.DataFrame = None):
        self.pd_dataframe_instance = pd_dataframe_instance

    def get_pd_dataframe_instance(self) -> (pd.DataFrame, None):
        return self.pd_dataframe_instance

    def set_pd_dataframe_instance(self, csv_instance) -> None:
        self.pd_dataframe_instance = csv_instance

    def django_queryset_to_dataframe(self, queryset, col_sequence=[], col_map={}) -> pd.DataFrame:
        pd_dataframe = pd.DataFrame(list(queryset.values()))
        self.pd_dataframe_instance = pd_dataframe

        if col_map:
            pd_dataframe.rename(columns=col_map, inplace=True)

        if col_sequence:
            pd_dataframe = pd_dataframe[col_sequence]

        return pd_dataframe

    def object_list_to_dataframe(self, object_list, col_sequence=[], col_map={}) -> pd.DataFrame:
        pd_dataframe = pd.DataFrame(object_list)

        # Cleaning data
        # Replacing NaN to None
        pd_dataframe = pd_dataframe.applymap(lambda x: None if pd.isnull(x) else x)

        self.pd_dataframe_instance = pd_dataframe

        if col_map:
            pd_dataframe.rename(columns=col_map, inplace=True)

        if col_sequence:
            col_sequence = [col for col in col_sequence if col in pd_dataframe.columns]
            pd_dataframe = pd_dataframe[col_sequence]

        return pd_dataframe

    @staticmethod
    def pd_dataframe_to_csv(pd_dataframe, full_file_path):
        return pd_dataframe.to_csv(full_file_path, index=False)
