import pandas as pd
import matplotlib.pyplot as plt
import pvlib
import numpy as np

# Read the historical GHI data
ghi_data = pd.read_csv("data/irradiance.csv", index_col=0, parse_dates=True)
ghi_data.set_index(ghi_data["GHI"])
# ghi_data.index = ghi_data.index.tz_localize(
#     "Europe/London", ambiguous="", nonexistent="shift_forward"
# )
print(ghi_data)

# Define the location (Newcastle Upon Tyne)
latitude = 54.9783
longitude = -1.6174
timezone = "Europe/London"
location = pvlib.location.Location(latitude, longitude, tz=timezone)

# Simulation times should match your historical data
times = ghi_data.index

# Simulate for different tilts and azimuths
tilts = [15, 30, 45]  # Example tilts in degrees
# tilts = [30]  # Example tilts in degrees
azimuths = [90, 180, 270]  # 0 = North, 90 = East, 180 = South, 270 = West

# Prepare a DataFrame to store simulation results
simulated_ghi = pd.DataFrame(index=times)

for tilt in tilts:
    for azimuth in azimuths:
        # Calculate the solar position
        solar_position = location.get_solarposition(times)

        # Get clear sky data
        clear_sky = location.get_clearsky(times, model="ineichen")

        # # Use the DIRINT model to estimate DNI and DHI from GHI
        erbs = pvlib.irradiance.erbs(
            ghi=ghi_data["GHI"],
            zenith=solar_position["apparent_zenith"],
            datetime_or_doy=ghi_data.index,
        )
        # Calculate plane of array irradiance
        poa_irradiance = pvlib.irradiance.get_total_irradiance(
            surface_tilt=tilt,
            surface_azimuth=azimuth,
            dni=erbs["dni"],
            ghi=ghi_data["GHI"],
            dhi=ghi_data["DHI"],
            solar_zenith=solar_position["apparent_zenith"],
            solar_azimuth=solar_position["azimuth"],
        )
        simulated_ghi[f"tilt_{tilt}_azimuth_{azimuth}"] = poa_irradiance["poa_global"]

# plt.plot(simulated_ghi.index, simulated_ghi["tilt_30_azimuth_180"], color="blue")
# plt.plot(simulated_ghi.index, ghi_data["GHI"], color="red")
# plt.show()
#
# column_name = "tilt_30_azimuth_180"
# irradiance_histogram = simulated_ghi[column_name][simulated_ghi[column_name] > 0]
# plt.hist(
#     irradiance_histogram,
#     bins=np.arange(0, 1000, 50),
#     color="skyblue",
#     edgecolor="black",
# )


# Define figure and subplot grid
num_tilts = 3  # Example number of tilts used in the simulation
num_azimuths = 3  # Example number of azimuths used in the simulation
fig, axs = plt.subplots(
    num_tilts, num_azimuths, figsize=(20, 20), sharex=True, sharey=True
)

# Iterate through each subplot and plot the data
for i, tilt in enumerate([15, 30, 45]):
    for j, azimuth in enumerate([90, 180, 270]):
        ax = axs[i, j]
        column_name = f"tilt_{tilt}_azimuth_{azimuth}"
        ax.plot(
            simulated_ghi[column_name],
            label=f"Simulated GHI\nTilt: {tilt}, Azimuth: {azimuth}",
        )
        # ax.plot(ghi_data["GHI"], label="Actual GHI", color="black", alpha=0.75)
        ax.set_title(f"Tilt: {tilt}°, Azimuth: {azimuth}°")
        ax.grid(True)

        # Add legend to each subplot
        ax.legend()

# Set common labels
for ax in axs[-1, :]:
    ax.set_xlabel("Time")
for ax in axs[:, 0]:
    ax.set_ylabel("GHI (W/m²)")

# Adjust layout
plt.tight_layout()
plt.show()

# Define figure and subplot grid for histograms
fig_hist, axs_hist = plt.subplots(
    num_tilts, num_azimuths, figsize=(20, 20), sharex=True, sharey=True
)

# Iterate through each subplot to plot histograms
bin_range = np.arange(
    0, 1000, 50
)  # Calculate bins based on max irradiance across all simulations

for i, tilt in enumerate(tilts):
    for j, azimuth in enumerate(azimuths):
        ax = axs_hist[i, j]
        column_name = f"tilt_{tilt}_azimuth_{azimuth}"

        # Filter out values equal to 0 and NaN
        valid_irradiance = simulated_ghi[column_name]
        valid_irradiance = simulated_ghi[simulated_ghi > 0]  # Exclude 0 values

        # Calculate and plot histogram
        ax.hist(
            valid_irradiance[
                column_name
            ].dropna(),  # Drop NaN values which can occur in solar calculations
            bins=bin_range,
            color="skyblue",  # You can change the color if you like
            edgecolor="black",
        )
        ax.set_title(f"Histogram of POA Irradiance\nTilt: {tilt}°, Azimuth: {azimuth}°")
        ax.grid(True)

# Set common labels
for ax in axs_hist[-1, :]:
    ax.set_xlabel("POA Irradiance (W/m²)")
for ax in axs_hist[:, 0]:
    ax.set_ylabel("Frequency")

# Adjust layout
plt.tight_layout()
plt.show()
