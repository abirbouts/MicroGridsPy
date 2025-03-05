def get_gurobi_settings(milp_formulation: bool) -> dict:
    """Get specific Gurobi settings based on the formulation type."""
    if milp_formulation:
        return{
            'Method': 3,
            'BarHomogeneous': 1,
            'Crossover': 1,
            'MIPFocus': 2, 
            'BarConvTol': 1e-3,
            'OptimalityTol': 1e-3,
            'FeasibilityTol': 1e-4,
            'NumericFocus': 2,
            'Heuristics': 0.9,
            'MIPGap': 0.05,
            'Cuts': 3
        }

    else:
        return {
            'Method': 2,
            'BarHomogeneous': 1,
            'Crossover': 1,
            'BarConvTol': 1e-3,
            'OptimalityTol': 1e-3,
            'FeasibilityTol': 1e-4,
            'MIPGap': 0.05,
            #'IterationLimit': 10000
        }