
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ----------------------------
# Global plot style
# ----------------------------
plt.rcParams["font.family"] = "serif"

# Circuit-diagram display style for U_T and U_F gates
style = {
    "displaycolor": {
        "U_T": ("#b266ff", "#000000"),   # purple fill, black text
        "U_F": ("#228B22", "#ffffff")    # dark-green fill, white text
    },
    "displaytext": {
        "U_T": r"$\hat{U}_{T}$",
        "U_F": r"$\hat{U}_{F}$"
    }
}


def plot_normalized_results(results, plot_type, state, shots, kappa_T):
    """
    Plot the measured success probability of a remote CNOT gate versus
    fiber communication steps, reproducing the style of Fig. 5 in the paper.

    The x-axis begins with a monolithic reference point 'M' (step = 0,
    i.e. no inter-QPU communication noise) followed by steps 1–10, where
    each step corresponds to one additional 10 m fiber segment.

    Four curves are shown — G-652-D, G-654-E, G-655-D, and a numerical
    (AerSimulator) reference — matching the legend in Fig. 5.

    Parameters
    ----------
    results : dict
        Keys are fiber-type labels (must match the `fibers` dictionary
        defined in Main.ipynb).  Values are lists of length `steps`
        containing the raw success counts for steps 1 … steps.
        The first element of each list is the monolithic (M) result
        obtained without any inter-QPU noise.
    plot_type : str
        Protocol label shown in the figure title, e.g. 'Cat-Comm' or 'TP1'.
    state : int or str
        Initial state of the control qubit (0 or 1), shown in the title.
    shots : int
        Total number of measurement shots per data point; used for
        normalisation to probability.
    kappa_T : float
        Transducer coupling constant used in this experiment (kappa_T = 0.5),
        displayed in the figure title.
    """
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams.update({'font.size': 16})

    # Number of fiber steps (excluding monolithic baseline)
    step_count = len(next(iter(results.values()))) - 1   # M + steps 1..N

    # x positions: 0 = M, 1..step_count = fiber steps
    x_positions = list(range(step_count + 1))
    x_labels = ['M'] + list(range(1, step_count + 1))

    # Marker styles and attenuation labels matching paper Fig. 5
    markers = ['o', 's', '^', 'D']
    # Original attenuation constants (km⁻¹) for display — NOT the kappa_F values
    alpha_display = {
        'G-652-D': 0.0415,
        'G-654-E': 0.0392,
        'G-655-D': 0.0507,
        'Numerical': 0.0415,
    }

    fig, ax = plt.subplots(figsize=(7, 5))

    for i, (label, values) in enumerate(results.items()):
        normalized = np.array(values, dtype=float) / shots
        alpha_val = alpha_display.get(label, '')
        legend_label = (
            f"{label} ($\\alpha={alpha_val}$ km$^{{-1}}$)"
            if alpha_val != '' else label
        )
        ax.plot(
            x_positions,
            normalized,
            marker=markers[i % len(markers)],
            linestyle='-',
            label=legend_label
        )

    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Fiber Step")
    ax.set_ylabel("Measured Probability")
    ax.set_title(
        f"$\\kappa_{{T}} = {kappa_T}$,  Control qubit in state $|{state}\\rangle$  ({plot_type})",
        fontsize=12
    )
    ax.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig("plot.png", dpi=300)
    plt.show()
    return fig


def fourier_plot(results, ax=None):
    """
    Plot the QFT fidelity versus communication distance, reproducing
    Fig. 9 of the paper.

    The first element of `results` is the monolithic fidelity (labelled
    'M' on the x-axis); subsequent elements correspond to increasing fiber
    lengths, each step representing one additional 10 m fiber segment.
    Two curves are expected — one for ibm_torino hardware and one for
    the AerSimulator reference — and should be passed in two separate
    calls or as a combined list.

    Parameters
    ----------
    results : list or array-like
        Fidelity values in the range [0, 1].  The y-axis is displayed
        as a percentage (multiplied by 100).
    ax : matplotlib.axes.Axes, optional
        Existing axes to plot on.  If None a new figure is created.

    Returns
    -------
    fig : matplotlib.figure.Figure
    ax  : matplotlib.axes.Axes
    """
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.size"] = 16

    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    else:
        fig = ax.figure

    results = np.array(results, dtype=float)
    steps = np.arange(len(results))

    # x-axis: 'M' for monolithic, then 1, 2, … for fiber steps
    labels = ['M'] + list(range(1, len(results)))

    ax.plot(steps, results, marker='o')
    ax.set_xticks(steps)
    ax.set_xticklabels(labels)

    # Display fidelity as percentage
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda y, _: f"{y * 100:.1f}")
    )

    ax.set_xlabel("Fiber Steps")
    ax.set_ylabel("Fidelity (%)")

    plt.tight_layout()
    return fig, ax
