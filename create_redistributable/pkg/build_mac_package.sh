#!/bin/bash
printf "Creating MacOS SubPackages...\n"
for pkg_dir in `ls OSX`; do
    if [ "${pkg_dir}" != "payload" ]; then
        pkgbuild --nopayload --scripts OSX/${pkg_dir} --identifier "INEL.GOV.mooseCompilerLibraries.${pkg_dir}" --version 1.0 OSX.pkgbuild/${pkg_dir}.pkg
    fi
done
printf "Creating MacOS Payload...\n"
pkgbuild --root "$1" --scripts OSX/payload --install-location "$1" --identifier "INEL.GOV.mooseCompilerLibraries.payload" --version 1.0 OSX.pkgbuild/payload.pkg

printf "Creating MacOS product package"
cd OSX.pkgbuild
productbuild --distribution ./Distribution --scripts ./Scripts --resources ./Resources --package-path environment.pkg --package-path icecream.pkg --package-path lldb.pkg --package-path payload.pkg ../../osx.pkg
