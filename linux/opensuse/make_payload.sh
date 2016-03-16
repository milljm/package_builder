#!/bin/bash
if [ -z $PACKAGES_DIR ]; then
  echo 'PACKAGES_DIR not set. Can not continue.'
  exit 1
fi
echo -e '\nBe sure to perform a cleaning operation on conda before continuing:\n\n\tconda clean --lock --tarballs --index-cache --packages --source-cache'
sleep 3
#####
# Set some initial location variables
OPENSUSE_PACKAGE=/tmp/moose_compiler_package/OPENSUSE_PACKAGE
RELATIVE_PACKAGE=${PACKAGES_DIR:1}

###
# Check for a current PACKAGES_DIR, exit if not set
# Clean out previous build, if it exists
if [ -d ~/rpmbuild/ ]; then
  echo -e "deleting previous build attempt: ~/rpmbuild"
  rm -rf ~/rpmbuild
fi
# Build the RPM directory structure
mkdir -p ~/rpmbuild/SOURCES/$RELATIVE_PACKAGE ~/rpmbuild/SPECS ~/rpmbuild/BUILD ~/rpmbuild/BUILDROOT ~/rpmbuild/RPMS ~/rpmbuild/SRPMS
cd ~/rpmbuild/SOURCES/$RELATIVE_PACKAGE
# Grab additional binaries

if ! [ -d $PACKAGES_DIR/distcc-3.2rc1 ]; then
  echo 'distcc not built... Just FYI'
  sleep 3
fi

#####
# Display any warnings, otherwise, the script has everything it needs
echo 'Using '$PACKAGES_DIR' as source tree. If this is somehow incorrect, ctrl-c now!'
sleep 5

#####
# Copy the compiler stack to payload_build (exclude stack_src)
rsync -av --progress --exclude "*-build" --exclude "stack_src" --exclude "*_backup*" $PACKAGES_DIR/* .

####
# Copy the build PETSc head script
cp $OPENSUSE_PACKAGE/../common_files/build_PETSc-head .

#####
# Get a list of directories/applications which will be included in the package
export my_application_list=`ls`

#####

## TODO
# capture the major.minor-revision efficiently
# cause the below is stupid ugly

# Increment the revision number
current_version=`grep "Release:" $OPENSUSE_PACKAGE/SPECS/moose-compilers.spec | cut -d% -f1 | cut -d\  -f2`
let new_version=$current_version+1
all_together_now='Release: '$new_version'%{?dist}'
sed -i -e "s/Release:.*/$all_together_now/g" $OPENSUSE_PACKAGE/SPECS/moose-compilers.spec
echo -e "#################################################\n\tThe revision of moose-environment has been changed to: "$new_version"\n\n\tcommitting to git repository...\n#################################################"
cd $OPENSUSE_PACKAGE
echo '1.1-'$new_version > ~/rpmbuild/SOURCES/$RELATIVE_PACKAGE/build
git commit -a -m 'update OPENSUSE_PACKAGE build: '$new_version
git push

#####
# Build the sources tarbal
cd ~/rpmbuild/SOURCES
tar -pzcf moose-environment.tar.gz opt

#####
# Copy the spec file to rpmbuild directory
cp $OPENSUSE_PACKAGE/SPECS/moose-compilers.spec ~/rpmbuild/SPECS/


echo -e '##################\n\nBinaries moved\nList of applications/directories to be included in your package:\n\n\n'$my_application_list'\n\n##################\nBuilding RPM...
'

# Build the RPM
time rpmbuild -ba ~/rpmbuild/SPECS/moose-compilers.spec
mv $HOME/rpmbuild/RPMS/x86_64/moose-environment-1.1-${new_version}.x86_64.rpm $OPENSUSE_PACKAGE/

echo -e 'Built package: '$OPENSUSE_PACKAGE/moose-environment-1.1-${new_version}.x86_64.rpm
