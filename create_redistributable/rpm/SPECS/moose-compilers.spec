#
# spec file for package 
#
# Copyright (c) 2013 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

Name: moose-environment
Version: 1.1
Release: <VERSION>%{?dist}
License: None
Summary: Compilers neccessary to utilize the MOOSE Framework
Url: http://mooseframework.org
Group: Development/Libraries
Source: %{name}.tar.gz
Requires: gcc gcc-c++ make
BuildRoot: %{_tmppath}/%{name}-build
AutoReqProv: no

# Prevent debug package from being created
%define debug_package %{nil}
%define __strip /bin/true

# Disable debug symbol stripping
%define __spec_install_port /usr/lib/rpm/brp-compress

# Disable binary stripping
%define __os_install_post %{nil}

# Prevent check-buildroot from running. We do not need it.
%define __arch_install_post /usr/lib/rpm/check-rpaths

%description
This package contains the neccessary libraries/binaries to utilize the MOOSE framework and assocaited applications.

%prep
%setup -q -n <PACKAGES_BASENAME>

%build


%install
export QA_SKIP_RPATHS=true
mkdir -p %{buildroot}/<PACKAGES_BASENAME>
mv -f <PACKAGES_PARENT> %{buildroot}/<PACKAGES_BASENAME>/

%post
# Supported shells for modulecmd
shells=(bash sh zsh csh tcsh ksh)
exp_cm=('export MODULEPATH=' 'export MODULEPATH=' 'export MODULEPATH=' 'setenv MODULEPATH ' 'setenv MODULEPATH ' 'export MODULEPATH=')
index=0
# Loop through each supported shell, and generate a profile for it
for a_shell in ${shells[@]}; do
    if [ `which ${a_shell} 2>/dev/null` ]; then
        # bash and sh use the same profile. Do once.
        if [ ${a_shell} = 'sh' ] && [ -d /etc/profile.d ] && [ -z "$DO_BASH_ONCE" ]; then
            DO_BASH_ONCE=true
            # overwrite previous initialization
            cat <<EOF > /etc/profile.d/moose-environment.${a_shell}
# initialize moose-environment modulecmd if available
if [ -d <PACKAGES_DIR>/Modules/3.2.10 ]; then
  if [ -n "\$MODULESHOME" ]; then
    ${exp_cm[$index]}"\$MODULEPATH:<PACKAGES_DIR>/Modules/3.2.10/modulefiles"
  else
    MY_SHELL=\`cat /proc/\$\$/comm 2>/dev/null\`
    if [ "\${MY_SHELL}" = "bash" ]; then
      source <PACKAGES_DIR>/Modules/3.2.10/init/bash
    elif [ "\${MY_SHELL}" = "sh" ]; then
      . <PACKAGES_DIR>/Modules/3.2.10/init/sh
    fi
  fi
fi
EOF
        # csh and tcsh use the same profile. Do once.
        elif [ ${a_shell} = 'csh' ] || [ ${a_shell} = 'tcsh' ] && [ -d /etc/csh/login.d ] && [ -z "$DO_CSH_ONCE" ]; then
            DO_CSH_ONCE=true
            # overwrite previous initialization
            cat <<EOF > /etc/csh/login.d/moose-environment.csh
# initialize moose-environment modulecmd if available
if (-d <PACKAGES_DIR>/Modules/3.2.10) then
  if (! \$?MODULEPATH ) then
    set MY_SHELL=\`cat /proc/\$\$/comm\`
    source "<PACKAGES_DIR>/Modules/3.2.10/init/\${MY_SHELL}"
  else
    setenv MODULEPATH "\${MODULEPATH}:<PACKAGES_DIR>/Modules/3.2.10/modulefiles"
  endif
endif
EOF
        elif [ ${a_shell} = 'zsh' ] && [ -f /etc/zsh/zshenv ]; then
            if [ `cat /etc/zsh/zshenv | grep -c "START-INITIALIZE-MOOSE"` -ne 0 ]; then
                # Remove previous initialization section
                sed -i'' -e '/#START-INITIALIZE-MOOSE/,/#END-INITIALIZE-MOOSE/d' /etc/zsh/zshenv
            fi
            cat <<EOF >> /etc/zsh/zshenv
#START-INITIALIZE-MOOSE
if [[ ( -d <PACKAGES_DIR>/Modules/3.2.10 ) ]]
then
  if [[ -n \${MODULESHOME} ]]
  then
    export MODULEPATH="\$MODULEPATH:<PACKAGES_DIR>/Modules/3.2.10/modulefiles"
  else
    source "<PACKAGES_DIR>/Modules/3.2.10/init/zsh"
  fi
fi
#END-INITIALIZE-MOOSE
EOF
        elif [ ${a_shell} = 'ksh' ] && [ -f /etc/profile ]; then
            if [ `cat /etc/profile | grep -c "START-INITIALIZE-MOOSE"` -ne 0 ]; then
                # Remove previous initialization section
                sed -i'' -e '/#START-INITIALIZE-MOOSE/,/#END-INITIALIZE-MOOSE/d' /etc/profile
            fi
            cat <<EOF >> /etc/profile
#START-INITIALIZE-MOOSE
if [ "\$(cat /proc/\$\$/comm 2>/dev/null)" = "${a_shell}" ]; then
  if [ -d <PACKAGES_DIR>/Modules/3.2.10 ]; then
    if [ -n "\$MODULESHOME" ]; then
      ${exp_cm[$index]}"\$MODULEPATH:<PACKAGES_DIR>/Modules/3.2.10/modulefiles"
    else
      source "<PACKAGES_DIR>/Modules/3.2.10/init/${a_shell}"
    fi
  fi
fi
#END-INITIALIZE-MOOSE
EOF
        fi
    fi
    let index=$index+1
done

# Make sure urls.txt is present
if [ -d "<PACKAGES_DIR>/miniconda/pkgs" ]; then
  touch "<PACKAGES_DIR>/miniconda/pkgs/urls.txt"
fi

echo -e """
MOOSE Environment Install Complete.
In order to utilize the MOOSE environment, YOU MUST OPEN A NEW TERMINAL WINDOW.

Upon doing so, the module system which controls the library stack will become
available for use. The default modules used for MOOSE development on linux can
be loaded as follows:

     \`module load moose-dev-gcc\`

There are many other modules available (such as a different PETSc version, or
compiler). You can peruse these other modules by running a combination of
\`module avail\` and \`module load\` commands.

See \`module help\` for more details on other module commands.

"""

%postun

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
<PACKAGES_DIR>

%changelog
