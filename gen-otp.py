#!/bin/bash

# Script to generate session token for AWS CLI
# Author: Ananda Raj
# Date: 2 Nov 2020


#!/usr/bin/env python3
"""
Shows your OTP challenge
The first time the script will create a configuration file
"""

import os
from onetimepass import get_totp  # Ensure onetimepass is installed

# Replace Username here (optional)
print "OTP for user: abcde"

# OTP configuration file path
#otpconfig = f"{os.environ['HOME']}/scripts/.otp-secret"
otpconfig = f"./.otp-secret"

# Ensure the configuration file exists
if not os.path.isfile(otpconfig):
    with open(otpconfig, 'w') as f:
        f.write("# OTP Secret\notp_secret = 'XXXXXXXXXXXXXX'\n")
    print(f"Sample config file created at {otpconfig}.")
    print("Please update it with your secret.")
    quit(1)

# Load the secret from the config file
otp_secret = None
with open(otpconfig) as f:
    for line in f:
        if line.startswith("otp_secret"):
            otp_secret = line.split("=", 1)[1].strip().strip("'")

# Validate the secret
if not otp_secret:
    print("Invalid or missing OTP secret. Please set it in the config file.")
    quit(1)

try:
    # Generate OTP token
    otp_token = get_totp(otp_secret)  # No need to decode as_string=False by default
except Exception as e:
    print(f"Error: {e}")
    print("Failed to generate OTP. Check your secret.")
    quit(1)

# Display the OTP token
def show_otp():
    """ Display the OTP token """
    print(otp_token)

if __name__ == "__main__":
    show_otp()
