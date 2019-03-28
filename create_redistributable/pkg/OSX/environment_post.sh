#!/bin/bash
verifyItWorkes()
{
    for profile in "${profiles[@]}"; do
        if [ -f """$profile""" ]; then
            break
        fi
    done
    unset MOOSE_JOBS
    source """$profile"""
    if [ -z "$MOOSE_JOBS" ]; then
        error_message="""Installer script wrote changes to\n\n\t$use_this_profile\n\nbut was unable to determine the presence of key MOOSE environment vairables in a new terminal session.\n\nBash loads the first readable profile it finds in the following order:\n\n\t~/.bash_profile\n\t~/.bash_login\n\t~/.profile\n\nYou will need to investigate these files and figure out why\n\n\t$use_this_profile\n\nis not being loaded."""
        response=`osascript -e 'display alert "'"$error_message"'"' 2>/dev/null`
    fi
}

function findCorrectProfile()
{
    # Loop through each found profile and determine the last profile being sourced
    reverse_priority_array=()
    for profile in "${profiles[@]}"; do
        if [ -f """$profile""" ] && ! [ -L """$profile""" ]; then reverse_priority_array=("""$profile""" """${reverse_priority_array[@]}"""); fi
    done

    # No profile exists
    if [ "${reverse_priority_array}x" = "x" ]; then
        reverse_priority_array=("""${profiles[${#profiles[@]}-1]}""")
    fi

    for found_profile in "${reverse_priority_array[@]}"; do
        if [ -n "$previous_priority_profile" ]; then
            if [ `grep -c \\\\$(basename """$previous_priority_profile""") """$found_profile"""` -ge 1 ]; then
                use_this_profile="""$previous_priority_profile"""
            else
                use_this_profile="""$found_profile"""
            fi
        fi
        previous_priority_profile=$found_profile
    done
    use_this_profile=${use_this_profile:-"""$found_profile"""}
}

function detectAndCreateProfile()
{
    if [ -z "$use_this_profile" ]; then
        findCorrectProfile
    fi
    # First, make sure we are not already loading a MOOSE profile (perhaps they are simply updating their package)
    if [ -f """$use_this_profile""" ] && [ "$(grep -i "environments/moose_profile" """$use_this_profile""")x" != "x" ]; then
        return
    fi
    cat <<EOF >"""$use_this_profile"""
# Uncomment to enable pretty prompt:
# export MOOSE_PROMPT=true

# Uncomment to enable autojump:
# export MOOSE_JUMP=true

# Source MOOSE profile
if [ -f <PACKAGES_DIR>/environments/moose_profile ]; then
        . <PACKAGES_DIR>/environments/moose_profile
fi
EOF
    chown """$USER:staff""" """$use_this_profile"""
}
# Bash will search and load the first readable profile it finds in the following order
# ~/.bash_profile ~/.bash_login ~/.profile
profiles=("""$HOME/.bash_profile""" """$HOME/.bash_login""" """$HOME/.profile""")
detectAndCreateProfile
verifyItWorkes
