import os
import pandas as pd


def write_file(df: pd.DataFrame, file_name: str, compression: str = ""):
    file_name_extension = os.path.splitext(file_name)[1]

    if file_name_extension == ".csv":
        df.to_csv(file_name, index=False)

    elif file_name_extension == ".zip":
        df.to_csv(
            file_name, compression=dict(method="zip", archive_name="data"), index=False
        )

    elif file_name_extension == ".parquet":
        compression = "brotli" if compression == "" else compression
        df.to_parquet(file_name, engine="pyarrow", compression=compression)

    elif file_name_extension == ".feather":
        compression = "zstd" if compression == "" else compression
        df.to_feather(file_name, compression=compression)

    elif file_name_extension == ".h5":
        compression = "blosc:lz4" if compression == "" else compression
        df.to_hdf(
            file_name,
            key="data",
            mode="w",
            format="table",
            index=False,
            complevel=9,
            complib=compression,
        )

    elif file_name_extension == ".pkl":
        compression = "zip" if compression == "" else compression
        df.to_pickle(file_name, compression=compression)

    elif file_name_extension == ".json":
        df.to_json(file_name, orient="records")

    else:
        Exception(
            "[ERROR]: Error in write_file()! The file extension is unknown or not mapped:",
            file_name_extension,
        )


def read_file(file_name: str, compression: str=""):
    file_name_extension = os.path.splitext(file_name)[1]

    if file_name_extension == ".csv" or file_name_extension == ".zip":
        df = pd.read_csv(file_name, keep_default_na=False)

    elif file_name_extension == ".parquet":
        df = pd.read_parquet(file_name)

    elif file_name_extension == ".feather":
        df = pd.read_feather(file_name)

    elif file_name_extension == ".h5":
        df = pd.read_hdf(file_name, key="data")

    elif file_name_extension == ".pkl":
        df = pd.read_pickle(
            file_name, compression=compression
        ).copy()  # copy added because of some trouble with categories not fully read by mem util on first pass

    elif file_name_extension == ".json":
        df = pd.read_json(file_name, convert_dates=False)

    elif file_name_extension == ".xlsx":
        df = pd.read_excel(file_name, sheet_name="quotes", keep_default_na=False)

    else:
        Exception(
            "[ERROR]: Error in write_file()! The file extension is unknown or not mapped:",
            file_name_extension,
        )

    return df
