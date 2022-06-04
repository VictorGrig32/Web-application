#!/bin/bash

fdisk $1 <<EEOF
t

fd
w

EEOF
exit 0
