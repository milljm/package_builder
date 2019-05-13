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

    # Fix previous versions of the bash_profile (add header/footer to our sourcing profile to make it easier to remove/alter)
    if [ `grep -c "#MOOSE_ENVIRONMENT" """$use_this_profile"""` -eq 0 ]; then
      sed -i '' -e $'s/# Uncomment to enable pretty prompt:/#MOOSE_ENVIRONMENT\\\n# Uncomment to enable pretty prompt:/g' """$use_this_profile"""
      sed -i '' -e $'/environments\/moose_profile$/{n;s/^fi/fi\\\n#ENDMOOSE_ENVIRONMENT/;}' """$use_this_profile"""
    fi

    # Remove source section, so we can add changes
    sed -i '' -e '/#MOOSE_ENVIRONMENT/,/#ENDMOOSE_ENVIRONMENT/d' """$use_this_profile"""

    cat >> """$use_this_profile""" << EOF
#MOOSE_ENVIRONMENT
# Uncomment to enable pretty prompt:
# export MOOSE_PROMPT=true

# Uncomment to enable autojump:
# export MOOSE_JUMP=true

# Source MOOSE profile
if [ -f <PACKAGES_DIR>/environments/moose_profile ]; then
        . <PACKAGES_DIR>/environments/moose_profile

        # Make the moose compiler stack available.
        # Note: if you have any additional package managers installed
        # (Homebrew, Macports, Fink, etc) know that you must perform
        # the following command _after_ the source commands for the
        # afore mentioned package managers.
        module load moose-dev-clang
fi
#ENDMOOSE_ENVIRONMENT
EOF
    chown """$USER:staff""" """$use_this_profile"""
}
# Use bash_profile by default.
profiles=("""$HOME/.bash_profile""")
detectAndCreateProfile
verifyItWorkes
