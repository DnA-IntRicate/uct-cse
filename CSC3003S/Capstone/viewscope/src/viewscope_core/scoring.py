import numpy as np

from viewscope_core.constants import MU_RHO_M, MU_THETA_DEG, SIGMA_RHO_M, SIGMA_THETA_DEG


def weight_factors(distances_m, incidences_deg):
    rho = np.asarray(distances_m, dtype=np.float64)
    theta = np.asarray(incidences_deg, dtype=np.float64)
    f_rho = np.exp(-0.5 * ((rho - MU_RHO_M) / SIGMA_RHO_M) ** 2)
    f_theta = np.exp(-0.5 * ((theta - MU_THETA_DEG) / SIGMA_THETA_DEG) ** 2)
    return f_rho * f_theta, f_rho, f_theta


def tangent_basis(normal):
    n = np.asarray(normal, dtype=np.float64)
    n = n / np.linalg.norm(n)
    axis = np.zeros(3, dtype=np.float64)
    axis[int(np.argmin(np.abs(n)))] = 1.0
    e1 = axis - np.dot(axis, n) * n
    e1 = e1 / np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    return e1, e2


def observer_geometry(target_position, target_normal, camera_positions):
    n = np.asarray(target_normal, dtype=np.float64)
    n = n / np.linalg.norm(n)
    d = np.atleast_2d(np.asarray(camera_positions, dtype=np.float64)) - np.asarray(
        target_position, dtype=np.float64
    )
    rho = np.linalg.norm(d, axis=1)
    unit = d / np.maximum(rho, 1e-12)[:, None]
    theta = np.degrees(np.arccos(np.clip(unit @ n, -1.0, 1.0)))
    return rho, theta


def sector_indices(target_position, target_normal, camera_positions, sector_count):
    e1, e2 = tangent_basis(target_normal)
    d = np.atleast_2d(np.asarray(camera_positions, dtype=np.float64)) - np.asarray(
        target_position, dtype=np.float64
    )
    azimuth = np.mod(np.arctan2(d @ e2, d @ e1), 2.0 * np.pi)
    k = np.floor(azimuth * sector_count / (2.0 * np.pi)).astype(np.int64)
    return np.minimum(k, sector_count - 1)


def best_per_sector(sectors, weights, sector_count):
    sectors = np.asarray(sectors)
    weights = np.asarray(weights, dtype=np.float64)
    best = np.zeros(weights.shape[0], dtype=bool)
    maxima = np.zeros(sector_count, dtype=np.float64)
    for s in range(sector_count):
        members = np.flatnonzero(sectors == s)
        if members.size:
            leader = members[int(np.argmax(weights[members]))]
            best[leader] = True
            maxima[s] = weights[leader]
    return best, maxima


def angular_diversity(sectors, sector_count):
    sectors = np.asarray(sectors)
    if sectors.size == 0:
        return 0.0
    ideal = sectors.size / sector_count
    counts = np.bincount(sectors, minlength=sector_count).astype(np.float64)
    return float(np.mean(np.minimum(counts, ideal) / ideal))


def target_score(sectors, weights, sector_count):
    _, maxima = best_per_sector(sectors, weights, sector_count)
    return float(maxima.mean())
