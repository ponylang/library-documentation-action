## Add support for packages that have external dependencies

Documentation with full linking is now supported for libraries that
have external dependencies like the `http` package that relies on
`net_ssl`.

For this to work, a new experimental corral object `packages` must
be used. Additionally, the newish `documentation_url` that is part of
the `info` object in `corral.json` is also required.

Full documentation on corral as well as an update to add the `packages`
object is forthcoming.

