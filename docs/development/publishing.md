# Publishing packages

This guide covers manual releases of the Python, JavaScript, and Ruby packages
in this repository. Run commands from the repository root unless a section says
otherwise.

The packages have independent versions. Release and tag each package separately.
Do not reuse a package version that has already been published: package
registries treat published artifacts as immutable.

## Before any release

1. Check out the branch that should contain the release.
2. Confirm that the working tree is clean.
3. Update the package version and any package-specific release notes.
4. Run the package's tests.
5. Commit the release changes.
6. Build and inspect the exact artifact that will be uploaded from that commit.
7. Publish with an account protected by multi-factor authentication (MFA).
8. Install the published artifact in a clean environment and run a smoke test.
9. Create and push a package-specific Git tag for the release commit.

If an upload is interrupted, inspect the registry before retrying. A registry
may have accepted one artifact even if the command reported a failure.

## License files

Each package directory contains its own `LICENSE` because package build tools
normally include files from the package directory, not its parent:

```text
LICENSE          canonical repository license
python/LICENSE   included in Python distributions
js/LICENSE       included in npm packages
ruby/LICENSE     included in the Ruby gem
```

Keep every copy identical to the root file. The `license-drift` job in
`.github/workflows/conformance.yml` currently verifies the Python and
JavaScript copies. Check the Ruby copy manually until CI covers it as well.
Use copies rather than symlinks because symlinks can cause problems in Windows
checkouts and package archives.

## Publish the Python package to PyPI

### Prerequisites

- Python 3.9 or newer
- Accounts on [PyPI](https://pypi.org/account/register/) and, when testing there,
  [TestPyPI](https://test.pypi.org/account/register/)
- MFA enabled on both accounts
- A separate API token for each registry
- Current packaging tools:

```sh
python3 -m pip install --upgrade build twine
```

Do not commit tokens or place them directly in shell commands. The upload
commands below prompt for a token after `--username __token__`. A trusted
publishing workflow is preferable if releases are later automated in CI.

### Build and check the release

From the repository root:

```sh
cd python

# Update version in pyproject.toml, replace X.Y.Z below, then run the tests.
python3 -m unittest discover -s tests -t .

# Commit the version change before continuing.
git add pyproject.toml
git commit -m "release(python): X.Y.Z"

# Remove artifacts from earlier builds and build an sdist and wheel.
rm -rf build dist *.egg-info
python3 -m build

# Check package metadata and inspect both archives.
python3 -m twine check dist/*
python3 -m zipfile -l dist/*.whl

tar -tzf dist/*.tar.gz
```

Confirm that the archives contain `README.md`, `LICENSE`, the `textprov`
package, and `textprov/mapping.json`.

### Test on TestPyPI

Upload with the TestPyPI token when prompted:

```sh
python3 -m twine upload \
  --repository testpypi \
  --username __token__ \
  dist/*
```

Install the uploaded version in a clean virtual environment. Replace `X.Y.Z`
with the version in `pyproject.toml`:

```sh
rm -rf /tmp/textprov-testpypi
python3 -m venv /tmp/textprov-testpypi
/tmp/textprov-testpypi/bin/python -m pip install \
  --index-url https://test.pypi.org/simple/ \
  --no-deps \
  textprov==X.Y.Z
/tmp/textprov-testpypi/bin/textprov --version
```

TestPyPI is a separate registry. An account or token from PyPI does not grant
access to it.

### Publish and verify

```sh
python3 -m twine upload --username __token__ dist/*

rm -rf /tmp/textprov-pypi
python3 -m venv /tmp/textprov-pypi
/tmp/textprov-pypi/bin/python -m pip install textprov==X.Y.Z
/tmp/textprov-pypi/bin/textprov --version
printf 'hello' | /tmp/textprov-pypi/bin/textprov mark --human - \
  | /tmp/textprov-pypi/bin/textprov inspect -
```

From `python/`, tag the exact commit that produced the artifacts:

```sh
git tag -a python-vX.Y.Z -m "textprov python X.Y.Z"
git push origin python-vX.Y.Z
```

## Publish the JavaScript package to npm

### Prerequisites

- Node.js 18 or newer; CI uses Node.js 20
- An [npm account](https://www.npmjs.com/signup) with two-factor authentication
- Permission to publish the unscoped `textprov` package

Authenticate and verify the active account:

```sh
npm login
npm whoami
```

### Build and check the release

From the repository root:

```sh
cd js

# Choose patch, minor, or major. This updates package.json and package-lock.json
# without creating a generic Git tag.
npm version <patch|minor|major> --no-git-tag-version

npm test
npm publish --dry-run

rm -rf /tmp/textprov-npm
mkdir /tmp/textprov-npm
npm pack --pack-destination /tmp/textprov-npm
```

Inspect the file list printed by `npm publish --dry-run` and `npm pack`. The
package should contain `README.md`, `LICENSE`, `package.json`, `textprov.js`, and
`textprov.css`. `prepublishOnly` runs `npm test` again during publication.

Test the tarball in a clean temporary project. Replace `X.Y.Z` with the version
in `package.json`:

```sh
(
  cd /tmp/textprov-npm
  npm init -y
  npm install ./textprov-X.Y.Z.tgz
  node -e 'console.log(require("textprov").contractVersion)'
)
```

The subshell returns to `js/` when the test finishes. Commit the version files
before publishing:

```sh
git add package.json package-lock.json
git commit -m "release(js): X.Y.Z"
```

### Publish and verify

```sh
npm publish
npm view textprov@X.Y.Z
```

Then install the registry package in a clean temporary project:

```sh
rm -rf /tmp/textprov-npm-registry
mkdir /tmp/textprov-npm-registry
(
  cd /tmp/textprov-npm-registry
  npm init -y
  npm install textprov@X.Y.Z
  node -e 'console.log(require("textprov").contractVersion)'
)
```

From `js/`, tag the release commit. Replace `X.Y.Z` before running these
commands:

```sh
git tag -a js-vX.Y.Z -m "textprov javascript X.Y.Z"
git push origin HEAD
git push origin js-vX.Y.Z
```

## Publish the Ruby gem to RubyGems

### Prerequisites

- Ruby 3.2 or newer
- A [RubyGems account](https://rubygems.org/sign_up) with MFA enabled
- Bundler

From the repository root:

```sh
cd ruby
gem signin
bundle install
```

`gem signin` stores credentials in RubyGems' local credentials file. Use the
permissions RubyGems requests and never commit that file.

### Build and check the release

```sh
# Update Textprov::VERSION in lib/textprov/version.rb, replace X.Y.Z below,
# then run the tests.
bundle exec ruby -Ilib -rtextprov -e 'puts Textprov::VERSION'
bundle exec rake test

# Commit the version change before continuing.
git add lib/textprov/version.rb
git commit -m "release(ruby): X.Y.Z"

rm -f textprov-*.gem
gem build textprov.gemspec
```

Replace `X.Y.Z` below with the version printed above:

```sh
gem specification textprov-X.Y.Z.gem
rm -rf /tmp/textprov-gem
gem unpack textprov-X.Y.Z.gem --target /tmp/textprov-gem
find /tmp/textprov-gem/textprov-X.Y.Z -type f | sort
```

Confirm that the gem contains `README.md`, `LICENSE`, `exe/textprov`, and the
files under `lib/`. Install and test the artifact itself:

```sh
gem install --local textprov-X.Y.Z.gem
textprov --version
printf 'hello' | textprov mark --human - | textprov inspect -
```

### Publish and verify

```sh
gem push textprov-X.Y.Z.gem
gem info textprov --remote
```

RubyGems prompts for an MFA code when required. From `ruby/`, tag the exact
commit that produced the gem:

```sh
git tag -a ruby-vX.Y.Z -m "textprov ruby X.Y.Z"
git push origin ruby-vX.Y.Z
```

## Credential and release safety

- Give publishing tokens the narrowest available permissions.
- Keep MFA recovery codes separate from publishing credentials.
- Revoke and replace an exposed token immediately.
- Do not bypass tests or publish-time checks to force a release through.
- Never modify an artifact after inspecting it; rebuild, inspect, and test again.
- Verify that each release tag identifies the source used to build the published
  artifact.
