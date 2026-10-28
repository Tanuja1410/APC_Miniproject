def predict_next_expense(trip):
    try:
        import numpy as np
        from sklearn.linear_model import LinearRegression
    except ImportError as exc:
        raise ImportError("Install requirements first") from exc

    amounts = [e.amount for e in trip.expenses]
    if len(amounts) < 2:
        return None
    x = np.arange(1, len(amounts) + 1).reshape(-1, 1)
    y = np.array(amounts, dtype=float)
    model = LinearRegression()
    model.fit(x, y)
    return round(float(model.predict([[len(amounts) + 1]])[0]), 2)
