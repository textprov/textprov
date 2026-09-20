# docs/development/publishing.md

---

# Publishing

## LICENSE — one file per package directory

Both PyPI sdists and npm tarballs are meant to be self-contained: their build
tools only read files inside the package directory, not parent paths. So each
package directory keeps its own copy of the license:

```
LICENSE                # canonical
python/LICENSE         # copy, consumed by setuptools via license-files
js/LICENSE             # copy, auto-detected by npm
```

The `license-drift` job in `.github/workflows/conformance.yml` fails CI if the
copies diverge from the root. If you ever relicense, update all three files in
the same commit. This is what protobuf, grpc, and Apache Arrow do; symlinks
work locally but break on Windows checkouts and confuse some archive tools.

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

# 1. Bump version in pyproject.toml (e.g. 0.1.0 -> 0.1.1).
#    `textprov/__init__.py` reads it from installed metadata, so nothing else
#    to edit. Confirm with:
#      python -c "import textprov; print(textprov.__version__)"
#    (run after `pip install -e .` so metadata reflects the new number)

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
git tag -a python-v0.1.2 -m "textprov python 0.1.2"
git push origin python-v0.1.2
```

**Verify:**
```bash
pip install textprov
textprov --version                                    # prints "textprov 0.1.0 (contract 1, mapping 1)"
echo -n "hello" | textprov mark --human - | textprov inspect -
```

## npm — publishing `textprov`

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
# Enable 2FA on the account
npm login
npm whoami   # confirm the right user
```

**Per-release** (still in `js/`):
```bash
cd /Users/d/Projects/dev/textprov/textprov/js

# 1. Version bump (uses semver: patch|minor|major). This edits package.json
#    AND creates a git commit + tag.
npm version patch    # 0.1.0 -> 0.1.1

# 2. Dry-run to see exactly what will be published
npm publish --dry-run
# Confirm the file list matches "files": [...] in package.json
# (should be README, LICENSE, package.json, textprov.js, textprov.css)

# 3. Test the tarball locally. npm pack names the file after the version
#    in package.json; the command below reads it back out.
npm pack
tar -tzf "textprov-$(node -p 'require("./package.json").version').tgz"

# 4. Run the test suite one more time
npm test

# 5. Publish. Unscoped packages default to public, no flag needed.
npm publish

# 6. Push the tag npm version created
git push origin main --follow-tags
```

**Verify:**
```bash
npm view textprov
mkdir /tmp/test && cd /tmp/test && npm init -y && npm install textprov
node -e "console.log(require('textprov'))"
```

## Gotchas worth knowing

- **Registry names are irrevocable.** Once you take `textprov` on PyPI or npm, you own it — you can yank a version but you cannot rename or transfer casually.
- **npm 2FA on publish** — if you enabled "auth-and-writes" 2FA, every `npm publish` prompts for an OTP. Have your authenticator ready.
- **PyPI `long_description`** — your `pyproject.toml` reads `README.md`; make sure the README renders on PyPI by running `twine check dist/*` before upload. It catches RST/MD errors that would otherwise leave the project page blank.
- **Version once, publish once.** You cannot re-upload the same version to either registry, even after deletion. If a publish fails halfway, bump the patch version before retrying.
- **`prepublishOnly` runs `npm test`.** Any test failure aborts the publish before the tarball leaves your machine. Don't disable it.
