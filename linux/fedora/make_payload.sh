#!/bin/bash
if [ -z $PACKAGES_DIR ]; then
  echo 'PACKAGES_DIR not set. Can not continue.'
  exit 1
fi
#####
# Set some initial location variables
FEDORA_PACKAGE=/tmp/moose_compiler_package/FEDORA_PACKAGE
RELATIVE_PACKAGE=${PACKAGES_DIR:1}

###
# Check for a current PACKAGES_DIR, exit if not set
if ! [ -z $PACKAGES_DIR ]; then
  # Clean out previous build, if it exists
  if [ -d ~/rpmbuild/ ]; then
    echo -e "deleting previous build attempt: ~/rpmbuild"
    rm -rf ~/rpmbuild
  fi
  # Build the RPM directory structure
  mkdir -p ~/rpmbuild/SOURCES/$RELATIVE_PACKAGE ~/rpmbuild/SPECS ~/rpmbuild/BUILD ~/rpmbuild/BUILDROOT ~/rpmbuild/RPMS ~/rpmbuild/SRPMS
  cd ~/rpmbuild/SOURCES/$RELATIVE_PACKAGE
else
  echo -e 'No $PACKAGES_DIR environment variable set. Exiting.'
  exit 1
fi

#####
# Display any warnings, otherwise, the script has everything it needs
echo -e '\nBe sure to perform a cleaning operation on conda before continuing:\n\n\tconda clean --lock --tarballs --index-cache --packages --source-cache'
sleep 3
echo 'Using '$PACKAGES_DIR' as source tree. If this is somehow incorrect, ctrl-c now!'
sleep 5

#####
# Copy the compiler stack to payload_build (exclude stack_src)
rsync -av --progress --exclude '*-build' --exclude 'stack_src' $PACKAGES_DIR/* .

#####
# Get a list of directories/applications which will be included in the package
export my_application_list=`ls`

####
# Clean it up a bit (for now, remove *.pyc *.pyo files)
echo "Searching for and removing *.pyc files..."
find . -type f -name "*.pyc" -or -name "*.pyo" | xargs rm -f

#####
# Build the sources tarbal
cd ~/rpmbuild/SOURCES
tar -pzcf moose-environment.tar.gz opt
#####
# Increment the revision number
current_version=`grep "Release:" $FEDORA_PACKAGE/SPECS/moose-compilers.spec | cut -d% -f1 | cut -d\  -f2`
let new_version=$current_version+1
all_together_now='Release: '$new_version'%{?dist}'
sed -i -e "s/Release:.*/$all_together_now/g" $FEDORA_PACKAGE/SPECS/moose-compilers.spec
cd $FEDORA_PACKAGE
git commit -a -m "Update Fedora package to version: $all_together_now"
git push

#####
# Copy the spec file to rpmbuild directory and create RPM
cp $FEDORA_PACKAGE/SPECS/moose-compilers.spec ~/rpmbuild/SPECS/
echo -e '##################\n\nBinaries moved\nList of applications/directories to be included in your package:\n\n\n'$my_application_list'\n\n##################\nNow building actual rpm package.\n\n'
time rpmbuild -ba ~/rpmbuild/SPECS/moose-compilers.spec


