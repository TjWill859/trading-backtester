import matplotlib.pyplot as plt
from engine.metrics import drawdown_series


def plot_equity_curves(equities, benchmark_equity=None,
                       title="Equity Curve", save_path=None):
    
    fig, ax = plt.subplots(figsize=(11, 5))

    for name, eq in equities.items():
        ax.plot(eq.index, eq, label=name, linewidth=1.5)

    if benchmark_equity is not None:
        ax.plot(benchmark_equity.index, benchmark_equity,
                label="SPY (benchmark)", color="black",
                linestyle="--", linewidth=1.5)

    ax.set_title(title)
    ax.set_ylabel("Portfolio value ($)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
    plt.show()


def plot_drawdowns(equities, title="Drawdown (% below previous peak)",
                   save_path=None):
    
    fig, ax = plt.subplots(figsize=(11, 4))

    for name, eq in equities.items():
        dd = drawdown_series(eq) * 100   # convert -0.25 to -25 (percent)
        ax.plot(dd.index, dd, label=name, linewidth=1.2)

    ax.set_title(title)
    ax.set_ylabel("Drawdown (%)")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1))
    ax.grid(alpha=0.3)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=150)
    plt.show()