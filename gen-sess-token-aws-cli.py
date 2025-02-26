#!/bin/bash

# Script to generate session token for AWS CLI
# Author: Ananda Raj
# Date: 2 Nov 2020

# Default filename values, change as required
username=$(whoami)
AWS_TOKEN_FILE="/home/$username/.aws/.awstoken"
AWS_AUTH_PROFILE="user-bastion"
OTP_FILE="/home/username/scripts/gen-otp.py"   # Replace the OTP generation script path here

# Function for prompting for MFA token code
promptForMFA(){
  while true; do
        if [ -e $OTP_FILE ]; then 
            echo "OTP generation script found. Reading OTP and ARN."
            bastuser=$(/usr/bin/python3 $OTP_FILE | head -n 1 | cut -d ":" -f 2 | sed 's/^ //;s/"$//'
)
            _MFA_SERIAL="arn:aws:iam::591940994135:mfa/$bastuser"
            _MFA_TOKEN=$(/usr/bin/python3 $OTP_FILE | tail -n 1)
            break
        else
            echo "OTP generation script not found."
            while true; do
                read -p "Enter AWS Bastion user name: " bastuser
                _MFA_SERIAL="arn:aws:iam::591940994135:mfa/$bastuser"
                echo "ARN is $_MFA_SERIAL"
                break
            done
            read -p "Please input your 6 digit MFA token: " token
            case $token in
                [0-9][0-9][0-9][0-9][0-9][0-9] ) _MFA_TOKEN=$token; break;;
                * ) echo "Please enter a valid 6 digit pin." ;;
            esac
        fi
  done

  # Run the awscli command
  _authenticationOutput=`aws sts get-session-token --serial-number ${_MFA_SERIAL} --token-code ${_MFA_TOKEN}`
  echo "Generated new token for AWS CLI session"

  # Save authentication to some file
  echo $_authenticationOutput > $AWS_TOKEN_FILE;
}

# If token is present, retrieve it from file
if [ -e $AWS_TOKEN_FILE ]; then
  echo "A token has been found, checking the validity"
  _authenticationOutput=`cat $AWS_TOKEN_FILE`
  _authExpiration=`echo $_authenticationOutput | jq -r '.Credentials.Expiration'`
  _nowTime=`date -u +'%Y-%m-%dT%H:%M:%SZ'`
  
  # Check for the expiration value against the current time
  # If expired, invoke the prompt for mfa function
  if [ "$_authExpiration" \< "$_nowTime" ]; then
    echo "Your last token has expired"
    promptForMFA
  else 
    echo "Your last token is still valid, no need to create a new one"
  fi
# Else token not found, invoke the prompt for mfa function
else
  echo "Token not found. Creating one now."
  promptForMFA
fi

# Decode the json file to collect variables
_AWS_ACCESS_KEY_ID=`echo ${_authenticationOutput} | jq -r '.Credentials.AccessKeyId'`
_AWS_SECRET_ACCESS_KEY=`echo ${_authenticationOutput} | jq -r '.Credentials.SecretAccessKey'`
_AWS_SESSION_TOKEN=`echo ${_authenticationOutput} | jq -r '.Credentials.SessionToken'`

# Add variables to conf
aws --profile $AWS_AUTH_PROFILE configure set aws_access_key_id "$_AWS_ACCESS_KEY_ID"
aws --profile $AWS_AUTH_PROFILE configure set aws_secret_access_key "$_AWS_SECRET_ACCESS_KEY"
aws --profile $AWS_AUTH_PROFILE configure set aws_session_token "$_AWS_SESSION_TOKEN"
echo "Token generation completed, try executing CLI commands"
