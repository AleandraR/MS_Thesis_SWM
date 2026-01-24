import pandas as pd
import numpy as np

# ---------------- CONFIG ----------------
stations = [
    "Ambulong", "Baguio", "Coron", "Cuyo", "Dagupan",
    "Iba", "Iloilo", "Laoag", "Port Area", "Sangley Point", "Science Garden"
]

clim_file = "climnormals.csv"
output_file = "mean_monthly_rainfall.csv"

months = {
    6: "jun",
    7: "jul",
    8: "aug",
    9: "sep"
}

# ---------------- LOAD CLIM NORMALS ----------------
clim = pd.read_csv(clim_file)

# normalize column names
clim.columns = clim.columns.str.strip().str.upper()

clim.rename(columns={"STATION": "station"}, inplace=True)
clim.set_index("station", inplace=True)

# ---------------- MONTHLY TOTALS PER STATION ----------------
station_monthly = {}

for st in stations:
    df = pd.read_csv(f"{st} Daily Data.csv")

    # normalize column names
    df.columns = df.columns.str.strip().str.lower()

    # construct datetime
    df["date"] = pd.to_datetime(
        df[["year", "month", "day"]]
    )
    df.set_index("date", inplace=True)

    records = {}

    for yr in df["year"].unique():
        records[yr] = {}
        for m in months:
            data = df[
                (df.index.year == yr) &
                (df.index.month == m)
            ]["rainfall"]

            # fallback to climatological normal if missing or trace data exist
            if data.empty or data.isin([-999, -1]).any():
                records[yr][m] = clim.loc[st, months[m].upper()]
            else:
                records[yr][m] = data.sum()

    station_monthly[st] = pd.DataFrame.from_dict(records, orient="index")

# ---------------- REGIONAL MEAN (ARITHMETIC) ----------------
all_years = sorted(
    set().union(*[df.index for df in station_monthly.values()])
)

output = []

for yr in all_years:
    row = {"year": yr}

    for m, name in months.items():
        values = [
            station_monthly[st].loc[yr, m]
            for st in stations
            if yr in station_monthly[st].index
        ]

        row[name] = np.mean(values)

    # seasonal mean (Jun–Sep)
    row["annual"] = np.mean([row[m] for m in months.values()])
    output.append(row)

final_df = pd.DataFrame(output)
final_df.to_csv(output_file, index=False)

print("✔ Mean monthly rainfall saved to:", output_file)