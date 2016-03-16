#!/bin/bash
if [ -z $PACKAGES_DIR ]; then
  echo 'PACKAGES_DIR not set. Can not continue.'
  exit 1
fi
echo -e '\nBe sure to perform a cleaning operation on conda before continuing:\n\n\tconda clean --lock --tarballs --index-cache --packages --source-cache'
sleep 3
#####
# prepare for building...
if [ -f common_post.sh ]; then
  rm -f common_post.sh
fi
if [ -f environment_post.sh ]; then
  rm -f environment_post.sh
fi
if [ -f README_Panel.html ]; then
  rm -f README_Panel.html
fi
if [ -f Conclusion_Panel.html ]; then
  rm -f Conclusion_Panel.html
fi
if [ -f payload.tar.gz ]; then
  rm -f payload.tar.gz
fi

# Move into the main containment directory
cd payload_build
for sfile in `ls`; do
  if [ $sfile != "build_PETSc-head" ]; then
    rm -rf $sfile
  fi
done
#####
# Display any warnings
echo 'Using '$PACKAGES_DIR' as source tree. If this somehow is incorrect, ctrl-c now!'
sleep 5

#####
# Increment the build version
current_build=`cat /tmp/moose_compiler_package/ELCAPITAN_PACKAGE/build`
let "current_build = $current_build + 1"
echo $current_build > $PACKAGES_DIR/build
echo $current_build > /tmp/moose_compiler_package/ELCAPITAN_PACKAGE/build
echo 'Commiting new build version to external repo...'
sleep 3
git commit -a -m 'update ELCAPITAN_PACKAGE build: '$current_build
git push

#####
# Copy the compiler stack to payload_build
rsync -av --progress --exclude "*-build" --exclude "stack_src" --exclude "*_backup*" $PACKAGES_DIR/* .

####
# Clean it up a bit (for now, remove *.pyc files)
echo "Searching for and removing *.pyc files..."
find . -type f -name *.pyc | xargs rm -f

#####
# Get a list of directories/applications copied
export my_application_list=`ls`

#####
# Build the distributable tarball and move it into place
echo "Building tarball... this takes a bit..."
tar -pzcf payload.tar.gz .gdbinit *
mv -f payload.tar.gz ../

#####
# Build the emacs.tar.gz file
cd ../emacs_build
tar -pzcf emacs.tar.gz .emacs .emacs.d
mv emacs.tar.gz ../

#####
# Build the common_post.sh script.
#
cat >> ../common_post.sh << EOF
#!/bin/bash
# Remove previous $PACKAGES_DIR, we have no reason to save it anymore.
# If someone is installing stuff into our directory, their loss.
if [ -d $PACKAGES_DIR ]; then
  rm -rf $PACKAGES_DIR
  mkdir -p $PACKAGES_DIR
else
  mkdir -p $PACKAGES_DIR
fi

export applications="`echo $my_application_list`"

for app in \$applications; do
  mv -f /private/tmp/MOOSE_installer-tmp/\${app} $PACKAGES_DIR
  chown -R root:wheel $PACKAGES_DIR/\${app}
done

# Create OpenMP symbolic link. El Capitan requirement now
# that DYLD_LIBRARY_PATH is ignored by Python (with out
# this run_tests would break)
if ! [ -d /usr/local/lib ]; then
  mkdir -p /usr/local/lib
fi
if [ -L /usr/local/lib/libomp.dylib ]; then
  if [ `stat -f %Y /usr/local/lib/libomp.dylib | grep -c $PACKAGES_DIR` -ge 1 ]; then
    rm -f /usr/local/lib/libomp.dylib
    cd /usr/local/lib
    ln -s $PACKAGES_DIR/llvm_3.7.0/lib/libomp.dylib .
  else
    echo "Warning: '/usr/local/lib/libomp.dylib' is not under MOOSE control" >> /opt/moose/build
  fi
else
  cd /usr/local/lib
  ln -s $PACKAGES_DIR/llvm_3.7.0/lib/libomp.dylib .
fi
EOF

#####
# Build environment_post.sh script.
cat >> ../environment_post.sh << EOENV
#!/bin/bash
# Change environment load path to new packages directory
sed -i -e 's!/opt/packages!'"$PACKAGES_DIR"'!g' """\$HOME"""/.bash_profile

if [ -f """\$HOME"""/.bash_profile ]; then
        if [ \`grep -c $PACKAGES_DIR/environments/moose_profile """\$HOME"""/.bash_profile\` -le 0 ]; then
                cat >> """\$HOME"""/.bash_profile << EOF

# Uncomment to enable pretty prompt:
# export MOOSE_PROMPT=true

# Uncomment to enable autojump:
# export MOOSE_JUMP=true

# Source MOOSE profile
if [ -f $PACKAGES_DIR/environments/moose_profile ]; then
        . $PACKAGES_DIR/environments/moose_profile
fi
EOF
        fi
else
        cat > """\$HOME"""/.bash_profile << EOF
#!/bin/bash
# Uncomment to enable pretty prompt:
# export MOOSE_PROMPT=true

# Uncomment to enable autojump:
# export MOOSE_JUMP=true

# Source MOOSE profile
if [ -f $PACKAGES_DIR/environments/moose_profile ]; then
        . $PACKAGES_DIR/environments/moose_profile
fi
EOF
        chown \$USER:staff """\$HOME"""/.bash_profile
fi

EOENV

#####
# Post-build...
cat ../README.html | sed -e 's!<PACKAGES_DIR>!'"$PACKAGES_DIR"'!g' > ../README_Panel.html
cat ../CONCLUSION.html | sed -e 's!<PACKAGES_DIR>!'"$PACKAGES_DIR"'!g' > ../Conclusion_Panel.html
cat ../WELCOME.html | sed -e 's!<BUILD_NUM>!'"Package version: $current_build"'!g' > ../Welcome_Panel.html
chmod 755 ../common_post.sh
chmod 755 ../environment_post.sh
echo -e '
###############################################
##
##  Tarball built.
##
##  The following is a list of
##  applications/directories that were included
##  in the tarball:
##
##  '$my_application_list'
##
###############################################
##
##  To finalize the packge, run the following
##  three commands:
##
##  1. Build the package:

  /Applications/PackageMaker.app/Contents/MacOS/PackageMaker --doc /tmp/moose_compiler_package/ELCAPITAN_PACKAGE.pmdoc

##
##  2. Sign the package:

  productsign --sign "Developer ID Installer: BATTELLE ENERGY ALLIANCE, LLC (J2Y4H5G88N)" /tmp/moose_compiler_package/ELCAPITAN_PACKAGE/elcapitanpackage.pkg ~/elcapitan-environment_'$current_build'.pkg

##
##  3. Verify the package was signed correctly:

  spctl -a -v --type install ~/elcapitan-environment_'$current_build'.pkg
'
