import pandas as pd
import matplotlib.pyplot as plt
import pvlib

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
tilts = [0, 15, 30, 45, 60, 75, 90]  # Example tilts in degrees
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

# Define figure and subplot grid
num_tilts = 7  # Example number of tilts used in the simulation
num_azimuths = 3  # Example number of azimuths used in the simulation
fig, axs = plt.subplots(
    num_tilts, num_azimuths, figsize=(20, 20), sharex=True, sharey=True
)

# Iterate through each subplot and plot the data
for i, tilt in enumerate([0, 15, 30, 45, 60, 75, 90]):
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
