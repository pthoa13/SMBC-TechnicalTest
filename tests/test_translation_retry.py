from brightlearn_site.translation.retry import RetryPolicy


def test_retry_policy_attempts_include_initial_call() -> None:
    assert RetryPolicy(max_retries=3).max_attempts == 4


def test_retry_policy_uses_exponential_backoff_with_cap() -> None:
    policy = RetryPolicy(max_retries=5, base_delay_seconds=2, max_delay_seconds=5)

    assert policy.delay_for_retry(1) == 2
    assert policy.delay_for_retry(2) == 4
    assert policy.delay_for_retry(3) == 5
