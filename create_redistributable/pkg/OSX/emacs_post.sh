#!/bin/bash
timestamp=$(date +%m-%d-%Y)
# lets not do this stuff anymore...
exit
if [ -d """$HOME"""/.emacs.d ] || [ -f """$HOME"""/.emacs ]; then
	mv -f """$HOME"""/.emacs """$HOME"""/.emacs_backup-${timestamp}
	mv -f """$HOME"""/.emacs.d """$HOME"""/.emacs.d_backup-${timestamp}
    	tar -xf /private/tmp/MOOSE_installer-tmp/emacs.tar.gz -C """$HOME"""/
    	chown -R $USER:staff """$HOME"""/.emacs
	chown -R $USER:staff """$HOME"""/.emacs.d
else
        tar -xf /private/tmp/MOOSE_installer-tmp/emacs.tar.gz -C """$HOME"""/
        chown -R $USER:staff """$HOME"""/.emacs
        chown -R $USER:staff """$HOME"""/.emacs.d
fi
