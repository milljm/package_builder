To get started using the automated scripts, be sure to have a clean working developers environment.
Explaining how to create this environment for each operating system out there, is beyond the scope
of this document. Also, we have to assume the very reason you are attempting to build the
redistributable and not simply downloading one of our pre-existing redistributable packages, is
because you have extensive knowledge with your particular operating system that we have not provided
a package for.

The following is a list of dependency libraries you should install before attempting to build the
redistributable (Linux only):

```bash
gcc
gfortran
flex
bison
tcl-devel
tk-devel
python-devel
libblas-devel
liblapack-devel
freeglut3-devel
libXt-devel
ncurses-devel
libedit-devel
zlib-devel
```
Note: For Darwin machines, simply having the Xcode Command Line Tools package will suffice.
Note: Install the 'devel' arch type for all of the above where labeled.

The following is a list of executable binaries the scripts make use of:
```bash
make
curl
git
```

Hopefully, thats everything your machine requires, but in practice there's always something. If
that 'something' comes up, the script will fail, and report what 'configure/make' reported to it.
Usually that will be enough to understand what additional dependency is needed to continue.
And once you do satisfy that dependency, re-running the script will pick up where it left off.

Clone the script to where ever you wish and enter the build_from_source directory:
```bash
git clone https://github.com/idaholab/package_builder
cd package_builder/build_from_source
```

Create and chown the target directory:
```bash
sudo mkdir /some/path
sudo chown -R <your user id> /some/path
```
Note: We do this, so that the script we're about to execute does not require root privileges.
While we're on the subject, NEVER. Never trust a script you find on the internet with 'root'
privileges.

AGAIN, do not run this script as root

Engage!
```bash
./make_all.py --prefix /some/path --max-jobs <int> --cpu-count <int>
```
A word about those options:  
 --max-jobs basically means, build this many modules at the same time  
 --cpu-count is how many processors to throw at anything requiring a `make -j`  

When/If a problem arises, it will normally be a dependency issue. What ever the fix may be, once solved,
simply re-execute the same ./make_all.py script with the same set of arguments and the script will pick
up where it left off.  

On my test Macintosh workstation with 12 real cores available, I've found max-jobs set at 4 and cpu-count
set at 6 completes the entire package in roughly 1 hour 40 minutes. I have tinkered with load balancing,
but ultimately, just like the many posts out there already on the subject, `make -j` seems to: 'just works
better than make -l'.  

Maybe you can come up with an ingenious way to solve this and create a merge request!

The script will let you know when it has completed. Everything the script did, happened in your /tmp directory.
If there were any issues along the way that had you stop and restart the process, there will be temporary
directories in this location. Also the temporary downloads directory will be sitting in /tmp. It is safe to
remove this directory once the entire package has been built.


Now that everything has been built, you should test your results by sourcing the moose_profile and attempt to
build libMesh/MOOSE and run the tests:

```bash
source /some/path/environments/moose_profile
git clone https://github.com/idaholab/moose
cd moose/scripts
./update_and_rebuild_libmesh.sh
cd ../test
make -j 12
./run_tests -j 12
```


If all goes well, it should be safe to to create a redistributable package. There are several scripts which
facilitates the creation of our redistributable available in this repository. Please see the README's in
those corresponding locations for addition information:  package_builder/linux, package_builder/macintosh

