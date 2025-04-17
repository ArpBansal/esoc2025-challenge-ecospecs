Fine-Tuning not used for trial task.

Reason:
    Given the small dataset (3 cases, 9 documents), fine-tuning large models is not feasible.

Initial Model used:
    Qwen/Qwen2.5-7B-Instruct-AWQ in local env, Although to increase the performance we should use bigger model.
    Or using GEMINI model via GEMINI API, but as use of open-source model is preferred. Proprietary model is avoided.
    128K - context window -> Qwen 2.5 models

In high-vram available environment, we can use like qwen QWQ-32B model.