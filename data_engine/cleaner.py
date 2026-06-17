try:
    from .cleaning_steps import CLEANING_STEPS, DEFAULT_CLEANING_STEPS
except ImportError:
    from cleaning_steps import CLEANING_STEPS, DEFAULT_CLEANING_STEPS


def clean_data(df, steps=None):
    selected_steps = steps if steps is not None else DEFAULT_CLEANING_STEPS
    cleaned_df = df.copy()

    for step_id in selected_steps:
        step = CLEANING_STEPS.get(step_id)

        if step is None:
            raise ValueError(f"Unsupported cleaning step: {step_id}")

        cleaned_df = step["function"](cleaned_df)

    return cleaned_df


def get_cleaning_step_options():
    return [
        {
            "id": step_id,
            "label": step["label"],
            "description": step["description"],
        }
        for step_id, step in CLEANING_STEPS.items()
    ]
