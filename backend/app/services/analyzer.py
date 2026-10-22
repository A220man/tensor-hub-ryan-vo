import re
import json
from typing import List, Optional, Dict, Any
from backend.app.models.schemas import IssueCategory, AnalyzeRequest, AnalysisCreate, TestCaseCreate


class PHPIssueAnalyzer:
    """Deterministic PHP issue analyzer - no LLM required."""

    # Patterns for classification
    SEGFAULT_PATTERNS = [
        r"segmentation fault",
        r"segfault",
        r"signal 11",
        r"signal 6",
        r"SIGSEGV",
        r"SIGABRT",
        r"core dump",
        r"Cannot access memory at address",
        r"ZEND_.*_HANDLER",
        r"zend_vm_execute",
        r"CACHED_PTR",
    ]

    PERFORMANCE_PATTERNS = [
        r"performance",
        r"slow",
        r"slowdown",
        r"regression",
        r"GC_THRESHOLD",
        r"garbage collection",
        r"timing",
        r"benchmark",
    ]

    MEMORY_PATTERNS = [
        r"memory leak",
        r"out of memory",
        r"OOM",
        r"memory usage",
        r"memory_limit",
        r"allocation",
    ]

    PLATFORM_PATTERNS = [
        r"macos",
        r"darwin",
        r"objc",
        r"fork",
        r"__NSPlaceholderDate",
        r"initializeAfterForkError",
        r"centos",
        r"amazon linux",
        r"homebrew",
    ]

    LOGIC_BUG_PATTERNS = [
        r"array_unique",
        r"sort",
        r"comparison",
        r"transitive",
        r"duplicate",
        r"wrong result",
        r"incorrect",
        r"unexpected",
        r"enum.*array",
        r"SORT_REGULAR",
    ]

    FEATURE_REQUEST_PATTERNS = [
        r"feature request",
        r"can this be implemented",
        r"would be nice",
        r"proposal",
        r"rfc",
    ]

    # Stack trace extraction
    STACK_TRACE_PATTERN = re.compile(
        r"(?:^|\n)(?:#\d+\s+)?0x[0-9a-f]+\s+in\s+\w+.*?(?:\n|$)",
        re.MULTILINE | re.IGNORECASE
    )

    GDB_FRAME_PATTERN = re.compile(
        r"#\d+\s+0x[0-9a-f]+\s+in\s+(\w+)\s+\(\)\s+at\s+(.+?):(\d+)",
        re.MULTILINE
    )

    PHP_VERSION_PATTERN = re.compile(
        r"PHP\s+(\d+\.\d+\.\d+)",
        re.IGNORECASE
    )

    def analyze(self, request: AnalyzeRequest) -> tuple[AnalysisCreate, Optional[TestCaseCreate]]:
        text = f"{request.title}\n{request.body}".lower()

        # Classify
        category = self._classify(text)

        # Extract stack trace
        stack_trace = self._extract_stack_trace(request.body)

        # Extract error patterns
        error_patterns = self._extract_error_patterns(request.body)

        # Determine root cause and suggested fix
        root_cause, suggested_fix, confidence = self._determine_root_cause(
            category, request.title, request.body, stack_trace, error_patterns
        )

        # Generate test case
        test_case = self._generate_test_case(category, request.title, request.body, error_patterns)

        analysis = AnalysisCreate(
            classification=category.value,
            stack_trace=stack_trace,
            error_patterns=error_patterns,
            root_cause=root_cause,
            suggested_fix=suggested_fix,
            confidence=confidence,
        )

        return analysis, test_case

    def _classify(self, text: str) -> IssueCategory:
        scores = {
            IssueCategory.SEGFAULT: sum(1 for p in self.SEGFAULT_PATTERNS if re.search(p, text, re.IGNORECASE)),
            IssueCategory.PERFORMANCE: sum(1 for p in self.PERFORMANCE_PATTERNS if re.search(p, text, re.IGNORECASE)),
            IssueCategory.MEMORY: sum(1 for p in self.MEMORY_PATTERNS if re.search(p, text, re.IGNORECASE)),
            IssueCategory.PLATFORM_SPECIFIC: sum(1 for p in self.PLATFORM_PATTERNS if re.search(p, text, re.IGNORECASE)),
            IssueCategory.LOGIC_BUG: sum(1 for p in self.LOGIC_BUG_PATTERNS if re.search(p, text, re.IGNORECASE)),
            IssueCategory.FEATURE_REQUEST: sum(1 for p in self.FEATURE_REQUEST_PATTERNS if re.search(p, text, re.IGNORECASE)),
        }

        # Boost segfault if stack trace present
        if re.search(r"#\d+\s+0x[0-9a-f]+", text):
            scores[IssueCategory.SEGFAULT] += 2

        max_category = max(scores, key=scores.get)
        return max_category if scores[max_category] > 0 else IssueCategory.UNKNOWN

    def _extract_stack_trace(self, body: str) -> Optional[str]:
        matches = self.STACK_TRACE_PATTERN.findall(body)
        if matches:
            return "\n".join(matches[:20])  # Limit length
        gdb_matches = self.GDB_FRAME_PATTERN.findall(body)
        if gdb_matches:
            return "\n".join(f"#{i} {func} at {file}:{line}" for i, (func, file, line) in enumerate(gdb_matches[:20]))
        return None

    def _extract_error_patterns(self, body: str) -> List[str]:
        patterns = []
        # Error messages
        for match in re.finditer(r"(?:error|warning|notice):\s*(.+?)(?:\n|$)", body, re.IGNORECASE):
            patterns.append(match.group(1).strip()[:200])
        # Function names in backtraces
        for match in re.finditer(r"in\s+(\w+)\s*\(", body):
            patterns.append(match.group(1))
        # Specific PHP functions
        for func in re.findall(r"\b(zend_\w+|php_\w+|ZEND_\w+)\b", body):
            patterns.append(func)
        return list(dict.fromkeys(patterns))[:10]  # Unique, limited

    def _determine_root_cause(
        self,
        category: IssueCategory,
        title: str,
        body: str,
        stack_trace: Optional[str],
        error_patterns: List[str],
    ) -> tuple[str, str, int]:
        text = f"{title}\n{body}".lower()

        if category == IssueCategory.SEGFAULT:
            if "ZEND_NEW_SPEC_CONST_UNUSED_HANDLER" in body and "CACHED_PTR" in body:
                return (
                    "JIT compilation issue in PHP 8.1: CACHED_PTR dereference in ZEND_NEW_SPEC_CONST_UNUSED_HANDLER "
                    "accesses invalid memory address. Likely related to opcache JIT tracing mode.",
                    "Disable JIT (opcache.jit=off) or upgrade to PHP 8.1.2+ where this was fixed. "
                    "Ensure opcache.enable_cli=On for CLI debugging.",
                    85
                )
            if "ldap_bind" in text and "ENGINE_cleanup" in (stack_trace or ""):
                return (
                    "OpenSSL engine cleanup order issue during PHP shutdown. curl/ldap extension "
                    "calls ENGINE_cleanup after OpenSSL engines already freed, causing double-free.",
                    "Upgrade OpenSSL or PHP. Workaround: avoid ldap_bind with ldaps:// in short-lived scripts, "
                    "or set OPENSSL_CONF to disable engine loading.",
                    80
                )
            return (
                "Segmentation fault in PHP engine. Stack trace indicates memory corruption or invalid pointer dereference.",
                "Compile PHP with --enable-debug and reproduce with gdb. Check for extension conflicts. "
                "Disable JIT and opcache to isolate.",
                60
            )

        if category == IssueCategory.PERFORMANCE:
            if "GC_THRESHOLD" in body:
                return (
                    "Hard-coded GC threshold values cause excessive garbage collection cycles in PHP 8.1.10+.",
                    "Tune gc_threshold_* ini settings or upgrade to PHP 8.2+ where GC is improved. "
                    "Consider gc_enable()/gc_collect_cycles() manual control in test suites.",
                    75
                )
            return (
                "Performance regression detected. Compare PHP versions with profiling (xdebug, tideways).",
                "Bisect PHP versions to find regression commit. Profile with perf/xdebug to identify hot paths.",
                55
            )

        if category == IssueCategory.PLATFORM_SPECIFIC:
            if "objc" in text and "fork" in text:
                return (
                    "macOS Objective-C runtime fork safety check crashes PHP-FPM children. "
                    "__NSPlaceholderDate initialize runs in parent thread, fork() child crashes on access.",
                    "Set OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES in PHP-FPM environment. "
                    "Long-term: PHP should call pthread_atfork handlers to reinitialize Objective-C runtime.",
                    90
                )
            return (
                "Platform-specific issue affecting PHP runtime behavior.",
                "Check platform-specific PHP configuration. Consult distribution packaging for patches.",
                50
            )

        if category == IssueCategory.LOGIC_BUG:
            if "array_unique" in text and "SORT_REGULAR" in text:
                return (
                    "SORT_REGULAR uses zendi_smart_strcmp which has non-transitive comparison for mixed "
                    "numeric/non-numeric strings. Sorting algorithms require transitivity; without it, "
                    "duplicates aren't grouped together, so adjacent-only dedup misses them.",
                    "Use SORT_STRING for string arrays. For mixed types, implement custom comparison "
                    "or use spl_fixedarray with manual dedup. PHP 8.4+ may fix this.",
                    95
                )
            if "enum" in text and "array" in text:
                return (
                    "PHP enums cannot be used directly as array keys. Only scalar values (int, string) "
                    "are valid array keys in PHP.",
                    "Use $enum->value as key, or implement ArrayAccess/JsonSerializable on enum. "
                    "Consider RFC for enum-as-array-key support.",
                    70
                )
            return (
                "Logic bug in PHP built-in function or engine behavior.",
                "Create minimal reproduction case. Check if fixed in newer PHP version. "
                "Report to php-src with exact version and reproduction steps.",
                55
            )

        if category == IssueCategory.FEATURE_REQUEST:
            return (
                "Feature request for PHP language or standard library enhancement.",
                "Follow PHP RFC process: https://wiki.php.net/rfc/howto. Gather community support.",
                40
            )

        return (
            "Unable to determine specific root cause from available information.",
            "Provide more details: minimal reproduction code, PHP version, OS, extensions, full stack trace.",
            30
        )

    def _generate_test_case(
        self,
        category: IssueCategory,
        title: str,
        body: str,
        error_patterns: List[str],
    ) -> Optional[TestCaseCreate]:
        text = f"{title}\n{body}".lower()

        if category == IssueCategory.SEGFAULT and "ZEND_NEW_SPEC_CONST_UNUSED_HANDLER" in body:
            return TestCaseCreate(
                language="php",
                code='<?php\n// Test case for JIT segfault in PHP 8.1\n// Run with: php -d opcache.enable=1 -d opcache.jit=tracing test.php\n\nclass TestClass {\n    public function __construct() {\n        // Trigger JIT compilation path\n        $x = new self();\n    }\n}\n\n// This may segfault in PHP 8.1.0/8.1.1 with JIT enabled\nfor ($i = 0; $i < 1000; $i++) {\n    new TestClass();\n}\necho "OK\\n";',
                description="Reproduces JIT segfault in PHP 8.1.0/8.1.1 with opcache.jit=tracing",
                expected_behavior="Should complete without segmentation fault",
            )

        if category == IssueCategory.SEGFAULT and "ldap_bind" in text:
            return TestCaseCreate(
                language="php",
                code='<?php\n// Test case for ldap_bind segfault on exit\n// Requires: php-ldap extension, OpenSSL\n\n$connection = @ldap_connect("ldaps://ldap.google.com");\nif (!$connection) {\n    echo "SKIP: Cannot connect to LDAP server\\n";\n    exit(0);\n}\n\n$result = @ldap_bind($connection, "test", "test");\n// Script should exit cleanly without segfault\necho "OK\\n";',
                description="Reproduces segfault on PHP shutdown after failed ldap_bind",
                expected_behavior="Script exits with exit code 0, no segmentation fault",
            )

        if category == IssueCategory.LOGIC_BUG and "array_unique" in text:
            return TestCaseCreate(
                language="php",
                code='<?php\n// Test case for array_unique SORT_REGULAR bug\n// https://github.com/php/php-src/issues/20262\n\n$units = [\'5\', \'10\', \'5\', \'3A\', \'5\', \'5\'];\n$unique = array_unique($units, SORT_REGULAR);\n\nprint_r($unique);\n\n// Expected: 3 elements (5, 10, 3A)\n// Bug: Returns 4 elements (5, 10, 3A, 5)\necho "Count: " . count($unique) . "\\n";\necho "Expected: 3\\n";\nif (count($unique) === 3) {\n    echo "PASS\\n";\n} else {\n    echo "FAIL: Duplicates not removed correctly\\n";\n}',
                description="Reproduces array_unique duplicate leakage with SORT_REGULAR",
                expected_behavior="Returns 3 unique values: 5, 10, 3A",
            )

        if category == IssueCategory.LOGIC_BUG and "enum" in text:
            return TestCaseCreate(
                language="php",
                code='<?php\n// Test case for enum as array key\n// PHP does not support enum cases as array keys directly\n\nenum ResponseKey: string {\n    case Message = "message";\n    case Status = "status";\n}\n\n// Workaround: use enum value\n$data = [];\n$data[ResponseKey::Message->value] = "success";\n$data[ResponseKey::Status->value] = 200;\n\nprint_r($data);\n// Expected: Array ( [message] => success [status] => 200 )\n',
                description="Demonstrates enum value workaround for array keys",
                expected_behavior="Array uses enum string values as keys",
            )

        if category == IssueCategory.PLATFORM_SPECIFIC and "fork" in text:
            return TestCaseCreate(
                language="php",
                code='<?php\n// Test case for macOS fork() crash\n// Only reproduces on macOS with Objective-C runtime\n\nif (PHP_OS_FAMILY !== "Darwin") {\n    echo "SKIP: Only relevant on macOS\\n";\n    exit(0);\n}\n\n// This triggers Objective-C initialization in parent\n$date = new DateTime();\n\n$pid = pcntl_fork();\nif ($pid === -1) {\n    die("fork failed");\n} elseif ($pid === 0) {\n    // Child process - may crash on macOS 13.5+\n    $childDate = new DateTime();\n    echo "Child OK\\n";\n    exit(0);\n} else {\n    pcntl_wait($status);\n    if (pcntl_wifsignaled($status)) {\n        echo "Child crashed with signal: " . pcntl_wtermsig($status) . "\\n";\n    } else {\n        echo "Child exited normally\\n";\n    }\n}',
                description="Reproduces macOS fork() crash due to Objective-C runtime fork safety",
                expected_behavior="Child process should not crash with SIGABRT",
            )

        if category == IssueCategory.PERFORMANCE and "GC_THRESHOLD" in body:
            return TestCaseCreate(
                language="php",
                code='<?php\n// Test case for GC performance regression\n// Compare runtime with different gc_threshold values\n\nfunction createObjects(int $count): array {\n    $objects = [];\n    for ($i = 0; $i < $count; $i++) {\n        $objects[] = new stdClass();\n    }\n    return $objects;\n}\n\n$start = microtime(true);\nfor ($i = 0; $i < 100; $i++) {\n    $objs = createObjects(1000);\n    unset($objs);\n}\n$end = microtime(true);\n\necho "Time: " . ($end - $start) . " seconds\\n";\n// Run with: php -d gc_threshold=10000 test.php\n// Compare with: php -d gc_threshold=1000000 test.php\n',
                description="Measures GC impact on object allocation/cleanup performance",
                expected_behavior="Higher gc_threshold should reduce GC overhead",
            )

        # Generic test case template
        return TestCaseCreate(
            language="php",
            code='<?php\n// Auto-generated test case template\n// Issue: ' + title + '\n\n// TODO: Add minimal reproduction code based on issue description\n\n',
            description=f"Template for issue: {title}",
            expected_behavior="Add expected behavior based on issue analysis",
        )