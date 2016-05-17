#!/bin/bash
if [ -f $HOME/.bash_profile ]; then
  if [ `grep -c <PACKAGES_DIR>/environments/moose_profile $HOME/.bash_profile` -le 0 ]; then
    cat >> $HOME/.bash_profile << EOF

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
else
 cat > $HOME/.bash_profile << EOF
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
        chown $USER:staff $HOME/.bash_profile
fi
