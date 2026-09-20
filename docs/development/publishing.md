# docs/development/publishing.md

---

# Publishing

## LICENSE — one file per package directory

PyPI sdists, npm tarballs, and RubyGems packages are meant to be self-contained:
their build tools only read files inside the package directory, not parent
paths. So each package directory keeps its own copy of the license:

```
LICENSE                # canonical
python/LICENSE         # copy, consumed by setuptools via license-files
js/LICENSE             # copy, auto-detected by npm
ruby/LICENSE           # copy, included by textprov.gemspec
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

## RubyGems — publishing `textprov`

All commands in this section run from the `ruby/` subdirectory of the repo,
where `textprov.gemspec` lives. Ruby 3.2 or newer is required.

```bash
cd /Users/d/Projects/dev/textprov/textprov/ruby
pwd                    # confirm .../textprov/textprov/ruby
ls textprov.gemspec     # should print textprov.gemspec
```

**One-time setup:**
```bash
# Create an account at https://rubygems.org/sign_up
# Enable MFA, then sign in from RubyGems:
gem signin

# Install development dependencies:
bundle install
```

`gem signin` stores a RubyGems API key in the local credentials file. Protect
that file with the permissions RubyGems requests, and do not commit it.

**Per-release** (still in `ruby/`):
```bash
cd /Users/d/Projects/dev/textprov/textprov/ruby

# 1. Bump Textprov::VERSION in lib/textprov/version.rb
#    (e.g. 0.1.0 -> 0.1.1), then confirm it:
bundle exec ruby -Ilib -rtextprov -e 'puts Textprov::VERSION'

# 2. Run the test suite
bundle exec rake test

# 3. Remove prior packages and build the gem
rm -f textprov-*.gem
gem build textprov.gemspec
# produces: textprov-0.1.1.gem

# 4. Inspect the package metadata and file list
#    (replace the version below with the version you just built)
gem specification textprov-0.1.1.gem
rm -rf /tmp/textprov-gem
gem unpack textprov-0.1.1.gem --target /tmp/textprov-gem
find /tmp/textprov-gem/textprov-0.1.1 -type f | sort
# Confirm the gem includes README.md, LICENSE, exe/textprov, and lib/**.

# 5. Install and test the exact package locally
gem install --local textprov-0.1.1.gem
textprov --version

# 6. Publish. RubyGems prompts for an MFA code when required.
gem push textprov-0.1.1.gem

# 7. Tag the release
git tag -a ruby-v0.1.1 -m "textprov ruby 0.1.1"
git push origin ruby-v0.1.1
```

**Verify:**
```bash
gem info textprov --remote
gem install textprov
textprov --version                                  # prints "textprov 0.1.1 (contract 1, mapping 1)"
echo -n "hello" | textprov mark --human - | textprov inspect -
```

## Gotchas worth knowing

- **Registry names are hard to change.** Once you take `textprov` on PyPI, npm, or RubyGems, you can yank a version but cannot casually rename or transfer the package.
- **npm 2FA on publish** — if you enabled "auth-and-writes" 2FA, every `npm publish` prompts for an OTP. Have your authenticator ready.
- **PyPI `long_description`** — your `pyproject.toml` reads `README.md`; make sure the README renders on PyPI by running `twine check dist/*` before upload. It catches RST/MD errors that would otherwise leave the project page blank.
- **Version once, publish once.** You cannot re-upload the same version to these registries, even after deletion. If a publish fails halfway, determine whether the release reached the registry before retrying; if it did, bump the patch version.
- **`prepublishOnly` runs `npm test`.** Any test failure aborts the publish before the tarball leaves your machine. Don't disable it.
