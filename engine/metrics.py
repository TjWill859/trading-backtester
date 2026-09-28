import numpy as np


def sharpe_ratio(returns, risk_free_rate=0.0, periods_per_year=252):
    
    daily_rf = risk_free_rate / periods_per_year
    excess = returns - daily_rf
    if excess.std() == 0:
        return np.nan  # avoid divide-by-zero if returns are flat
    return np.sqrt(periods_per_year) * excess.mean() / excess.std() # scales a daily number up to an annual one (variance scales linearly with time, so std scales with the square root of time)


def max_drawdown(equity):
    
    running_max = equity.cummax() # "highest point seen so far, at each day"
    drawdown = (equity - running_max) / running_max
    return drawdown.min()


def drawdown_series(equity):
    
    running_max = equity.cummax()
    return (equity - running_max) / running_max


def annualized_return(equity, periods_per_year=252):
   
    total_return = equity.iloc[-1] / equity.iloc[0]
    n_years = len(equity) / periods_per_year
    return total_return ** (1 / n_years) - 1 # that's just algebra on compound interest: if (1+r)^years = total_return, solve for r


def alpha_vs_benchmark(strategy_ann_return, benchmark_ann_return):
    
    return strategy_ann_return - benchmark_ann_return


def performance_summary(result, benchmark_equity=None, risk_free_rate=0.0):
   
    equity = result['equity']
    returns = result['strategy_return']

    summary = {
        'sharpe': sharpe_ratio(returns, risk_free_rate),
        'max_drawdown': max_drawdown(equity),
        'annualized_return': annualized_return(equity),
    }

    if benchmark_equity is not None:
        bench_ann_return = annualized_return(benchmark_equity)
        summary['benchmark_annualized_return'] = bench_ann_return
        summary['alpha'] = alpha_vs_benchmark(summary['annualized_return'], bench_ann_return)

    return summary