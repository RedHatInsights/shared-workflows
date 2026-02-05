# SC Environment Impact Check Scripts

This directory contains automation for detecting changes that may impact SC Environment deployments.

## Files in this Directory

### `sc_environment_impact_check.py`
Main Python script that analyzes git diffs for SC Environment impact patterns.

**Features:**
- Configurable pattern detection (paths and content regex)
- Multiple output formats (JSON, Markdown, GitHub)
- Severity levels (None, Low, Medium, High, Critical)
- Detailed recommendations for each finding
- Can fail CI/CD based on impact threshold

**Usage:**
```bash
# Basic usage
python sc_environment_impact_check.py \
  --base-ref origin/master \
  --head-ref HEAD \
  --output-format markdown

# With custom config
python sc_environment_impact_check.py \
  --base-ref origin/master \
  --head-ref HEAD \
  --config ../.github/sc-environment-impact-config.yml \
  --output-format json

# Fail on high impact (useful for CI gates)
python sc_environment_impact_check.py \
  --base-ref origin/master \
  --head-ref HEAD \
  --fail-on high
```

### `test_impact_check.sh`
Test script that validates the detection patterns work correctly.

**Usage:**
```bash
./test_impact_check.sh
```

Creates temporary test scenarios to verify:
- Database migration detection
- Kessel integration detection
- S3 configuration detection
- And more...

## Related Files

- `../.github/workflows/sc-environment-impact-check.yml` - GitHub Actions workflow
- `../.github/sc-environment-impact-config.yml` - Detection pattern configuration
- `../.github/SC_ENVIRONMENT_IMPACT_CHECK.md` - Full documentation
- `../.github/SC_ENVIRONMENT_QUICK_REFERENCE.md` - Quick reference for developers

## Usage in Your Repository

There are two ways to use this workflow:

### Option 1: Reusable Workflow (Recommended)

Create `.github/workflows/sc-impact-check.yml` in your repo:

```yaml
name: SC Environment Check

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  sc-impact:
    uses: <YOUR_ORG>/shared-workflows/.github/workflows/sc-environment-impact-check.yml@main
    # Optional: provide a custom config path in your repo
    # with:
    #   config-path: '.github/my-custom-sc-config.yml'
```

This automatically pulls the latest version of the checker. No need to copy scripts!

### Option 2: Copy Files Directly

Copy these files into your repository:
1. `.github/workflows/sc-environment-impact-check.yml`
2. `.github/scripts/sc_environment_impact_check.py`
3. `.github/sc-environment-impact-config.yml` (optional, can customize)

The workflow will run automatically on pull requests.

## Quick Start (Local Testing)

1. **Install dependencies:**
   ```bash
   pip install PyYAML
   ```

2. **Test locally:**
   ```bash
   ./test_impact_check.sh
   ```

3. **Run on your current branch:**
   ```bash
   python sc_environment_impact_check.py \
     --base-ref origin/master \
     --head-ref HEAD \
     --output-format markdown
   ```

4. **Customize patterns:**
   Edit `../.github/sc-environment-impact-config.yml`

## How Detection Works

The script:
1. Gets list of changed files between base and head refs
2. Gets the diff content for each changed file
3. **Excludes the checker tool's own files** to avoid self-detection:
   - `.github/scripts/sc_environment_impact_check.py`
   - `.github/sc-environment-impact-config.yml`
   - `.github/workflows/sc-environment-impact-check.yml`
   - `.github/scripts/SC_CHECK_README.md`
4. Checks each file against configured patterns:
   - **Path patterns**: File glob matching (e.g., `migrations/**/*.py`)
   - **Content patterns**: Regex matching in diff content
5. Assigns impact level based on matched patterns
6. Generates report with findings and recommendations

## Adding New Detection Patterns

Edit `sc-environment-impact-config.yml`:

```yaml
patterns:
  your_pattern_name:
    paths:                    # Optional: file patterns to match
      - "path/to/files/**"
    content_patterns:         # Optional: regex patterns in diff
      - "regex_pattern_here"
    impact_level: high        # none, low, medium, high, critical
    description: "What changed"
    recommendation: "What to do about it"
```

## Testing New Patterns

After adding a pattern:

1. Make a test change that should match
2. Run the checker:
   ```bash
   python sc_environment_impact_check.py --base-ref HEAD~1 --head-ref HEAD --output-format markdown
   ```
3. Verify the pattern is detected
4. Adjust regex/paths as needed

## Troubleshooting

**Pattern not matching?**
- Check regex syntax (Python regex)
- Test regex at regex101.com
- Add debug output to see what's being compared
- Check file paths are correct glob patterns

**Too many false positives?**
- Make regex more specific
- Add file path restrictions
- Lower the impact level

**False negatives?**
- Add more variations of the pattern
- Check the diff content manually
- Verify file paths are being checked

## Contributing

To improve detection patterns:
1. Test your changes locally
2. Run the test script
3. Document new patterns
4. Submit PR with examples

## Support

- 📖 Documentation: `../.github/SC_ENVIRONMENT_IMPACT_CHECK.md`
- 🔍 Quick Reference: `../.github/SC_ENVIRONMENT_QUICK_REFERENCE.md`
- 🐛 Issues: Open a GitHub issue

