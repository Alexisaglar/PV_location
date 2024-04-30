import pandas as pd
import matplotlib.pyplot as plt
import pvlib

# Read the historical GHI data
ghi_data = pd.read_csv("data/irradiance.csv", index_col=0, parse_dates=True)
# Assuming your CSV has a column "GHI" that you want to use directly.
print(ghi_data.head())  # To check the first few entries.

# Define the location (Newcastle Upon Tyne)
latitude = 54.9783
longitude = -1.6174
timezone = "Europe/London"
location = pvlib.location.Location(latitude, longitude, tz=timezone)

# Calculate solar position for the times in your data
solar_position = location.get_solarposition(ghi_data.index)

# Decompose GHI into DNI and DHI using Erbs model
erbs_data = pvlib.irradiance.erbs(
    ghi_data["GHI"].values, solar_position["apparent_zenith"], ghi_data.index
)
ghi_data["DNI"] = erbs_data["dni"]
ghi_data["DHI"] = erbs_data["dhi"]
ghi_data["Kt"] = erbs_data["kt"]

print(ghi_data[["DNI", "DHI", "Kt"]].head())

# Simulation for different tilts and azimuths
tilts = [0, 15, 30, 45, 60, 75, 90]
azimuths = [0, 90, 180, 270]
simulated_poa = pd.DataFrame(index=ghi_data.index)

for tilt in tilts:
    for azimuth in azimuths:
        poa_components = pvlib.irradiance.get_total_irradiance(
            surface_tilt=tilt,
            surface_azimuth=azimuth,
            solar_zenith=solar_position["apparent_zenith"],
            solar_azimuth=solar_position["azimuth"],
            dni=ghi_data["DNI"],
            ghi=ghi_data["GHI"],
            dhi=ghi_data["DHI"],
        )
        simulated_poa[f"tilt_{tilt}_azimuth_{azimuth}"] = poa_components["poa_global"]

# Plot results for analysis
fig, axs = plt.subplots(
    len(tilts), len(azimuths), figsize=(20, 20), sharex=True, sharey=True
)
for i, tilt in enumerate(tilts):
    for j, azimuth in enumerate(azimuths):
        ax = axs[i, j]
        ax.plot(
            ghi_data.index,
            ghi_data["GHI"],
            label="Actual GHI",
            color="black",
            alpha=0.75,
        )
        ax.plot(
            simulated_poa.index,
            simulated_poa[f"tilt_{tilt}_azimuth_{azimuth}"],
            label=f"Simulated POA\nTilt: {tilt}, Azimuth: {azimuth}",
        )
        ax.set_title(f"Tilt: {tilt}°, Azimuth: {azimuth}°")
        ax.legend()
        ax.grid(True)

# Common labels
for ax in axs[-1, :]:
    ax.set_xlabel("Time")
for ax in axs[:, 0]:
    ax.set_ylabel("Irradiance (W/m²)")

plt.tight_layout()
plt.show()
