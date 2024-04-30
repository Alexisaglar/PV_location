import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pvlib

# Read the historical GHI data
ghi_data = pd.read_csv("data/irradiance.csv", index_col=0, parse_dates=True)
ghi_data = ghi_data.resample("h").mean()
print(ghi_data.head())  # To check the first few entries.
# Resample the 1-minute data to hourly

# Define the location (Newcastle Upon Tyne)
tilt = 30
azimuth = 180
latitude = 54.9783
longitude = -1.6174
timezone = "Europe/London"
location = pvlib.location.Location(latitude, longitude, tz=timezone)

# Calculate solar position for the times in your data
solar_position = location.get_solarposition(ghi_data.index)

# # Use the DIRINT model to estimate DNI and DHI from GHI
dirint = pvlib.irradiance.dirint(
    ghi=ghi_data["GHI"],
    solar_zenith=solar_position["apparent_zenith"],
    times=ghi_data.index,
)
print(dirint, ghi_data["GHI"].max())


# Calculate the solar zenith and azimuth in degrees
solar_zenith = solar_position["apparent_zenith"].values
solar_azimuth = solar_position["azimuth"].values

# Convert angles from degrees to radians for computation
solar_zenith_rad = np.radians(solar_zenith)
solar_azimuth_rad = np.radians(solar_azimuth)
tilt_rad = np.radians(tilt)
azimuth_rad = np.radians(azimuth)

# Calculate the angle of incidence
cos_theta = np.sin(solar_zenith_rad) * np.sin(tilt_rad) * np.cos(
    azimuth_rad - solar_azimuth_rad
) + np.cos(solar_zenith_rad) * np.cos(tilt_rad)

# Ensure cos_theta does not exceed 1 or drop below -1 due to precision issues
cos_theta = np.clip(cos_theta, -1, 1)

# Calculate irradiance on the panel
irradiance_on_panel = dirint * cos_theta

# # Output the results
# print(f"Solar Zenith Angle: {solar_zenith:} degrees")
# print(f"Solar Azimuth: {solar_azimuth:} degrees")
# print(f"Angle of Incidence (cosine): {cos_theta:}")
# print(f"Irradiance on Panel: {irradiance_on_panel:} W/m^2")

# Plotting the results
plt.figure(figsize=(12, 6))
plt.plot(ghi_data.index, irradiance_on_panel, label="Irradiance on Panel")
plt.plot(ghi_data.index, ghi_data["GHI"], label="GHI")
plt.xlabel("Time")
plt.ylabel("Irradiance (W/m^2)")
plt.title("Irradiance on Solar Panel Over Time")
plt.legend()
plt.grid(True)
plt.show()
