# docs/development/publishing.md

---

# Publishing

## PyPI — publishing `textprov`

All commands in this section run from the `python/` subdirectory of the repo,
where `pyproject.toml` lives. `cd` there first:

```bash
cd /Users/d/Projects/dev/textprov/textprov/python
pwd            # confirm .../textprov/textprov/python
ls pyproject.toml   # should print pyproject.toml
```

**One-time setup:**
```bash
# Create PyPI account at https://pypi.org/account/register/
# Enable 2FA, then create an API token: https://pypi.org/manage/account/token/
# Store token in ~/.pypirc:
cat > ~/.pypirc <<'EOF'
[pypi]
username = __token__
password = pypi-AgEI...<your-token>

[testpypi]
username = __token__
password = pypi-AgEI...<your-testpypi-token>
EOF
chmod 600 ~/.pypirc

pip install --upgrade build twine
```

**Per-release** (still in `python/`):
```bash
cd /Users/d/Projects/dev/textprov/textprov/python

# 1. Bump version in pyproject.toml (e.g. 0.1.0 -> 0.1.1)

# 2. Clean any prior build
rm -rf dist/ build/ *.egg-info

# 3. Build sdist + wheel
python -m build
# produces: dist/textprov-0.1.0.tar.gz and dist/textprov-0.1.0-py3-none-any.whl

# 4. Sanity check the wheel
twine check dist/*
unzip -l dist/textprov-0.1.0-py3-none-any.whl | grep mapping.json  # confirm package-data landed

# 5. Test on TestPyPI first (recommended for a 0.1.0)
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ --no-deps textprov
python -c "import textprov; print(textprov.__file__)"

# 6. Real upload
twine upload dist/*

# 7. Tag the release
git tag -a python-v0.1.0 -m "textprov python 0.1.0"
git push origin python-v0.1.0
```

**Verify:** `pip install textprov && textprov --selftest`

## npm — publishing `@textprov/decorator`

All commands in this section run from the `js/` subdirectory of the repo,
where `package.json` lives. `cd` there first:

```bash
cd /Users/d/Projects/dev/textprov/textprov/js
pwd              # confirm .../textprov/textprov/js
ls package.json  # should print package.json
```

**One-time setup:**
```bash
# Create npm account: https://www.npmjs.com/signup
# Enable 2FA (required for scoped public packages)
npm login
# For scoped packages under an org, first create the org at
# https://www.npmjs.com/org/create -- name it "textprov"

# Confirm you're logged in as the right user
npm whoami
```

**Per-release** (still in `js/`):
```bash
cd /Users/d/Projects/dev/textprov/textprov/js

# 1. Version bump (uses semver: patch|minor|major). This edits package.json
#    AND creates a git commit + tag.
npm version patch    # 0.1.0 -> 0.1.1

# 2. Dry-run to see exactly what will be published
npm publish --dry-run --access public
# Confirm the file list matches "files": [...] in package.json
# (should be textprov.js and textprov.css only, no fixtures/tests)

# 3. Test the tarball locally
npm pack
# produces textprov-decorator-0.1.1.tgz -- unpack and inspect if paranoid
tar -tzf textprov-decorator-0.1.1.tgz

# 4. Run the test suite one more time
npm test

# 5. Publish. --access public is REQUIRED the first time for scoped packages;
#    without it npm assumes private and errors.
npm publish --access public

# 6. Push the tag npm version created
git push origin main --follow-tags
```

**Verify:**
```bash
npm view @textprov/decorator
mkdir /tmp/test && cd /tmp/test && npm init -y && npm install @textprov/decorator
node -e "console.log(require('@textprov/decorator'))"
```

## Gotchas worth knowing

- **PyPI names are irrevocable.** Once you take `textprov`, you own it — you can yank a version but you cannot rename or transfer casually. Same for the npm scope `@textprov`.
- **npm 2FA on publish** — if you enabled "auth-and-writes" 2FA, every `npm publish` prompts for an OTP. Have your authenticator ready.
- **PyPI `long_description`** — your `pyproject.toml` reads `README.md`; make sure the README renders on PyPI by running `twine check dist/*` before upload. It catches RST/MD errors that would otherwise leave the project page blank.
- **First scoped npm publish** without `--access public` fails with a paid-account error even though scoped-public is free. Always pass the flag the first time.
- **Version once, publish once.** You cannot re-upload the same version to either registry, even after deletion. If a publish fails halfway, bump the patch version before retrying.
- **The `js/package.json` has no `prepublishOnly`** — add `"prepublishOnly": "node check_fixtures.mjs"` before your first publish so you can never ship a decoder that fails its own fixtures.
