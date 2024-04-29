import numpy as np
import pandas as pd

# Constants
DEG_TO_RAD = np.pi / 180  # Convert degrees to radians
SOLAR_CONSTANT = 1367  # Approximate solar constant (W/m^2)

# Solar panel settings
latitude = 40.7128  # Example latitude (New York City)
tilt_angle = 30  # Tilt of the solar panel in degrees
panel_azimuth = 180  # South facing in the northern hemisphere

# Sample data: Day 100 of the year, from 6 AM to 6 PM
data = {
    "day_of_year": [100] * 13,
    "hour": list(range(6, 19)),
    "GHI": [
        0,
        50,
        200,
        350,
        500,
        650,
        700,
        650,
        500,
        350,
        200,
        50,
        0,
    ],  # Example irradiance values
}
df = pd.DataFrame(data)


# Function to calculate solar declination
def solar_declination(day_of_year):
    return 23.45 * np.sin(DEG_TO_RAD * 360 * (day_of_year - 81) / 365)


# Function to calculate hour angle
def hour_angle(hour):
    return 15 * (hour - 12)


# Calculate solar angles and adjusted irradiance
def calculate_irradiance(row):
    declination = solar_declination(row["day_of_year"]) * DEG_TO_RAD
    hour_ang = hour_angle(row["hour"]) * DEG_TO_RAD
    latitude_rad = latitude * DEG_TO_RAD
    tilt_rad = tilt_angle * DEG_TO_RAD
    panel_azimuth_rad = panel_azimuth * DEG_TO_RAD

    # Solar elevation
    sin_alpha = np.sin(latitude_rad) * np.sin(declination) + np.cos(
        latitude_rad
    ) * np.cos(declination) * np.cos(hour_ang)
    alpha = np.arcsin(sin_alpha)

    # Solar azimuth
    cos_Az = (np.sin(declination) - np.sin(latitude_rad) * sin_alpha) / (
        np.cos(latitude_rad) * np.cos(alpha)
    )
    azimuth = np.arccos(cos_Az)

    # Adjust azimuth based on hour of the day
    if hour_ang > 0:
        azimuth = 2 * np.pi - azimuth

    # Angle of incidence
    cos_theta = (
        np.sin(declination) * np.sin(latitude_rad) * np.cos(tilt_rad)
        - np.sin(declination)
        * np.cos(latitude_rad)
        * np.sin(tilt_rad)
        * np.cos(panel_azimuth_rad)
        + np.cos(declination)
        * np.cos(latitude_rad)
        * np.cos(tilt_rad)
        * np.cos(hour_ang)
        + np.cos(declination)
        * np.sin(latitude_rad)
        * np.sin(tilt_rad)
        * np.cos(panel_azimuth_rad)
        * np.cos(hour_ang)
        + np.cos(declination)
        * np.sin(tilt_rad)
        * np.sin(panel_azimuth_rad)
        * np.sin(hour_ang)
    )

    # Effective irradiance
    irradiance = max(0, row["GHI"] * cos_theta)  # Set to zero if cos_theta is negative
    return irradiance


# Apply calculations to each row in the DataFrame
df["Adjusted Irradiance"] = df.apply(calculate_irradiance, axis=1)

# Output the results
print(df[["hour", "GHI", "Adjusted Irradiance"]])
