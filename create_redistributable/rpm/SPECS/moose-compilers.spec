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
Source: %{name}.tar
Requires: libbX11-devel gcc-c++ make freeglut-devel m4 blas-devel lapack-devel <REQUIREMENTS>
BuildRoot: %{_tmppath}/%{name}-build
AutoReqProv: no

%define debug_package %{nil}

%description
This package contains the neccessary libraries/binaries to utilize the MOOSE framework and assocaited applications.

%prep
%setup -q -n <PACKAGES_BASENAME>

%build


%install
install -d %{buildroot}/<PACKAGES_BASENAME>
mv -f <PACKAGES_PARENT> %{buildroot}/<PACKAGES_BASENAME>/

%post
echo -e '\n\tAdd the following lines to your ~/.bashrc file to source the MOOSE compiler stack:\n\n\n## Uncomment the following line to enable pretty prompt:\n#export MOOSE_PROMPT=true\n\n## Uncomment the following line to enable autojump:\n#export MOOSE_JUMP=true\n\n## Source the MOOSE profile if moose_profile exists:\nif [ -f <PACKAGES_DIR>/environments/moose_profile ]; then\n  . <PACKAGES_DIR>/environments/moose_profile\nfi'


%postun

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
<PACKAGES_DIR>

%changelog
