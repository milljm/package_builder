# Build from Source
The following scripts are used in order to build everything that ends up in our redistributable package.

To get started, be sure to have a clean environment. That is, a machine which is more or less 'right out of the box'. Your goal should be to produce a compiler stack which you can transport to another machine of the same build and just have it work. The best way to do this, is to always work with a vanilla install of the target OS. Not your day-to-day machine which might have a great many other packages in play.

## Prerequisites
Due to the many different ways packages can be named, you may have to search for your specific operating systems equivalent. The following two popular distribution examples are provided to help you out.

Install the following packages which are necessary to build from source, everything that will be included in the MOOSE Environment stack.

Debian based:
```bash
apt-get install \
git \
curl \
patch \
build-essential \
gfortran \
flex \
bison \
tcl-dev \
tk-dev \
python-dev \
libblas-dev \
liblapack-dev \
freeglut3-dev \
libxt-dev \
libncurses5-dev \
libedit-dev \
zlib1g-dev \
libperl-dev
```

RedHat (CentOS):
```bash
yum install \
git \
curl \
patch \
gcc \
gcc-c++ \
gcc-gfortran \
flex \
bison \
tcl-devel \
tk-devel \
python-devel \
libblas-devel \
liblapack-devel \
freeglut3-devel \
libXt-devel \
ncurses-devel \
libedit-devel \
zlib-devel \
libperl-devel
```

For Darwin machines, simply having Xcode and Xcode Command Line Tools package will suffice.

Hopefully, thats everything your machine requires, but in practice there's always something. If that 'something' comes up, the script will fail, and report what 'configure/make' reported to it. Usually that will be enough to understand what additional dependency is needed to continue. And once you do satisfy that dependency, re-running the script will pick up where it left off.

## Clone Repo
Clone the repository anywhere you would like:
```bash
git clone https://github.com/idaholab/package_builder.git
```

## Create Prefix Location
Create and chown the target directory:
```bash
sudo mkdir -p /opt/moose
sudo chown -R <your user id> /opt/moose
```
/opt/moose can be any location you wish. Keep in mind the *inx standard is to place optional packages such as the one we are about to create in the /opt directory. Which is why the MOOSE group uses /opt/moose

We chown the target directory so that the scripts we're about to execute do not require root privileges. Otherwise you would be asked for sudo's password an untold number of times throughout the build process. But most importantly we do it because: NEVER. Never trust a script you find on the internet with 'root' privileges.

## Execute
AGAIN, do not run this script as root. It would work, but thats just bad admin practices.
```bash
cd package_builder/build_from_source
./make_all.py --prefix /some/path --max-jobs <int> --cpu-count <int>
```
A word about those options:
 --max-jobs basically means, build this many modules at the same time
 --cpu-count is how many processors to throw at anything requiring a `make -j`

When/If a problem arises, it will normally be a dependency issue. What ever the fix may be, once solved, simply re-execute the same ./make_all.py script with the same set of arguments and the script will pick up where it left off.

On my test Macintosh workstation with 12 real cores available, I've found max-jobs set at 4 and cpu-count set at 6 completes the entire package in roughly 1 hour 40 minutes. I have tinkered with load balancing, but ultimately, just like the many posts out there already on the subject, `make -j` seems to: 'just works better than make -l'.

Maybe you can come up with an ingenious way to solve this and create a merge request!

The script will let you know when it has completed. Everything the script did, happened in your system's tmp directory; normally in: /tmp. If there were any issues along the way that had you stop and restart the process, there may be temporary directories in this location (if you used the --keep-failed argument). Everything that was downloaded will also be in this location (/tmp/moose_package_download_temp). The moose_package_download_temp directory does not get deleted automatically by design. This allows for rapid building on a machine in which failures are frequent (this is why I wrote these scripts!).

On Darwin machines the temp directory is a bit more obscure. /tmp exists... and is writable, but is not 'truly' the correct location. Bet you didn't that! You can figure out what your true temporary location is by running the following python commands:
```python
import tempfile
print tempfile.gettempdir()
```

## Test the Compiler Stack
Now that everything has been built, you should test this compiler stack by sourcing the moose_profile and attempt to build libMesh/MOOSE and run the tests:

```bash
source /some/path/environments/moose_profile
git clone https://github.com/idaholab/moose
cd moose/scripts
./update_and_rebuild_libmesh.sh
cd ../test
make -j 12
./run_tests -j 12
```

If all goes well, it should be safe to to create a redistributable package. The package_builder repository contains a helper script for this process. Please see the README.md file located in package_builder/create_redistributable/.
