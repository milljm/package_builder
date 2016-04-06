To begin building the redistributable, execute the `create.py` python
script with a single argument containing the path to the root directory
containing the compiler stack (what you --prefix'd everything to). Example:

```bash
  ./create_package.py --packages-dir /opt/moose
```

The script will attempt to determine OS type and build the correct
package. If unable to automatically determine OS, you can specify
the OS with additional arguments. Use --help to view all options.
