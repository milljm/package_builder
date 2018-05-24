#!/bin/bash
# Check if user supplied code signing certificate
if [ -d "<PACKAGES_DIR>/llvm-<LLVM>/codesign" ]; then
    security delete-certificate -c `cat <PACKAGES_DIR>/llvm-<LLVM>/codesign/codesign_name`
    sleep 3
    security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain <PACKAGES_DIR>/llvm-<LLVM>/codesign/moose_codesign.cert
    osascript -e 'tell app "System Events" to display dialog "LLDB code-signing certificate has been installed. \n\nNote: It may be necessary to reboot your machine for kernel extensions to load this certificate. Click `More Info` for details on how code-signing works and why a reboot may be necessary." with title "LLDB code-signing Caveats" buttons {"More Info", "Close"} default button 2
        if button returned of result = "More Info" then
            do shell script "echo Opening link"
            tell application "System Events" to open location "https://opensource.apple.com/source/lldb/lldb-69/docs/code-signing.txt"
        end if'
fi
