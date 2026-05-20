"""
Train XGBoost domain valuation model.

Features (in order):
  domain_length  - int, length of SLD (e.g. "google" -> 6)
  tld_length     - int, length of suffix (e.g. "com" -> 3)
  vowel_count    - int, vowels in SLD
  trends_score   - float 0-100
  moz_da         - float 0-100

Target: est_value in USD
"""

import os
import numpy as np
import joblib
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

ARTIFACT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "back-end",
    "artifacts",
    "xgb_valuation.pkl",
)

RNG = np.random.default_rng(42)
N = 2000


def generate_samples(n: int) -> tuple[np.ndarray, np.ndarray]:
    """Generate synthetic domain valuation training data."""

    # --- domain_length: mix of short / medium / long ---
    # ~20% short (3-5), ~50% medium (6-9), ~30% long (10-20)
    short_n = int(n * 0.20)
    medium_n = int(n * 0.50)
    long_n = n - short_n - medium_n

    domain_length = np.concatenate(
        [
            RNG.integers(3, 6, short_n),   # 3-5
            RNG.integers(6, 10, medium_n),  # 6-9
            RNG.integers(10, 21, long_n),   # 10-20
        ]
    )

    # --- tld_length: encode TLD type as length proxy ---
    # .com=3, .io=2, .ai=2, .net=3, .org=3, .co=2, .info=4
    # Assign TLD type per sample; use tld_length for feature
    tld_options = [
        (3, 2.0),   # .com  — 2x multiplier vs baseline
        (2, 1.5),   # .io   — 1.5x
        (2, 1.5),   # .ai   — 1.5x
        (3, 1.0),   # .net  — baseline
        (3, 0.8),   # .org  — 0.8x (slightly below baseline .net)
        (2, 1.2),   # .co   — 1.2x
        (4, 0.6),   # .info — 0.6x
    ]
    tld_weights = np.array([0.40, 0.15, 0.15, 0.10, 0.10, 0.05, 0.05])
    tld_indices = RNG.choice(len(tld_options), size=n, p=tld_weights)
    tld_lengths = np.array([tld_options[i][0] for i in tld_indices])
    tld_multipliers = np.array([tld_options[i][1] for i in tld_indices])

    # --- vowel_count: correlated with domain_length, ~30-40% of chars ---
    vowel_ratio = RNG.uniform(0.15, 0.60, n)
    vowel_count = np.clip(
        np.round(vowel_ratio * domain_length).astype(int), 0, domain_length
    )

    # --- trends_score: 0-100, skewed toward lower scores ---
    trends_score = np.clip(RNG.beta(1.5, 4.0, n) * 100, 0, 100)

    # --- moz_da: 0-100, most domains have low DA ---
    moz_da = np.clip(RNG.beta(1.2, 5.0, n) * 100, 0, 100)

    # --- base value by domain length ---
    base_value = np.where(
        domain_length <= 5,
        RNG.uniform(5000, 50000, n),
        np.where(
            domain_length <= 9,
            RNG.uniform(200, 5000, n),
            RNG.uniform(10, 200, n),
        ),
    )

    # --- TLD multiplier ---
    value = base_value * tld_multipliers

    # --- High vowel ratio (>40%) slightly lowers value ---
    high_vowel_mask = vowel_ratio > 0.40
    value = np.where(high_vowel_mask, value * RNG.uniform(0.70, 0.90, n), value)

    # --- Trends score multiplier (1.0 at score=0, up to 3x at score=100) ---
    trends_mult = 1.0 + (trends_score / 100.0) * 2.0  # 1.0 – 3.0
    value = value * trends_mult

    # --- Moz DA multiplier (1.0 at DA=0, up to 5x at DA=100) ---
    da_mult = 1.0 + (moz_da / 100.0) * 4.0  # 1.0 – 5.0
    value = value * da_mult

    # --- Gaussian noise (~15% std) to prevent overfitting ---
    noise = RNG.normal(1.0, 0.15, n)
    value = np.clip(value * noise, 1.0, None)

    X = np.column_stack(
        [domain_length, tld_lengths, vowel_count, trends_score, moz_da]
    ).astype(np.float32)
    y = value.astype(np.float32)

    return X, y


def main() -> None:
    print(f"Generating {N} synthetic training samples…")
    X, y = generate_samples(N)

    print(f"  X shape: {X.shape}  |  y range: ${y.min():.0f} – ${y.max():.0f}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = XGBRegressor(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
    )

    print("Training XGBRegressor…")
    model.fit(X_train, y_train)

    train_rmse = mean_squared_error(y_train, model.predict(X_train)) ** 0.5
    test_rmse = mean_squared_error(y_test, model.predict(X_test)) ** 0.5
    print(f"  Train RMSE: ${train_rmse:,.0f}")
    print(f"  Test  RMSE: ${test_rmse:,.0f}")

    feature_names = ["domain_length", "tld_length", "vowel_count", "trends_score", "moz_da"]
    importances = model.feature_importances_
    print("\nFeature importances:")
    for name, imp in sorted(zip(feature_names, importances), key=lambda x: -x[1]):
        bar = "#" * int(imp * 40)
        print(f"  {name:<15} {imp:.4f}  {bar}")

    artifact_dir = os.path.dirname(ARTIFACT_PATH)
    os.makedirs(artifact_dir, exist_ok=True)
    joblib.dump(model, ARTIFACT_PATH)
    print(f"\nModel saved to: {ARTIFACT_PATH}")


if __name__ == "__main__":
    main()
