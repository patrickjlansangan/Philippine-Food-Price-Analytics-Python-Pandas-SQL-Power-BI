import os
import re
import pandas as pd
from sqlalchemy import create_engine


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

USER = "root"
PASSWORD = "10Garfield04"
HOST = "localhost"
PORT = 3307
DATABASE = "supply"

engine = create_engine(
    f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
)


# ============================================================
# FOLDER CONFIGURATION
# ============================================================

folder_path = r"C:\Users\Patrick\Downloads\DOWNLOADS\wfp_food_prices_phl.csv"


# ============================================================
# START
# ============================================================

print("=" * 70)
print("Starting the Automated ETL Pipeline...")
print("=" * 70)

print(f"\nScanning folder: {folder_path}")


# ============================================================
# EXTRACT - FIND CSV FILES
# ============================================================

try:
    files = [
        file for file in os.listdir(folder_path)
        if file.lower().endswith(".csv")
    ]
except Exception as e:
    print(f"\nERROR: Could not access folder.")
    print(e)
    raise SystemExit


print(f"Found {len(files)} CSV files.")


# ============================================================
# STATISTICS
# ============================================================

files_found = len(files)
files_processed = 0
files_failed = 0

total_rows_extracted = 0
total_rows_loaded = 0
total_duplicates_removed = 0


# ============================================================
# FUNCTION: CREATE SAFE TABLE NAME
# ============================================================

def make_safe_table_name(name):

    name = os.path.splitext(name)[0]

    # Replace anything that is not a letter, number, or underscore
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)

    # Replace multiple underscores
    name = re.sub(r"_+", "_", name)

    # Remove underscores from beginning/end
    name = name.strip("_")

    # MySQL table names should not exceed 64 characters
    name = name[:64]

    # Prevent empty table name
    if not name:
        name = "table_data"

    return name.lower()


# ============================================================
# FUNCTION: CLEAN COLUMN NAMES
# ============================================================

def clean_column_names(df):

    new_columns = []
    used_columns = set()

    for column in df.columns:

        column = str(column).strip().lower()

        # Replace spaces with underscores
        column = re.sub(r"\s+", "_", column)

        # Remove special characters
        column = re.sub(r"[^a-zA-Z0-9_]", "", column)

        # Replace multiple underscores
        column = re.sub(r"_+", "_", column)

        # Remove underscores from beginning/end
        column = column.strip("_")

        # Prevent empty column names
        if not column:
            column = "column"

        # MySQL maximum identifier length = 64
        column = column[:60]

        # Make duplicate column names unique
        original_column = column
        counter = 1

        while column in used_columns:

            suffix = f"_{counter}"

            # Keep total length <= 64
            column = original_column[:64 - len(suffix)] + suffix

            counter += 1

        used_columns.add(column)
        new_columns.append(column)

    df.columns = new_columns

    return df


# ============================================================
# FUNCTION: CLEAN TEXT COLUMNS
# ============================================================

def clean_text_columns(df):

    text_columns = df.select_dtypes(include=["object", "string"]).columns

    for column in text_columns:

        df.loc[:, column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

        # Convert empty strings to missing values
        df.loc[df[column] == "", column] = pd.NA

    return df


# ============================================================
# FUNCTION: AUTOMATIC DATA TYPE DETECTION
# ============================================================

def detect_data_types(df):

    for column in df.columns:

        # Skip columns that already have a non-object type
        if not (
            pd.api.types.is_object_dtype(df[column])
            or pd.api.types.is_string_dtype(df[column])
        ):
            continue

        # Remove missing values for testing
        non_null = df[column].dropna()

        if len(non_null) == 0:
            continue

        # ----------------------------------------------------
        # DATE DETECTION
        # ----------------------------------------------------
        #
        # We only attempt date conversion when the column
        # name strongly suggests that it contains dates.
        #
        # This prevents values such as:
        # open_hour
        # close_hour
        # time
        #
        # from being incorrectly converted into datetime.
        # ----------------------------------------------------

        date_keywords = [
            "date",
            "datetime",
            "timestamp",
            "created_at",
            "updated_at",
            "start_date",
            "end_date",
            "birth_date",
            "purchase_date",
            "order_date",
            "transaction_date"
        ]

        is_date_column = any(
            keyword in column.lower()
            for keyword in date_keywords
        )

        if is_date_column:

            converted_dates = pd.to_datetime(
                df[column],
                errors="coerce",
                dayfirst=True
            )
            success_rate = converted_dates.notna().mean()

            if success_rate >= 0.80:

                df.loc[:, column] = converted_dates

                print(
                    f"  Converted '{column}' -> datetime"
                )

                continue

        # ----------------------------------------------------
        # NUMERIC DETECTION
        # ----------------------------------------------------

        converted_numeric = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        success_rate = converted_numeric.notna().mean()

        if success_rate >= 0.90:

            df.loc[:, column] = converted_numeric

            print(
                f"  Converted '{column}' -> numeric"
            )

    return df


# ============================================================
# FUNCTION: ANALYZE MISSING VALUES
# ============================================================

def analyze_missing_values(df):

    missing = df.isna().sum()

    missing = missing[missing > 0]

    if len(missing) == 0:

        print("  Missing values: None")

    else:

        print("  Missing values:")

        for column, count in missing.items():

            percentage = (count / len(df)) * 100

            print(
                f"    {column}: "
                f"{count} ({percentage:.2f}%)"
            )

    return missing


# ============================================================
# FUNCTION: REMOVE COMPLETELY EMPTY COLUMNS
# ============================================================

def remove_empty_columns(df):

    empty_columns = [
        column
        for column in df.columns
        if df[column].isna().all()
    ]

    if empty_columns:

        print(
            f"\n  Completely empty columns found: "
            f"{len(empty_columns)}"
        )

        print("  Removing completely empty columns...")

        df = df.drop(columns=empty_columns).copy()

    return df


# ============================================================
# FUNCTION: HANDLE MISSING VALUES
# ============================================================

def handle_missing_values(df):

    print("\n  Handling missing values...")

    for column in df.columns:

        missing_count = df[column].isna().sum()

        if missing_count == 0:
            continue

        # Numeric columns
        if pd.api.types.is_numeric_dtype(df[column]):

            df.loc[:, column] = df[column].fillna(0)

        # Datetime columns
        elif pd.api.types.is_datetime64_any_dtype(df[column]):

            # Do not invent dates.
            # Keep missing datetime values as NULL.
            continue

        # Text columns
        else:

            df.loc[:, column] = df[column].fillna("Unknown")

    return df


# ============================================================
# FUNCTION: VALIDATE DATA
# ============================================================

def validate_data(df):

    print("\n  Validating data...")

    problems = []

    # Check completely empty columns
    empty_columns = [
        column
        for column in df.columns
        if df[column].isna().all()
    ]

    if empty_columns:

        problems.append(
            f"Completely empty columns: {len(empty_columns)}"
        )

    # Check infinite numeric values
    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:

        infinite_count = df[column].isin(
            [float("inf"), float("-inf")]
        ).sum()

        if infinite_count > 0:

            problems.append(
                f"{column}: "
                f"{infinite_count} infinite values"
            )

    if problems:

        print("  Validation issues:")

        for problem in problems:
            print(f"    - {problem}")

    else:

        print("  Validation passed.")

    return problems


# ============================================================
# FUNCTION: DETECT OUTLIERS
# ============================================================

def detect_outliers(df):

    print("\n  Checking for possible outliers...")

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    outlier_results = {}

    for column in numeric_columns:

        series = df[column].dropna()

        # Need enough values to calculate meaningful IQR
        if len(series) < 5:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        # If all values are identical
        if iqr == 0:
            continue

        lower_bound = q1 - (1.5 * iqr)
        upper_bound = q3 + (1.5 * iqr)

        outliers = df[
            (df[column] < lower_bound)
            |
            (df[column] > upper_bound)
        ]

        count = len(outliers)

        if count > 0:

            percentage = (count / len(df)) * 100

            outlier_results[column] = count

            print(
                f"    {column}: "
                f"{count} possible outlier rows "
                f"({percentage:.2f}%)"
            )

    if not outlier_results:

        print("  No obvious outliers detected.")

    else:

        print(
            "  Note: Outliers are flagged only. "
            "They are NOT automatically deleted."
        )

    return outlier_results


# ============================================================
# FUNCTION: SHOW DATA TYPES
# ============================================================

def show_data_types(df):

    print("\n  Data types:")

    for column, dtype in df.dtypes.items():

        print(
            f"    {column}: {dtype}"
        )


# ============================================================
# FUNCTION: DATA QUALITY SUMMARY
# ============================================================

def data_quality_summary(df):

    print("\n  Data Quality Summary")

    print(
        f"    Rows: {len(df)}"
    )

    print(
        f"    Columns: {len(df.columns)}"
    )

    print(
        f"    Missing values: {df.isna().sum().sum()}"
    )

    print(
        f"    Duplicate rows: {df.duplicated().sum()}"
    )


# ============================================================
# PROCESS EACH CSV FILE
# ============================================================

for file in files:

    file_path = os.path.join(
        folder_path,
        file
    )

    print("\n")
    print("=" * 70)
    print(f"Processing: {file}")
    print("=" * 70)

    try:

        # ====================================================
        # EXTRACT
        # ====================================================

        print("\n[EXTRACT] Reading CSV...")

        df = pd.read_csv(
            file_path,
            low_memory=False
        )

        # Make sure we have an independent DataFrame
        df = df.copy()

        extracted_rows = len(df)

        total_rows_extracted += extracted_rows

        print(
            f"  Rows extracted: {extracted_rows}"
        )

        print(
            f"  Columns extracted: {len(df.columns)}"
        )


        # ====================================================
        # TRANSFORM - CLEAN COLUMN NAMES
        # ====================================================

        print("\n[TRANSFORM] Cleaning column names...")

        df = clean_column_names(df)


        # ====================================================
        # TRANSFORM - REMOVE EMPTY COLUMNS
        # ====================================================

        df = remove_empty_columns(df)


        # ====================================================
        # TRANSFORM - REMOVE DUPLICATES
        # ====================================================

        print("\n[TRANSFORM] Removing duplicate rows...")

        before_duplicates = len(df)

        df = df.drop_duplicates().copy()

        duplicates_removed = (
            before_duplicates - len(df)
        )

        total_duplicates_removed += duplicates_removed

        print(
            f"  Duplicate rows removed: "
            f"{duplicates_removed}"
        )


        # ====================================================
        # TRANSFORM - CLEAN TEXT
        # ====================================================

        print("\n[TRANSFORM] Cleaning text columns...")

        df = clean_text_columns(df)


        # ====================================================
        # TRANSFORM - DATA TYPE DETECTION
        # ====================================================

        print(
            "\n[TRANSFORM] Detecting data types..."
        )

        df = detect_data_types(df)


        # ====================================================
        # ANALYSIS - MISSING VALUES
        # ====================================================

        print(
            "\n[ANALYSIS] Checking missing values..."
        )

        analyze_missing_values(df)


        # ====================================================
        # TRANSFORM - HANDLE MISSING VALUES
        # ====================================================

        df = handle_missing_values(df)


        # ====================================================
        # VALIDATION
        # ====================================================

        validate_data(df)


        # ====================================================
        # OUTLIER DETECTION
        # ====================================================

        detect_outliers(df)


        # ====================================================
        # DATA QUALITY SUMMARY
        # ====================================================

        data_quality_summary(df)


        # ====================================================
        # SHOW DATA TYPES
        # ====================================================

        show_data_types(df)


        # ====================================================
        # CREATE TABLE NAME
        # ====================================================

        table_name = make_safe_table_name(file)

        print(
            f"\n[LOAD] Loading into MySQL table: "
            f"{table_name}"
        )


        # ====================================================
        # LOAD INTO MYSQL
        # ====================================================

        df.to_sql(
            table_name,
            con=engine,
            if_exists="replace",
            index=False,
            chunksize=1000
        )


        loaded_rows = len(df)

        total_rows_loaded += loaded_rows

        files_processed += 1

        print(
            f"  Successfully loaded "
            f"{loaded_rows} rows."
        )


        # ====================================================
        # SUCCESS
        # ====================================================

        print(
            f"\nSUCCESS: {file}"
        )


    except PermissionError:

        files_failed += 1

        print(
            f"\nFAILED: Permission denied "
            f"for {file}"
        )

        print(
            "  Make sure the file is not open in "
            "Excel or another program."
        )

        continue


    except Exception as e:

        files_failed += 1

        print(
            f"\nFAILED: {file}"
        )

        print(
            f"  Error: {e}"
        )

        continue


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n")
print("=" * 70)
print("ETL PIPELINE COMPLETE")
print("=" * 70)

print(
    f"\nFiles found:              {files_found}"
)

print(
    f"Files processed:          {files_processed}"
)

print(
    f"Files failed:             {files_failed}"
)

print(
    f"Rows extracted:           {total_rows_extracted}"
)

print(
    f"Rows loaded:              {total_rows_loaded}"
)

print(
    f"Duplicate rows removed:   {total_duplicates_removed}"
)

print("\n" + "=" * 70)
print("End of ETL Pipeline")
print("=" * 70)
