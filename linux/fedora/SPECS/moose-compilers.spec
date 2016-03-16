Name: moose-environment
Version: 1.0
Release: 20%{?dist}
License: None
Summary: Compilers neccessary to utilize the MOOSE Framework
Url: http://mooseframework.com
Group: Development/Libraries
Source: %{name}.tar.gz
Requires: gcc-c++, gcc-gfortran, tcl, tk, libX11-devel
BuildRoot: %{_tmppath}/%{name}-build
AutoReqProv: no

%define debug_package %{nil}

%description
This package contains the neccessary libraries/binaries to utilize the MOOSE framework and assocaited applications.

%prep
%setup -q -n opt

%build


%install
install -d %{buildroot}/opt
mv -f moose %{buildroot}/opt/

%post
echo -e '\n\tAdd the following lines to your ~/.bashrc file to source the MOOSE compiler stack:\n\nif [ -f /opt/moose/environments/moose_profile ]; then\n  . /opt/moose/environments/moose_profile\nfi'

%postun

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
/opt/moose

%changelog
