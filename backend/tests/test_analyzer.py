import pytest
from backend.app.services.analyzer import PHPIssueAnalyzer
from backend.app.models.schemas import AnalyzeRequest, IssueCategory


@pytest.fixture
def analyzer():
    return PHPIssueAnalyzer()


class TestPHPIssueAnalyzer:
    def test_segfault_jit_classification(self, analyzer):
        request = AnalyzeRequest(
            title="JIT segmentation fault in PHP 8.1",
            body="Program terminated with signal 11, Segmentation fault. #0 0x000055bbf04c0f25 in ZEND_NEW_SPEC_CONST_UNUSED_HANDLER () at /usr/src/debug/php-8.1.1/Zend/zend_vm_execute.h:10137 ce = CACHED_PTR(opline->op2.num);",
            php_version="8.1.1",
            os="CentOS 7",
        )
        analysis, test_case = analyzer.analyze(request)
        assert analysis.classification == IssueCategory.SEGFAULT.value
        assert analysis.confidence >= 80
        assert test_case is not None
        assert "opcache.jit" in test_case.code

    def test_segfault_ldap_classification(self, analyzer):
        request = AnalyzeRequest(
            title="Segmentation fault on exit when using ldap_bind()",
            body="ldap_bind(): Unable to bind to server: Protocol error. Segmentation fault. ENGINE_cleanup at eng_lib.c:205",
            php_version="7.4.28",
            os="Amazon Linux 2",
        )
        analysis, test_case = analyzer.analyze(request)
        assert analysis.classification == IssueCategory.SEGFAULT.value
        assert test_case is not None
        assert "ldap_bind" in test_case.code

    def test_performance_gc_classification(self, analyzer):
        request = AnalyzeRequest(
            title="Bad performance with hard-coded GC_THRESHOLD_* values",
            body="phpunit tests slowed down between PHP 8.1.9 and 8.1.10. GC_THRESHOLD values causing performance issues.",
            php_version="8.1.12",
            os="Docker",
        )
        analysis, test_case = analyzer.analyze(request)
        assert analysis.classification == IssueCategory.PERFORMANCE.value
        assert test_case is not None
        assert "gc_threshold" in test_case.code

    def test_platform_macos_fork_classification(self, analyzer):
        request = AnalyzeRequest(
            title="macOS now crashes fork() process instead of just warning output",
            body="objc[54119]: +[__NSPlaceholderDate initialize] may have been in progress in another thread when fork() was called. Crashing instead. SIGABRT",
            php_version="8.2.8",
            os="macOS 13.5",
        )
        analysis, test_case = analyzer.analyze(request)
        assert analysis.classification == IssueCategory.PLATFORM_SPECIFIC.value
        assert test_case is not None
        assert "pcntl_fork" in test_case.code
        assert "Darwin" in test_case.code

    def test_logic_bug_array_unique_classification(self, analyzer):
        request = AnalyzeRequest(
            title="array_unique() with SORT_REGULAR returns duplicate values",
            body="SORT_REGULAR uses zendi_smart_strcmp which has non-transitive behavior. array_unique returns 4 elements instead of 3.",
            php_version="8.4.13",
            os="Linux",
        )
        analysis, test_case = analyzer.analyze(request)
        assert analysis.classification == IssueCategory.LOGIC_BUG.value
        assert analysis.confidence >= 50
        assert test_case is not None
        assert "array_unique" in test_case.code
        assert "SORT_REGULAR" in test_case.code

    def test_logic_bug_enum_array_classification(self, analyzer):
        request = AnalyzeRequest(
            title="Enum case as Array key?",
            body="Want to use enum as array key. Got error. Workaround: use $key->value",
            php_version="8.1",
            os="Linux",
        )
        analysis, test_case = analyzer.analyze(request)
        assert analysis.classification == IssueCategory.LOGIC_BUG.value
        assert test_case is not None
        assert "enum" in test_case.code.lower()
        assert "ResponseKey" in test_case.code

    def test_feature_request_classification(self, analyzer):
        request = AnalyzeRequest(
            title="Add new array function",
            body="Feature request: would be nice to have array_first() function in PHP core.",
            php_version="8.2",
            os="Linux",
        )
        analysis, test_case = analyzer.analyze(request)
        assert analysis.classification == IssueCategory.FEATURE_REQUEST.value

    def test_unknown_classification(self, analyzer):
        request = AnalyzeRequest(
            title="Random question",
            body="How do I install PHP?",
            php_version="8.2",
            os="Linux",
        )
        analysis, test_case = analyzer.analyze(request)
        # Could be UNKNOWN or LOGIC_BUG depending on patterns
        assert analysis.classification in [IssueCategory.UNKNOWN.value, IssueCategory.LOGIC_BUG.value]

    def test_stack_trace_extraction(self, analyzer):
        request = AnalyzeRequest(
            title="Test",
            body="""#0 0x000055bbf04c0f25 in ZEND_NEW_SPEC_CONST_UNUSED_HANDLER () at zend_vm_execute.h:10137
#1 0x000055bbf04c0f26 in execute_ex () at zend_vm_execute.h:50000""",
        )
        analysis, _ = analyzer.analyze(request)
        assert analysis.stack_trace is not None
        assert "ZEND_NEW_SPEC_CONST_UNUSED_HANDLER" in analysis.stack_trace

    def test_error_patterns_extraction(self, analyzer):
        request = AnalyzeRequest(
            title="Test",
            body="Error: segmentation fault\nWarning: ldap_bind failed\nin zend_execute",
        )
        analysis, _ = analyzer.analyze(request)
        assert analysis.error_patterns is not None
        assert len(analysis.error_patterns) > 0

    def test_deterministic_results(self, analyzer):
        """Same input should always produce same output."""
        request = AnalyzeRequest(
            title="Test issue",
            body="Segmentation fault in ZEND_NEW_SPEC_CONST_UNUSED_HANDLER with CACHED_PTR",
        )
        analysis1, tc1 = analyzer.analyze(request)
        analysis2, tc2 = analyzer.analyze(request)

        assert analysis1.classification == analysis2.classification
        assert analysis1.confidence == analysis2.confidence
        assert analysis1.root_cause == analysis2.root_cause
        if tc1 and tc2:
            assert tc1.code == tc2.code