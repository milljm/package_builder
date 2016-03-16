#!/bin/bash
if [ -f """$HOME"""/.bash_profile ]; then
        if [ `grep -c <PACKAGES_DIR>/environments/moose_profile """$HOME"""/.bash_profile` -le 0 ]; then
		response=`osascript -e 'tell app "System Events" to display dialog "You have selected not to setup the MOOSE environment. If you choose cancel here, know that nothing will work, until you source the moose_profile script on your own. By selecting OK, the following will be appended to your ~/.bash_profile:\n\n# Uncomment to enable pretty prompt:\n# export MOOSE_PROMPT=true\n\n# Uncomment to enable autojump:\n# export MOOSE_JUMP=true\n\n# Source MOOSE profile\nif [ -f <PACKAGES_DIR>/environments/moose_profile ]; then\n\t. <PACKAGES_DIR>/environments/moose_profile\nfi"' 2>/dev/null`
		if [ "$response" == "button returned:OK" ]; then
			cat >> """$HOME"""/.bash_profile << EOF

# Uncomment to enable pretty prompt:
# export MOOSE_PROMPT=true

# Uncomment to enable autojump:
# export MOOSE_JUMP=true

# Source MOOSE profile
if [ -f <PACKAGES_DIR>/environments/moose_profile ]; then
        . <PACKAGES_DIR>/environments/moose_profile
fi
EOF
		fi
	fi
else
	response=`osascript -e 'tell app "System Events" to display dialog "You have selected not to setup the MOOSE environment. If you choose cancel here, know that nothing will work, until you source the moose_profile script on your own. By selecting OK, the following will be appended to your ~/.bash_profile:\n\n# Uncomment to enable pretty prompt:\n# export MOOSE_PROMPT=true\n\n# Uncomment to enable autojump:\n# export MOOSE_JUMP=true\n\n# Source MOOSE profile\nif [ -f <PACKAGES_DIR>/environments/moose_profile ]; then\n\t. <PACKAGES_DIR>/environments/moose_profile\nfi"' 2>/dev/null`
	if [ "$response" == "button returned:OK" ]; then
		cat > """$HOME"""/.bash_profile << EOF
#!/bin/bash
# Uncomment to enable pretty prompt:
# export MOOSE_PROMPT=true

# Uncomment to enable autojump:
# export MOOSE_JUMP=true

# Source MOOSE profile
if [ -f <PACKAGES_DIR>/environments/moose_profile ]; then
        . <PACKAGES_DIR>/environments/moose_profile
fi
EOF
        chown $USER:staff """$HOME"""/.bash_profile
	fi
fi
cd /
rm -rf /private/tmp/MOOSE_installer-tmp
