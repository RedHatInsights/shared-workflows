#!/usr/bin/env python3
"""
SC Environment Impact Assessment Tool

Analyzes git diffs to determine the potential impact of changes on SC Environment deployments.
Configurable via sc-environment-impact-config.yml for reuse across repositories.
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from enum import Enum
from functools import total_ordering
from pathlib import Path
from typing import List, Dict, Optional
import yaml


@total_ordering
class ImpactLevel(Enum):
    """Impact severity levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def __lt__(self, other):
        order = [self.NONE, self.LOW, self.MEDIUM, self.HIGH, self.CRITICAL]
        return order.index(self) < order.index(other)

    def __eq__(self, other):
        if isinstance(other, ImpactLevel):
            return self.value == other.value
        return False

    __hash__ = Enum.__hash__


@dataclass
class ImpactItem:
    """Represents a single item that impacts SC Environment"""
    category: str
    impact_level: ImpactLevel
    file_path: str
    description: str
    details: List[str] = field(default_factory=list)
    recommendation: Optional[str] = None


@dataclass
class ImpactReport:
    """Complete impact assessment report"""
    overall_impact: ImpactLevel
    items: List[ImpactItem] = field(default_factory=list)
    summary: Dict[str, int] = field(default_factory=dict)
    changed_files: List[str] = field(default_factory=list)

    def add_item(self, item: ImpactItem):
        """Add an impact item and update overall impact"""
        self.items.append(item)
        if item.impact_level > self.overall_impact:
            self.overall_impact = item.impact_level

    def generate_summary(self):
        """Generate summary statistics"""
        self.summary = {
            "total_items": len(self.items),
            "critical": len([i for i in self.items if i.impact_level == ImpactLevel.CRITICAL]),
            "high": len([i for i in self.items if i.impact_level == ImpactLevel.HIGH]),
            "medium": len([i for i in self.items if i.impact_level == ImpactLevel.MEDIUM]),
            "low": len([i for i in self.items if i.impact_level == ImpactLevel.LOW]),
        }


class SCEnvironmentImpactChecker:
    """Analyzes code changes for SC Environment deployment impact"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.report = ImpactReport(overall_impact=ImpactLevel.NONE)

    def _load_config(self, config_path: Optional[Path]) -> dict:
        """Load configuration file or use defaults"""
        if config_path and config_path.exists():
            with open(config_path) as f:
                return yaml.safe_load(f)

        # Default configuration
        return {
            "patterns": {
                "database_migrations": {
                    "paths": ["migrations/versions/**/*.py", "db/migrate/**/*.rb"],
                    "impact_level": "high",
                    "description": "Database migration detected",
                    "recommendation": "Review migration for SC Environment compatibility and timing requirements"
                },
                "clowdapp_config": {
                    "paths": ["deploy/clowdapp.yml", "deploy/*.yml"],
                    "impact_level": "high",
                    "description": "ClowdApp configuration change",
                    "recommendation": "Verify all changes are compatible with SC Environment"
                },
                "kessel_integration": {
                    "paths": ["**/*kessel*"],
                    "content_patterns": ["kessel", "KESSEL"],
                    "impact_level": "critical",
                    "description": "Kessel integration change",
                    "recommendation": "Kessel may is not available in SC Environment. Ensure feature flags and bypass options are configured."
                },
                "aws_s3": {
                    "content_patterns": [
                        r"S3.*bucket",
                        r"aws.*s3",
                        r"s3\.(get|put|delete|list)",
                        r"boto3.*s3",
                        r"S3_.*BUCKET"
                    ],
                    "impact_level": "high",
                    "description": "AWS S3 integration change",
                    "recommendation": "Verify S3 bucket configuration for SC Environment region and permissions"
                },
                "aws_rds": {
                    "content_patterns": [
                        r"RDS",
                        r"aws.*rds",
                        r"aurora",
                        r"database.*endpoint",
                        r"DB_HOST.*amazonaws"
                    ],
                    "impact_level": "high",
                    "description": "AWS RDS configuration change",
                    "recommendation": "Ensure RDS endpoints and credentials are configured for SC Environment"
                },
                "aws_elasticache": {
                    "content_patterns": [
                        r"elasticache",
                        r"redis.*amazonaws",
                        r"cache\..*\.amazonaws"
                    ],
                    "impact_level": "medium",
                    "description": "AWS ElastiCache configuration change",
                    "recommendation": "Verify ElastiCache endpoints for SC Environment compatibility"
                },
                "secrets_management": {
                    "content_patterns": [
                        r"secretRef",
                        r"secretName:",
                        r"secret.*key",
                        r"AWS.*SECRET"
                    ],
                    "impact_level": "medium",
                    "description": "Secrets configuration change",
                    "recommendation": "Ensure secrets are available in SC Environment secret store"
                },
                "kafka_topics": {
                    "content_patterns": [
                        r"topicName:",
                        r"KAFKA.*TOPIC",
                        r"kafkaTopics:"
                    ],
                    "impact_level": "medium",
                    "description": "Kafka topic configuration change",
                    "recommendation": "New topics may need to be created in SC Environment Kafka cluster"
                },
                "external_dependencies": {
                    "content_patterns": [
                        r"dependencies:",
                        r"http://",
                        r"https://(?!github\.com)"
                    ],
                    "impact_level": "low",
                    "description": "External dependency change",
                    "recommendation": "Verify external endpoints are accessible from SC Environment"
                },
                "environment_config": {
                    "content_patterns": [
                        r"ENV_NAME",
                        r"ENVIRONMENT",
                        r"production.*config",
                        r"stage.*config"
                    ],
                    "impact_level": "low",
                    "description": "Environment configuration change detected",
                    "recommendation": "Review environment-specific settings to ensure SC Environment is properly configured."
                },
                "feature_flags": {
                    "content_patterns": [
                        r"UNLEASH",
                        r"feature.*flag",
                        r"BYPASS_",
                        r"ENABLE_.*FEATURE"
                    ],
                    "impact_level": "low",
                    "description": "Feature flag change detected",
                    "recommendation": "Verify feature flags are properly configured for SC Environment. Test bypass options for services not available in SC Environment."
                }
            }
        }

    def get_changed_files(self, base_ref: str, head_ref: str) -> List[str]:
        """Get list of changed files between two refs"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", f"{base_ref}...{head_ref}"],
                capture_output=True,
                text=True,
                check=True
            )
            files = [f for f in result.stdout.strip().split('\n') if f]
            self.report.changed_files = files
            return files
        except subprocess.CalledProcessError as e:
            print(f"Error getting changed files: {e}", file=sys.stderr)
            return []

    def get_file_diff(self, file_path: str, base_ref: str, head_ref: str) -> str:
        """Get diff for a specific file"""
        try:
            result = subprocess.run(
                ["git", "diff", f"{base_ref}...{head_ref}", "--", file_path],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError:
            return ""

    def check_path_patterns(self, file_path: str, patterns: List[str]) -> bool:
        """Check if file path matches any of the glob patterns"""
        from fnmatch import fnmatch
        return any(fnmatch(file_path, pattern) for pattern in patterns)

    def check_content_patterns(self, diff_content: str, patterns: List[str]) -> List[Dict]:
        """Check if diff content matches any regex patterns, return matches with line numbers"""
        matches = []
        current_line = 0

        for diff_line in diff_content.split('\n'):
            # Parse hunk header for new file line number
            hunk_match = re.match(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', diff_line)
            if hunk_match:
                current_line = int(hunk_match.group(1))
                continue

            if diff_line.startswith('+') and not diff_line.startswith('+++'):
                line_content = diff_line[1:]
                for pattern in patterns:
                    found = re.findall(pattern, line_content, re.IGNORECASE)
                    for match_text in found:
                        matches.append({
                            'pattern': match_text,
                            'line_number': current_line,
                        })
                current_line += 1
            elif diff_line.startswith('-') or diff_line.startswith('---'):
                # Removed lines don't increment the new file line counter
                continue
            elif not diff_line.startswith('\\'):
                # Context line
                current_line += 1

        return matches

    def analyze_file(self, file_path: str, base_ref: str, head_ref: str):
        """Analyze a single file for SC Environment impact"""
        diff_content = self.get_file_diff(file_path, base_ref, head_ref)

        for pattern_name, pattern_config in self.config["patterns"].items():
            # Check path patterns
            path_patterns = pattern_config.get("paths", [])
            if path_patterns and not self.check_path_patterns(file_path, path_patterns):
                continue

            # Check content patterns in diff
            content_patterns = pattern_config.get("content_patterns", [])
            if content_patterns:
                matches = self.check_content_patterns(diff_content, content_patterns)
                if not matches:
                    continue

                # Deduplicate by (pattern, line_number) and limit to 5 examples
                seen = set()
                details = []
                for m in matches:
                    key = (m['pattern'], m['line_number'])
                    if key not in seen:
                        seen.add(key)
                        details.append(
                            f"Found `{m['pattern']}` in `{file_path}` at line {m['line_number']}"
                        )
                    if len(details) >= 5:
                        break
            else:
                details = []

            # Create impact item
            item = ImpactItem(
                category=pattern_name,
                impact_level=ImpactLevel(pattern_config["impact_level"]),
                file_path=file_path,
                description=pattern_config["description"],
                details=details,
                recommendation=pattern_config.get("recommendation")
            )
            self.report.add_item(item)

    def analyze(self, base_ref: str, head_ref: str) -> ImpactReport:
        """Perform full analysis of changes"""
        changed_files = self.get_changed_files(base_ref, head_ref)

        if not changed_files:
            print("No changed files detected")
            return self.report

        for file_path in changed_files:
            # Skip all files in the .github directory
            if file_path.startswith('.github/') or file_path == '.github':
                continue
            self.analyze_file(file_path, base_ref, head_ref)

        self.report.generate_summary()
        return self.report

    def format_markdown(self, pr_number: Optional[int] = None) -> str:
        """Format report as GitHub-flavored markdown"""
        impact_emoji = {
            ImpactLevel.CRITICAL: "🔴",
            ImpactLevel.HIGH: "🟠",
            ImpactLevel.MEDIUM: "🟡",
            ImpactLevel.LOW: "🟢",
            ImpactLevel.NONE: "⚪"
        }

        # Overall impact
        emoji = impact_emoji[self.report.overall_impact]
        lines = [
            "<!-- sc-environment-impact-check -->",
            "## 🏛️ SC Environment Impact Assessment",
            "",
            f"**Overall Impact:** {emoji} **{self.report.overall_impact.value.upper()}**",
            "",
        ]

        if self.report.overall_impact == ImpactLevel.NONE:
            lines += [
                "✅ No SC Environment-specific impacts detected in this PR.",
                "",
                "<details>",
                "<summary>What we checked</summary>",
                "",
                "This PR was automatically scanned for:",
                "- Database migrations",
                "- ClowdApp configuration changes",
                "- Kessel integration changes",
                "- AWS service integrations (S3, RDS, ElastiCache)",
                "- Kafka topic changes",
                "- Secrets management changes",
                "- External dependencies",
                "</details>",
            ]
            return "\n".join(lines)

        # Summary
        if self.report.summary["total_items"] > 0:
            lines += [
                "### 📊 Summary",
                "",
                f"- **Total Issues:** {self.report.summary['total_items']}",
            ]

            if self.report.summary['critical'] > 0:
                lines.append(f"- 🔴 Critical: {self.report.summary['critical']}")
            if self.report.summary['high'] > 0:
                lines.append(f"- 🟠 High: {self.report.summary['high']}")
            if self.report.summary['medium'] > 0:
                lines.append(f"- 🟡 Medium: {self.report.summary['medium']}")
            if self.report.summary['low'] > 0:
                lines.append(f"- 🟢 Low: {self.report.summary['low']}")

            lines.append("")

        # Detailed findings
        lines += ["### 🔍 Detailed Findings", ""]

        # Group by impact level
        by_level = {}
        for item in self.report.items:
            by_level.setdefault(item.impact_level, []).append(item)

        for level in [ImpactLevel.CRITICAL, ImpactLevel.HIGH, ImpactLevel.MEDIUM, ImpactLevel.LOW]:
            items = by_level.get(level, [])
            if not items:
                continue

            lines += [
                f"#### {impact_emoji[level]} {level.value.upper()} Impact",
                "",
            ]

            for item in items:
                lines += [
                    f"**{item.description}**",
                    f"- File: `{item.file_path}`",
                    f"- Category: `{item.category}`",
                ]

                if item.details:
                    lines.append("- Details:")
                    for detail in item.details:
                        lines.append(f"  - {detail}")

                if item.recommendation:
                    lines.append(f"- ⚠️ **Recommendation:** {item.recommendation}")

                lines.append("")

        # Action items
        lines += [
            "### ✅ Required Actions",
            "",
            "- [ ] Review all findings above",
            "- [ ] Verify SC Environment compatibility for all detected changes",
            "- [ ] Update deployment documentation if needed",
            "- [ ] Coordinate with ROSA Core team or deployment timeline",
            "",
        ]

        # Footer
        lines += [
            "---",
            "*This assessment was automatically generated. Please review carefully and consult with the ROSA Core team for critical/high impact changes.*",
        ]

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Assess SC Environment impact of code changes")
    parser.add_argument("--base-ref", required=True, help="Base git reference")
    parser.add_argument("--head-ref", required=True, help="Head git reference")
    parser.add_argument("--pr-number", type=int, help="Pull request number")
    parser.add_argument("--config", type=Path, help="Path to configuration file")
    parser.add_argument("--output-format", choices=["json", "markdown", "github"], default="github")
    parser.add_argument("--fail-on", choices=["critical", "high", "medium", "low"], help="Fail if impact level is at or above this threshold")

    args = parser.parse_args()

    # Load config if exists, otherwise use defaults
    config_path = args.config or Path(".github/sc-environment-impact-config.yml")
    checker = SCEnvironmentImpactChecker(config_path if config_path.exists() else None)

    # Perform analysis
    report = checker.analyze(args.base_ref, args.head_ref)

    # Output results
    if args.output_format == "json":
        # Convert report to dict
        report_dict = {
            "overall_impact": report.overall_impact.value,
            "summary": report.summary,
            "items": [asdict(item) for item in report.items],
            "changed_files": report.changed_files
        }
        # Convert ImpactLevel enums to strings
        for item in report_dict["items"]:
            item["impact_level"] = item["impact_level"].value if isinstance(item["impact_level"], ImpactLevel) else item["impact_level"]

        print(json.dumps(report_dict, indent=2))

        # Also save to file for artifact upload
        with open("/tmp/sc-environment-impact-report.json", "w") as f:
            json.dump(report_dict, f, indent=2)

    elif args.output_format in ["markdown", "github"]:
        markdown = checker.format_markdown(args.pr_number)
        print(markdown)

        # Save for GitHub Actions to read
        if args.output_format == "github":
            with open("/tmp/sc-environment-impact-comment.md", "w") as f:
                f.write(markdown)

    # Fail if threshold exceeded
    if args.fail_on:
        threshold = ImpactLevel(args.fail_on)
        if report.overall_impact >= threshold:
            print(f"\n❌ Impact level {report.overall_impact.value} meets or exceeds threshold {threshold.value}", file=sys.stderr)
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
