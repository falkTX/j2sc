#!/bin/sh

# Cadence Session Startup Injection
# Start JACK (or not) according to user settings

INSTALL_PREFIX="X-PREFIX-X"

if [ -f $INSTALL_PREFIX/bin/cadence-session-start ]; then

export CADENCE_AUTO_STARTED="true"

STARTUP="${INSTALL_PREFIX}/bin/cadence-session-start --system-start-by-x11-startup ${STARTUP}"

fi

unset INSTALL_PREFIX
