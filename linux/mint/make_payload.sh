#!/bin/bash
#####
# Set some initial location variables
DISTRO_NAME="MINT"


DISTRO_PACKAGE=/tmp/moose_compiler_package/${DISTRO_NAME}_PACKAGE
RELATIVE_PACKAGE=${PACKAGES_DIR:1}

###
# Check for a current PACKAGES_DIR, exit if not set
if ! [ -z $PACKAGES_DIR ]; then
  # Clean out previous build, if it exists.
  if [ -d moose-environment ]; then
    echo -e "deleting previous moose-environment directory"
    rm -rf moose-environment
  fi
  # Build relative root installation directory
  mkdir -p moose-environment/$RELATIVE_PACKAGE
  cd moose-environment/$RELATIVE_PACKAGE
else
  echo -e 'No $PACKAGES_DIR environment variable set. Exiting.'
  exit 1
fi

#####
# Display any warnings, otherwise, the script has everything it needs.
echo 'Using '$PACKAGES_DIR' as source tree. If this is somehow incorrect, ctrl-c now!'
sleep 5
echo -e '\nBe sure to perform a cleaning operation on conda before continuing:\n\n\tconda clean --lock --tarballs --index-cache --packages --source-cache'
sleep 3

#####
# Copy the compiler stack to payload_build (exclude the stack_src directory)
rsync -av --progress --exclude '*-build' --exclude 'stack_src' $PACKAGES_DIR/* .

#####
# Get a list of directories/applications which will be included in the package.
export my_application_list=`ls`

#####
# Just let the builder know what is being included so the know
echo -e "The following files/directories were copied into the build directory:\n\n${my_application_list}"
sleep 3

#####
# Build the pre-installation script (in our case, its a backup script).
#
cat >> $DISTRO_PACKAGE/DEBIAN/preinst << EOF
#!/bin/bash
export applications="`echo $my_application_list`"
export BACKUP_TIME=\$(date +%m-%d-%Y)
if ! [ -d $PACKAGES_DIR ]; then
        mkdir -p $PACKAGES_DIR
fi
EOF
chmod 755 $DISTRO_PACKAGE/DEBIAN/preinst
echo "wrote: $DISTRO_PACKAGE/DEBIAN/preinst"


####
# Adjust revision in the control file... in a very rudimentary way...
current_revision=`cat $DISTRO_PACKAGE/DEBIAN/control | grep "Version:" | cut -d- -f2`
let new_revision=$current_revision+1
all_together_now=`cat $DISTRO_PACKAGE/DEBIAN/control | grep "Version:" | cut -d- -f1`-$new_revision
human_readable=$(echo $all_together_now | cut -d\  -f2)
sed -i -e "s/Version:.*/$all_together_now/g" $DISTRO_PACKAGE/DEBIAN/control

echo -e 'Updating repository with package version change'
sleep 3
cd $DISTRO_PACKAGE
git commit -a -m "update $DISTRO_NAME package version to ${human_readable}"
git push

# Copy the all-important DEBIAN directory. This is honestly all dpkg uses
cp -R $DISTRO_PACKAGE/DEBIAN $DISTRO_PACKAGE/moose-environment/

# Write the version to a file which will reside inside the package (just eye candy,
# as the version of this file is internal controlled with the 'control' file above)
echo $human_readable > $DISTRO_PACKAGE/moose-environment/opt/moose/build

# Move to $DISTRO_PACKAGE directory just in case we're elsewhere
cd $DISTRO_PACKAGE

dpkg -b moose-environment
mv moose-environment.deb moose-environment_$(echo $DISTRO_NAME | tr '[:upper:]' '[:lower:]')-$human_readable.x86_64.deb

echo -e "\nDEB package created: moose-environment_$DISTRO_NAME-${human_readable}.x86_64.deb\n\n"
