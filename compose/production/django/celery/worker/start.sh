#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset


celery -A prode.taskapp worker -l INFO
