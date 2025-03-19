# gen-otp.py

Generate an OTP from the OTP string. 

Create a file .otp-secret under current directory with OTP secret from the authenticator. If no file, it will be created when u execute the script and will be asked you to add the secret there. 

    [user@server ~]$ cat .otp-secret 
    #OTP SECRET
    otp_secret='UTSDFHDS1234567SD67324G3HRBSDFSAPZMPK2QIOO5'

Add execution permission to file.
    chmod +x gen-bast-otp

Execute the OTP generation script from the command line to see the AWS MFA OTP.
    ./gen-bast-otp


# gen-sess-token-aws-cli.py

Copy the file and execute to avoid entering AWS MFA code each time you run CLI commands. Remember to replace variables as required.

To run commands for a longer period, add --duration-seconds xxx to line 40 after replacing xxx with the required seconds.

So the new line will be:

  _authenticationOutput=`aws sts get-session-token --duration-seconds 900 --serial-number ${_MFA_SERIAL} --token-code ${_MFA_TOKEN}`

Comment out the line with the AWS bastion username (use find and replace) in the file .aws/config.

mfa_serial = arn:aws:iam::xxxxxxxxxxxxx:mfa/user-read-only

Sample output for various scenarios:

[user@bastion tester]$ bash new.sh 
A token has been found, checking validity
Your last token has expired
OTP generation script not found.
Enter AWS Bastion user name: aws-user
ARN is arn:aws:iam::591940994135:mfa/aws-user
Please input your 6 digit MFA token: 786551
Generated new token for AWS CLI session
Token generation completed, try executing CLI commands

[user@bastion tester]$ bash new.sh 
A token has been found, checking the validity
Your last token is still valid, no need to create a new one
Token generation completed, try executing CLI commands

[user@bastion tester]$ bash new.sh 
Token not found. Creating one now.
OTP generation script found. Reading OTP and ARN.
Generated new token for AWS CLI session
Token generation completed, try executing CLI commands

[user@bastion tester]$ bash new.sh 
Token not found. Creating one now.
OTP generation script not found.
Enter AWS Bastion user name: aws-user
ARN is arn:aws:iam::591940994135:mfa/aws-user
Please input your 6 digit MFA token: 035240
Generated new token for AWS CLI session
Token generation completed, try executing CLI commands

# sns_monitor.py

How it works:
	1.	Lists all SQS queues (even if more than 1000) using pagination.
	2.	Filters queues that start with "PROD_".
	3.	Fetches the number of messages waiting in each queue (from CloudWatch).
	4.	If messages exceed 5000, it sends an SNS alert.
	5.	Works dynamically with any number of queues.
