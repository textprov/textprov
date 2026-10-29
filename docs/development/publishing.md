# Publishing packages

Maintainers use this guide to prepare and release the Python, JavaScript, and
Ruby packages. Run commands from the repository root unless a section says
otherwise.

The packages have independent versions and release tags. This release prepares
Python at **0.2.0**, JavaScript at **0.2.1**, and Ruby at **0.1.2**. For later
releases, replace those versions in the commands with the version being
released. Never reuse a published version, and never reuse a release tag: tags
are immutable here, so a failed release is retried by bumping the package
version and cutting a new tag, not by moving or recreating the old one.

## Release model and safety

Tag pushes publish packages; they are not a post-publication bookkeeping step.
The npm release is staged rather than published directly: the workflow submits
the tarball to the package's staged queue and a maintainer approves it with 2FA.

| Tag | Version source | Workflow | GitHub environment |
| --- | --- | --- | --- |
| `python-v0.2.0` | `python/textprov/_version.py` | `publish-python.yml` | `pypi` |
| `js-v0.2.1` | `js/package.json` and `js/package-lock.json` | `publish-js.yml` | `npm` |
| `ruby-v0.1.2` | `ruby/lib/textprov/version.rb` | `publish-ruby.yml` | `rubygems` |

All three workflows reject a tag that does not exactly match its package version.
The JavaScript workflow also checks both root version entries in the lockfile.
Build/test jobs have only `contents: read`; checkout does not retain credentials.
Only the separate publishing jobs have `id-token: write`. They download the
artifacts tested by the build jobs rather than rebuilding them. No PyPI API
token, npm write token, or long-lived RubyGems API key is required. The npm
version is not public until a maintainer approves the staged package.

Before a maintainer creates or pushes a release tag:

1. Complete the registry and GitHub setup below.
2. Update the version sources and run the local checks and artifact smoke tests.
3. Review and commit the intended release changes. Confirm a clean working tree
   and successful [existing checks](../../.github/workflows/checks.yml) on that
   exact commit, including its Python 3.9/3.13 matrix. These checks do not run on
   tag pushes; the release workflows repeat the package-specific checks.
4. Protect release tags with GitHub rulesets. Restrict environment deployments
   to the corresponding release tags and require a maintainer approval.
5. Push only the intended package tag. Review the build results before approving
   its environment deployment. For npm, also approve the staged package after
   the workflow finishes.

Local preparation does not require any commit, tag, push, or publish operation.
The commands in the final release section are for the maintainer who authorizes
publication, not for a preparation-only session.

## One-time registry setup

### PyPI trusted publisher

A PyPI project owner must configure a
[GitHub Actions trusted publisher](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)
for the `textprov` project:

- Owner: `textprov`
- Repository: `textprov`
- Workflow filename: `publish-python.yml` (filename only)
- Environment: `pypi`

Create the `pypi` environment in GitHub with the protections described above.
Keep MFA enabled on maintainer accounts. If the project does not yet exist,
configure a [pending publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)
instead. This authorizes the first release without adding a token to GitHub.
TestPyPI is a separate registry with separate publisher configuration; this
workflow publishes only to production PyPI.

### npm trusted publisher and provenance

An npm package maintainer must configure a
[trusted publisher](https://docs.npmjs.com/trusted-publishers/)
in the existing `textprov` package's settings:

- Provider: GitHub Actions
- Organization or user: `textprov`
- Repository: `textprov`
- Workflow filename: `publish-js.yml` (filename only)
- Environment: `npm`
- Allowed actions: `npm stage publish` only. Do not allow direct `npm publish`;
  the workflow runs `npm stage publish` and a direct-publish permission is not
  needed. Separate `npm dist-tag` permissions are not needed either.

Create the `npm` environment in GitHub with deployment protections. Newly
configured npm publishers must complete their first successful publication
within two days; recreate an expired configuration before releasing. If the
package does not yet exist, a maintainer must bootstrap it through npm's
interactive publication process before configuring its trusted publisher.
Do not add a long-lived token as a silent fallback.

npm OIDC requires **Node >=22.14.0 and npm >=11.5.1**, and staged publishing
requires **npm >=11.15.0**. The release workflow uses Node 24 LTS and explicitly
installs npm 11; do not rely on the npm version bundled with a runner. Use
GitHub-hosted runners. The repository and package must be public for
`--provenance`; `js/package.json`'s `repository.url` must match
`https://github.com/textprov/textprov`. The workflow explicitly uses
`npm stage publish --provenance --access public` on the tested tarball.
`npm stage publish` accepts the same package spec as `npm publish`, so it
submits the exact tarball the build job tested.

A staged version occupies its version number: it cannot be staged or published
again under the same version until it is rejected. Rejecting a staged package
frees the version for re-staging. A staged tag cannot be changed after
staging; reject and re-stage instead.

Keep account 2FA enabled. Once trusted publishing is working, npm recommends
"Require two-factor authentication and disallow tokens" in package publishing
access settings, then revoking obsolete automation tokens. `npm whoami` does
not validate OIDC trust. Registry setup cannot be proven by a local dry run.

### RubyGems trusted publisher

A `textprov` gem owner must configure a
[trusted publisher](https://guides.rubygems.org/trusted-publishing/) on RubyGems.org:

- Repository owner: `textprov`
- Repository name: `textprov`
- Workflow filename: `publish-ruby.yml`
- Environment: `rubygems`

Create the matching GitHub environment with deployment protections. The workflow
exchanges its GitHub OIDC identity for short-lived gem-push credentials, then
pushes the same `.gem` artifact that passed the build job's installed-gem smoke
test. It does not create commits or tags and does not require repository write
permission. Registry authentication must be verified by a real authorized release;
local tests do not validate trusted-publisher setup.

## Local checks

Use Python 3.13 and Node 24 LTS for release preparation, with npm 11. The
Python package supports Python >=3.9; the existing checks run 3.9 and 3.13.
The existing JavaScript checks use Node 22. The published JavaScript package's
`node >=18` engine declaration is not the release tooling requirement; its
current development dependencies require a newer Node version.

Python's `pyproject.toml` declares a **dynamic** version from
`textprov._version.__version__`. Change `python/textprov/_version.py`, not a
static `project.version` field. For JavaScript, change `js/package.json` and
both package-root version entries in `js/package-lock.json` together, without
creating a Git tag.

These commands mirror the relevant jobs in `checks.yml`:

```sh
python3 tools/check_docs.py
python3 tools/sync_display_styles.py --check
diff -q python/LICENSE js/LICENSE
diff -q python/LICENSE ruby/LICENSE
(cd python && python3 -m unittest discover -s tests -t .)
PYTHONPATH=python python3 -m unittest discover -s plugins/codex/tests -v
(cd js && npm ci && npm test)
```

The remaining Ruby and site jobs in `checks.yml` are still required before a
release. Ruby packaging is described below; site deployment is separate.
The license check compares the package copies with each other, not with the
root `LICENSE` (which is a repository license overview).

## Build and smoke-test Python artifacts

Use isolated tooling and output directories so old artifacts are not uploaded.
The following commands prepare the current 0.2.0 release:

```sh
python3 -m venv python/dist/release-tools
python/dist/release-tools/bin/python -m pip install --upgrade build twine
rm -rf python/dist/release-0.2.0
python/dist/release-tools/bin/python -m build --outdir python/dist/release-0.2.0 python
python/dist/release-tools/bin/python -m twine check python/dist/release-0.2.0/*
python3 -m zipfile -l python/dist/release-0.2.0/textprov-0.2.0-py3-none-any.whl
tar -tzf python/dist/release-0.2.0/textprov-0.2.0.tar.gz
```

Inspect both archives. The sdist includes `README.md` and `LICENSE`; the wheel
includes distribution metadata, its license, and the `textprov` modules. Both
must include `textprov/mapping.json` and `textprov/textprov.css`.

Install **each** artifact into a clean environment, outside the Python source
directory so imports cannot accidentally resolve to the checkout. Installing
the sdist also verifies that a wheel can be built from its contents:

```sh
for artifact in python/dist/release-0.2.0/*.whl python/dist/release-0.2.0/*.tar.gz; do
  python3 -m venv --clear python/dist/release-smoke
  python/dist/release-smoke/bin/python -m pip install "$artifact"
  python/dist/release-smoke/bin/python -c 'import importlib.metadata, textprov; from textprov.chronicle import Chronicle; from textprov.prose import ProseEditor; assert textprov.__version__ == importlib.metadata.version("textprov") == "0.2.0"; assert callable(Chronicle.transfer)'
  python/dist/release-smoke/bin/textprov --version
  printf 'hello' | python/dist/release-smoke/bin/textprov mark --human - | python/dist/release-smoke/bin/textprov inspect -
done
```

The version must print `0.2.0`. Inspecting the marked `hello` should report
`human: 5` and `unmarked: 0`. The contract check mirrors the installed-package
imports in CI.
The [Python release workflow](../../.github/workflows/publish-python.yml)
builds fresh artifacts, runs Twine, and tests both archives before publishing.

## Pack and smoke-test JavaScript

No transpilation or bundle build is required. `npm test` runs
`check_fixtures.mjs` and `check_render.mjs`; `prepublishOnly` also runs those
tests when publishing a source directory. The workflow tests before packing
because it publishes a tarball, not the source directory.

Run from `js/`:

```sh
npm ci
npm test
npm publish --dry-run
mkdir -p node_modules/.release-artifacts
npm pack --pack-destination node_modules/.release-artifacts
npm install --prefix node_modules/.release-smoke --ignore-scripts --no-audit --no-fund ./node_modules/.release-artifacts/textprov-0.2.1.tgz
node <<'JS'
const assert = require('node:assert/strict');
const fs = require('node:fs');
const root = './node_modules/.release-smoke/node_modules/textprov';
const pkg = require(root + '/package.json');
const textprov = require(root);
assert.equal(pkg.version, '0.2.1');
assert.equal(textprov.specVersion, '0.2');
assert.equal(typeof textprov.runs, 'function');
assert.equal(typeof textprov.render, 'function');
assert.ok(fs.readFileSync(require.resolve('textprov/textprov.css', { paths: ['./node_modules/.release-smoke'] }), 'utf8').length);
JS
```

`npm ci` removes any previous `node_modules` tree, so the smoke project starts
clean. Inspect the pack listing: `README.md`, `LICENSE`, `package.json`,
`textprov.js`, and `textprov.css` should be present, without tests or development
dependencies. The smoke test checks the package version separately from the
TextProv specification version (`0.2`).

The [JavaScript release workflow](../../.github/workflows/publish-js.yml)
performs the same tests and tarball smoke check before its publishing job.

## Build and smoke-test the Ruby gem

Use Ruby 3.4, matching `checks.yml` and the release workflow. From `ruby/`:

```sh
bundle install
bundle exec rake test
mkdir -p pkg/release
gem build textprov.gemspec --output pkg/release/textprov.gem
gem install --local pkg/release/textprov.gem --no-document --install-dir pkg/smoke
GEM_HOME="$PWD/pkg/smoke" GEM_PATH="$PWD/pkg/smoke" ruby -r textprov -e 'abort unless Textprov.strip_marks(Textprov.mark("hello", state: "ai")) == "hello"; abort if Textprov.stylesheet.empty?'
GEM_HOME="$PWD/pkg/smoke" GEM_PATH="$PWD/pkg/smoke" pkg/smoke/bin/textprov --version
```

Use an empty `pkg/release` and `pkg/smoke` for each release check. The gem must
include `LICENSE`, `README.md`, the executable, Ruby modules, mapping, and CSS.
The [Ruby release workflow](../../.github/workflows/publish-ruby.yml) additionally
checks the installed gem's version against the tag, confirms it loads from the
isolated install directory, and exercises CLI marking and inspection.

After bumping and committing the Ruby version, create an annotated
`ruby-v0.1.2` tag matching `Textprov::VERSION` and push that tag to trigger
publication. `ruby-v0.1.0` is already published and `ruby-v0.1.1` is a spent
tag from a failed run; neither may be reused. After publication, install the
new version from RubyGems.org into a fresh directory and repeat the smoke
checks without `--local` or a source-checkout load path.

## Maintainer-authorized release

**The following commands trigger real publication. Do not run them during
local preparation.** After committing and reviewing the release changes, tag
the exact tested commit. Push each package tag separately, only when ready:

```sh
git tag -a python-v0.2.0 -m "textprov python 0.2.0"
git push origin python-v0.2.0

# Independent npm release:
git tag -a js-v0.2.1 -m "textprov javascript 0.2.1"
git push origin js-v0.2.1

# Independent RubyGems release:
git tag -a ruby-v0.1.2 -m "textprov ruby 0.1.2"
git push origin ruby-v0.1.2
```

Review the corresponding Actions run and approve the environment deployment.
Never move an already published release tag or rebuild a different commit
under the same version. If publication fails or is interrupted, inspect the
registry first: it may have accepted some or all artifacts. Do not blindly
retry a partial PyPI upload or disable tests to force a release.

The npm workflow ends with the version staged, not published. The workflow log
prints the stage id. A maintainer with publish access and 2FA then reviews and
approves it, from any machine with npm 11.15 or newer:

```sh
npm stage list textprov
npm stage view <stage-id>
npm stage download <stage-id>   # optional: inspect the tarball
npm stage approve <stage-id>    # prompts for 2FA; the version goes public
```

The Staged Packages tab on npmjs.com offers the same review and approval.
`npm stage reject <stage-id>` removes a staged version and frees its version
number. The registry checks below require the approval to have completed.

After successful publication, verify registry installs in new environments:

```sh
python3 -m venv --clear python/dist/registry-smoke
python/dist/registry-smoke/bin/python -m pip install --no-cache-dir textprov==0.2.0
python/dist/registry-smoke/bin/textprov --version
printf 'hello' | python/dist/registry-smoke/bin/textprov mark --human - | python/dist/registry-smoke/bin/textprov inspect -

# From js/ after the local checks above:
npm view textprov@0.2.1 version dist.attestations
rm -rf node_modules/.registry-smoke
npm install --prefix node_modules/.registry-smoke --ignore-scripts --no-audit --no-fund textprov@0.2.1
node -e 'const assert = require("node:assert/strict"); const root = "./node_modules/.registry-smoke/node_modules/textprov"; assert.equal(require(root + "/package.json").version, "0.2.1"); assert.equal(require(root).specVersion, "0.2")'
```

Confirm npm's provenance attestation on the registry as well as the installed
version. These registry checks are post-release operations, not local smoke
tests, and require the release to exist.
