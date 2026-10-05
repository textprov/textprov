# External metadata

Status: complementary integration and alternative carriage model.

HTML attributes, native annotations, JSON, sidecars, and richer clipboard formats
can associate unchanged text with references and descriptions. Their scope,
identity, versioning, and synchronization need definition. None is an assigned
Unicode provenance character.

A plain-text-only intermediate representation can lose metadata stored outside
the character stream. Interior selection can also omit enclosing annotations.
Cooperating applications can copy or synthesize scope and metadata; that support
must be measured separately from carriage through unaware software.

These alternatives remain in the comparison. Deciding whether to relax the
plain-text copying objective is distinct from demonstrating that one in-band
candidate fails.

The [published W3C/Unicode note](https://www.w3.org/TR/2007/NOTE-unicode-xml-20070516/)
discusses replacing several in-band controls with markup in XML/HTML. Its
recommendations are specific to the character and interchange context, not a
blanket rejection of all format controls. The
[editor's draft](https://www.w3.org/International/docs/unicode-xml/) is dated 2012
and predates bidi isolates and the modern emoji-tag use. Unicode 17 and current
UAX/UTS specifications determine present character status.

Character assignment, permitted semantics, rendering support, and measured
transport behavior are separate evidence. Inclusion here does not establish
support in ordinary software. Evaluation compares raw plain-text carriage with
conversion to native markup and records any lost or altered attribution.

See the [candidate comparison](README.md), [open decisions](../decisions.md),
and [evaluation](../evaluation.md).
