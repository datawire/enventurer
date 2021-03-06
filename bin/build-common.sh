#!/usr/bin/env bash

# Copyright 2015, 2016 Datawire. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
set -euo pipefail

sanity_check() {
    header "Build Environment Sanity Checks"
    local required_programs=("$@")
    for p in "${required_programs[@]}"; do
        is_on_path ${p}
    done
}

is_on_path() {
    local program=${1:?Program not specified}
    step "$program installed? "
    if command -v ${program} >/dev/null 2>&1 ; then
        ok
    else
        die
    fi
}

output() {
    local level="$1"
    local format="${2:?Output message format not set}"
    local msg="${3:?Output message not set}"

    if [ ${VERBOSITY} -ge ${level} ]; then
        printf -- "$format" "$msg"
    fi
}

msg() { output 1 "%s\n" "$1"; }
nl()  { printf "\n"; }

header() {
    nl
    msg "*** $1 ***"
    nl
}

step()   { output 2 "--> %s" "$1"; }
stepln() { step "$1\n"; }

sub_step () {
    output 3 "-->  %s" "$1"
}

ok() {
    output 3 "%s\n" "OK"
}

pass() {
    output 3 "%s\n" "OK"
}

die() {
    printf "FAIL"
    printf "\n\n        "
    printf "${1:?''}"
    printf "\n\n"
    exit 1
}