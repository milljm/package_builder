#!/bin/bash
# save current cron if there is one
crontab -l >> crontab_file

# If there is already a cron set for killing iceccd, leave it alone
# if not, set one up
if [ `cat crontab_file | grep -c iceccd` -le 0 ]; then
    cat >> crontab_file << EOF
02 03 * * * /usr/bin/killall iceccd
EOF
    crontab crontab_file
fi


# Determine if this is a laptop. If so, we will not distribute jobs to this machine (CPU count of 0)
if [ `system_profiler -detailLevel mini | grep "Model Identifier" | grep -i -c "macpro"` -ge 1 ]; then
    # Get number of Threads / 2 (Cores) - 1, so we can not
    # set up a machine that gets saturated with jobs.
    CPU_COUNT=`echo "($(/usr/sbin/sysctl -n hw.ncpu) / 2) - 1" | bc`
else
    CPU_COUNT=0
fi

if ! [ -f /Library/LaunchDaemons/com.moose.icecream.plist ]; then
    sed -e "s/<CHANGEME>/`hostname | cut -d. -f1`_$USER/g" <PACKAGES_DIR>/icecream/com.moose.icecream.plist | \
        sed -e "s/<CPUS>/$CPU_COUNT/g" > /Library/LaunchDaemons/com.moose.icecream.plist
    chown root:wheel /Library/LaunchDaemons/com.moose.icecream.plist
    launchctl load /Library/LaunchDaemons/com.moose.icecream.plist
else
    launchctl unload /Library/LaunchDaemons/com.moose.icecream.plist
    launchctl load /Library/LaunchDaemons/com.moose.icecream.plist
fi
