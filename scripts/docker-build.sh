#!/usr/bin/bash

if test -z "${DOCKER}"; then
    export DOCKER=nerdctl
fi

if test -z "$1"; then
    echo "Usage: $0 version"
    exit 1
else
    export BUILD_VERSION="$1"
fi

${DOCKER} build . -t broadcaststorm/maestro-conductor-service:${BUILD_VERSION}
${DOCKER} build . -t broadcaststorm/maestro-conductor-service:latest

${DOCKER} push broadcaststorm/maestro-conductor-service:${BUILD_VERSION}
${DOCKER} push broadcaststorm/maestro-conductor-service:latest
