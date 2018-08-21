To begin building the redistributable, execute the `create.py` python script with a single argument containing the path to the root directory containing the compiler stack (what you --prefix everything to). Example:

```bash
  ./create_package.py --packages-dir /opt/moose
```

The script will attempt to determine OS type and build the correct package using that platforms package management tools. Unfortunately, this script is not very smart or robust. Please use the internets and search for what it takes to create a redistributable for your platform (like deb for Debian based machines. rpmbuild for CentOS/Fedora, PackageMaker for Darwin). Install those necessary packages and then run the above command. If you are lazy or in a hurry, you can always tar the prefixed path and distribute a tarball instead. Everything the make_all.py script created will reside in the prefixed directory, and as such, is the only directory we need to distribute.
