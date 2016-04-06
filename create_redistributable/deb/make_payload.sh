#!/bin/bash
#####
# Set some initial location variables
UBUNTU_PACKAGE=/tmp/moose_compiler_package/UBUNTU_PACKAGE
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

# Delete pre/post-installation script if it exists.
if [ -f $UBUNTU_PACKAGE/DEBIAN/preinst ]; then
  rm -f $UBUNTU_PACKAGE/DEBIAN/preinst
fi
if [ -f $UBUNTU_PACKAGE/DEBIAN/postinst ]; then
  rm -f $UBUNTU_PACKAGE/DEBIAN/postinst
fi

#####
# Display any warnings, otherwise, the script has everything it needs.
echo 'Using '$PACKAGES_DIR' as source tree. If this is somehow incorrect, ctrl-c now!'
echo -e '\nBe sure to perform a cleaning operation on conda before continuing:\n\n\tconda clean --lock --tarballs --index-cache --packages --source-cache'
sleep 5

#####
# Copy the compiler stack to payload_build (exclude the stack_src directory)
rsync -av --progress --exclude '*-build' --exclude 'stack_src' $PACKAGES_DIR/* .

####
# Copy the build PETSc head script into place
cp -Rf $UBUNTU_PACKAGE/../common_files/build_PETSc-head .

#####
# Get a list of directories/applications which will be included in the package.
export my_application_list=`ls`

#####
# Build the pre-installation script (in our case, its a backup script).
#
cat >> $UBUNTU_PACKAGE/DEBIAN/preinst << EOF
#!/bin/bash
export applications="`echo $my_application_list`"
export BACKUP_TIME=\$(date +%m-%d-%Y)
if ! [ -d $PACKAGES_DIR ]; then
        mkdir -p $PACKAGES_DIR
fi
EOF
chmod 755 $UBUNTU_PACKAGE/DEBIAN/preinst
echo 'wrote: '$UBUNTU_PACKAGE'/DEBIAN/preinst'

####
# Build the post-installation script
#
cat >> $UBUNTU_PACKAGE/DEBIAN/postinst << EOF
#!/bin/bash
set -e
chown -R root:root $PACKAGES_DIR
echo -e '\n\tAdd the following lines to your ~/.bashrc file to source the MOOSE compiler stack:\n\n\n## Uncomment the following line to enable pretty prompt:\n#export MOOSE_PROMPT=true\n\n## Uncomment the following line to enable autojump:\n#export MOOSE_JUMP=true\n\n## Source the MOOSE profile if moose_profile exists:\nif [ -f /opt/moose/environments/moose_profile ]; then\n  . /opt/moose/environments/moose_profile\nfi'
EOF
chmod 755 $UBUNTU_PACKAGE/DEBIAN/postinst
echo 'wrote: '$UBUNTU_PACKAGE'/DEBIAN/postinst'

####
# Adjust revision in the control file... in a very rudimentary way...
current_revision=`cat $UBUNTU_PACKAGE/DEBIAN/control | grep "Version:" | cut -d- -f2`
let new_revision=$current_revision+1
all_together_now=`cat $UBUNTU_PACKAGE/DEBIAN/control | grep "Version:" | cut -d- -f1`-$new_revision
human_readable=$(echo $all_together_now | cut -d\  -f2)
sed -i -e "s/Version:.*/$all_together_now/g" $UBUNTU_PACKAGE/DEBIAN/control

echo -e 'Updating repository with package version change'
sleep 3
git checkout UBUNTU_PACKAGE/DEBIAN/preinst
git commit -a -m 'update Ubuntu package version to '$human_readable
git push

cd $UBUNTU_PACKAGE/moose-environment
cp -R $UBUNTU_PACKAGE/DEBIAN .
echo $human_readable > ./opt/moose/build
cd ..
dpkg -b moose-environment
mv moose-environment.deb moose-environment_ubuntu-$human_readable.x86_64.deb

echo -e '\nDeb package created: moose-environment_ubuntu-'$human_readable'.x86_64.deb\n\n'
