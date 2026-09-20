# 0012. Use one canonical npm package and reserve the matching scope

Status: accepted. Date: 2026-09-20.

## Context

ADR 0006 names the JavaScript package `textprov`, matching the package and
import name on PyPI and the Ruby gem. The unscoped npm name gives users the
same installation name in each ecosystem and is the most direct name for
search and recognition.

npm also has the independent `@textprov` scope. If the project did not control
that scope, another publisher could use names such as `@textprov/cli` or
`@textprov/core` in a way that users might mistake for official TextProv
packages. The project has reserved the scope, which also leaves room to publish
distinct packages there if the JavaScript distribution later grows beyond one
package.

Publishing identical code as both `textprov` and, for example,
`@textprov/textprov` would not solve a user problem. It would create two
installation names, split usage and download signals, and require both
packages to remain synchronized. Publishing a placeholder package solely to
redirect users would add registry clutter and should not be part of the
namespace strategy.

## Decision

The JavaScript implementation is published as the unscoped npm package
`textprov`. It is the sole canonical npm package and the name used in
installation, documentation, examples, and support.

The project reserves the `@textprov` scope through the npm organisation of the
same name. Do not publish a package under the scope until there is a distinct,
maintained artifact that needs its own package, such as `@textprov/cli` or
`@textprov/core`.

Do not dual-publish the same artifact under scoped and unscoped names. If a
future requirement justifies moving the canonical package into the scope,
publish the replacement there, deprecate `textprov` with an npm message that
names the replacement, and update the documentation. Do not maintain both
names as equal entry points.

The npm README and package metadata identify `textprov` as the JavaScript
implementation of TextProv and describe how its API differs from the Python
and Ruby packages. Cross-ecosystem recognition belongs in that metadata
rather than in a second npm package name.

## Evidence

As of 2026-09-20, the npm registry reports `textprov@0.1.0` as the `latest`
release. The [`textprov` npm organisation](https://www.npmjs.com/org/textprov)
exists and contains no scoped packages. The project also controls
[`textprov.org`](https://textprov.org), which resolves to the TextProv project
site.

## Consequences

- Users get one unambiguous npm installation command: `npm install textprov`.
- npm, PyPI, and the Ruby gem share the recognizable `textprov` name even
  though their APIs need not be identical.
- Reserving `@textprov` reduces the chance that unofficial packages appear to
  belong to the project and preserves room for a future multi-package layout.
- Download counts, issue reports, releases, and security notices remain
  attached to one canonical JavaScript package.
- The project takes responsibility for securing and maintaining the npm
  organisation even while it contains no packages.
- A later move to a scoped package is a migration requiring deprecation and
  documentation updates rather than a transparent alias.

## Relationship to earlier decisions

This record narrows the npm naming and namespace policy. It does not change
ADR 0006's choice of `textprov` for the JavaScript package or its decision to
use matching public names across ecosystems.
