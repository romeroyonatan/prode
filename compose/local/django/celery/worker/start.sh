#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace


celery -A prode.taskapp worker -l INFO
