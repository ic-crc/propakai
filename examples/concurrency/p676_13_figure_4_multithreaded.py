# Copyright (c) 2026 His Majesty the King in Right of Canada as represented by the Minister of
# Industry through the Communications Research Centre Canada.
#
# Licensed under the MIT License
# See LICENSE file in the project root for full license text.

"""Calculates values and display FIGURE 4 from ITU-R P.676-13."""

import sys
from os import cpu_count
import time
import concurrent.futures
from enum import Enum, auto
import matplotlib.pyplot as plt
from propakai import p676_13 as p676
from propakai import p835_6 as p835


class ExecutionMode(Enum):
    PROCESSING = auto()
    THREADING = auto() 


def zenith_attenuation(f_ghz) -> tuple[float, float]:
    MAGRA = p835.ReferenceAtmosphere.MEAN_ANNUAL_GLOBAL
    att_std_dB, _, _ = p676.slant_path_gaseous_attenuation(f_ghz=f_ghz, h1_km=0, h2_km=100.01,
                                                            phi1_deg=90, atm=MAGRA, rho0_gm3=7.5)

    # Note: The "peaks" of the dry curve generated here do not perfectly match those from
    # the figure in the recommendation. Not sure what input parameters were used.
    att_dry_dB, _, _ = p676.slant_path_gaseous_attenuation(f_ghz=f_ghz, h1_km=0, h2_km=100.01,
                                                            phi1_deg=90, atm=MAGRA, rho0_gm3=0)

    print('.', end='', flush=True)

    # NOTE should use locks on longer prints
    #print(f'{f_ghz} GHz, {att_std_dB:.3f} dB, {att_dry_dB:.3f} dB')

    return (att_std_dB, att_dry_dB)


def figure_4(exec_mode: ExecutionMode, num_workers: int) -> None:
    """Calculates values and display FIGURE 4 from ITU-R P.676-13."""
    freqs = list(range(1, 1001, 1))
    atts = [[],[]]

    start_time = time.time()

    if exec_mode == ExecutionMode.THREADING:
        executor = concurrent.futures.ThreadPoolExecutor
    else:
        executor = concurrent.futures.ProcessPoolExecutor
    with executor(max_workers=num_workers) as executor:
        futures = [executor.submit(zenith_attenuation, f_ghz) for f_ghz in freqs]
        for future in futures:
            att_std_dB, att_dry_dB = future.result()
            atts[0].append(att_std_dB)
            atts[1].append(att_dry_dB)

    end_time = time.time()
    print(f"\nExecution took {end_time - start_time:.2f} seconds.")

    fig, ax1 = plt.subplots()
    fig.set_size_inches(12, 6.75)
    ax1.set_yscale('log')
    ax1.set_xlim((0, 1000))
    ax1.set_xticks([*range(0, 1000+1, 100)])
    ax1.set_ylim((1E-3, 1E5))
    ax1.set_yticks([1E-3,1E-2,1E-1,1,1E1,1E2,1E3,1E4,1E5])
    ax1.plot(freqs, atts[0], color='#FF0000', label='standard')
    ax1.plot(freqs, atts[1], color='#0000FF', label='dry')
    ax1.set_title('FIGURE 4\nZenith attenuation due to atmospheric gases, calculated at 1 GHz ' \
                  'intervals, including line centre')
    ax1.set_xlabel('Frequency (GHz)')
    ax1.set_ylabel('Zenith attenuation (dB)')
    ax1.legend()
    plt.grid(True, 'both','both')
    plt.show()


def get_worker_count(exec_mode: ExecutionMode, default_num_workers: int) -> int:
    """Prompts the user to enter the number of worker threads"""
    if exec_mode == ExecutionMode.THREADING:
        worker_name = 'threads'
    else:
        worker_name = 'processes'
    prompt = f'\nEnter the number of worker {worker_name} to use (default: {default_num_workers}): '
    while True:
        user_input = input(prompt).strip()
        if not user_input:
            print(f'Using default value: {default_num_workers}')
            return default_num_workers
        try:
            num_workers = int(user_input)
            if num_workers > 0:
                return num_workers
            else:
                print(f'Error: Number of {worker_name} must be a positive number.')
        except ValueError:
            print('Error: Invalid input. Please enter a whole number.')


def ask_use_multiprocessing() -> bool:
    prompt = "\nDo you want to use multi-processing instead? [Y/n]: "
    while True:
        response = input(prompt).strip().lower()
        if response == "":
            return True
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print("Invalid input. Please enter 'y' for yes or 'n' for no.")


if __name__ == '__main__':
    exec_mode = ExecutionMode.THREADING

    if hasattr(sys, "_is_gil_enabled") and sys._is_gil_enabled() is False:
        print("\n✅ This Python interpreter is free-threaded (no GIL).")
        print("   This means multi-threading can provide true parallelism on CPU-bound tasks.")
    else:
        print("\n❌ This Python interpreter has the GIL enabled.")
        print("   This means multi-threading won't significantly improve performance on CPU-" \
              "bound tasks.")
        if ask_use_multiprocessing() is True:
            exec_mode = ExecutionMode.PROCESSING

    default_num_workers = cpu_count() or 4  # fallback to 4 if cpu_count fails
    num_workers = get_worker_count(exec_mode, default_num_workers)

    figure_4(exec_mode, num_workers)
