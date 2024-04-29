import pvlib
from datetime import datetime
import numpy as np


def hay_davies(
    I_h_diffuse, I_dn_direct, zenith_angle, azimuth_angle, tilt_angle, surface_azimuth
):
    """
    Calculate total irradiance on a tilted surface using the Hay-Davies method.

    Parameters:
    I_h_diffuse (float): Diffuse horizontal irradiance (W/m^2)
    I_dn_direct (float): Direct normal irradiance (W/m^2)
    zenith_angle (float): Solar zenith angle in degrees
    azimuth_angle (float): Solar azimuth angle in degrees
    tilt_angle (float): Tilt angle of the surface in degrees
    surface_azimuth (float): Azimuth angle of the surface in degrees

    Returns:
    float: Total irradiance on the tilted surface (W/m^2)
    """
    # Convert angles from degrees to radians for computation
    zenith_rad = np.radians(zenith_angle)
    azimuth_rad = np.radians(azimuth_angle)
    tilt_rad = np.radians(tilt_angle)
    surface_azimuth_rad = np.radians(surface_azimuth)

    # Cosine of the angle of incidence
    cos_theta_i = np.sin(zenith_rad) * np.cos(tilt_rad) * np.cos(
        azimuth_rad - surface_azimuth_rad
    ) + np.cos(zenith_rad) * np.sin(tilt_rad)
    cos_theta_i = max(cos_theta_i, 0)  # No negative values

    # Isotropic diffuse component
    I_d_isotropic = I_h_diffuse * (1 + np.cos(tilt_rad)) / 2

    # Beam component on the tilted surface
    I_b_direct = I_dn_direct * cos_theta_i

    # Simple model for circumsolar diffuse
    circumsolar_factor = 0.1  # Example fraction
    I_d_circumsolar = I_b_direct * circumsolar_factor

    # Total irradiance
    I_t_total = I_d_isotropic + I_d_circumsolar + I_b_direct

    return I_t_total


# Location and time setup
latitude, longitude = 40.7128, -74.0060  # New York City
tz = "America/New_York"
time = datetime(2023, 4, 15, 12)  # April 15, 2023, at noon

# Create a location object in pvlib
location = pvlib.location.Location(latitude, longitude, tz)

# Solar position
solar_position = location.get_solarposition(time)

# Clear sky irradiance using Ineichen model (simplified clear sky model)
clear_sky = location.get_clearsky(time, model="ineichen", solar_position=solar_position)

# Direct and diffuse irradiance
I_dn = clear_sky["dni"]
I_h = clear_sky["ghi"]
diffuse_fraction = 0.3  # Example value for diffuse fraction
I_h_diffuse = I_h * diffuse_fraction

# Tilt and azimuth of the surface
tilt_angle = 30  # Degrees
surface_azimuth = 140  # Degrees

# Total irradiance on the tilted surface
total_irradiance = hay_davies(
    I_h_diffuse,
    I_dn,
    solar_position["apparent_zenith"],
    solar_position["azimuth"],
    tilt_angle,
    surface_azimuth,
)

print(f"Total Irradiance on Tilted Surface: {total_irradiance} W/m^2")
