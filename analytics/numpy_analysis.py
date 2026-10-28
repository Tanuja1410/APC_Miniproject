from array import array
import numpy as np


def analyze_expenses(trip):
    amounts = array("d", [e.amount for e in trip.expenses])
    if not amounts:
        return {"total": 0.0, "average": 0.0, "maximum": 0.0, "minimum": 0.0, "count": 0}
    data = np.array(amounts, dtype=float)
    return {
        "total": round(float(np.sum(data)), 2),
        "average": round(float(np.mean(data)), 2),
        "maximum": round(float(np.max(data)), 2),
        "minimum": round(float(np.min(data)), 2),
        "count": int(data.size),
        "shape": data.shape,
        "dtype": str(data.dtype),
        "sample_reshape": data.reshape(-1, 1).shape
    }
