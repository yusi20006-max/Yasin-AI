from yasinai.providers.validation import ValidationResult
from yasinai.services.batch_health import BatchHealthService

class Fake:
    def validate_credential(self, credential, model=None):
        if credential == "good": return ValidationResult(True, True, 200)
        return ValidationResult(True, False, 401, "UNAUTHORIZED", "rejected")

def test_batch_health_report_aggregates_without_secrets():
    report=BatchHealthService(lambda provider: Fake()).check([{"provider":"openai","credential":"good"},{"provider":"openai","credential":"bad-secret"}])
    assert report["total"] == 2
    assert report["states"]["HEALTHY"] == 1
    assert report["states"]["QUARANTINED"] == 1
    assert "bad-secret" not in str(report)
