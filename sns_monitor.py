import boto3
import datetime

# AWS Clients
sqs = boto3.client('sqs')
sns = boto3.client('sns')
cloudwatch = boto3.client('cloudwatch')

# Your SNS topic for alerts
SNS_TOPIC_ARN = "arn:aws:sns:eu-central-1:94234X66234:test-sns"

# Create a reusable Paginator
paginator = sqs.get_paginator('list_queues')

# Collect all queue URLs
all_queues = []
for page in paginator.paginate(PaginationConfig={"PageSize": 100}):  # Fetch in batches of 100
    all_queues.extend(page.get('QueueUrls', []))  # Append queues from each page

# Filter only those that start with 'PROD_'
prod_queues = [q for q in all_queues if q.split('/')[-1].startswith("PROD_")]

# Print total PROD_ queues retrieved
print(f"✅ Total PROD_ Queues Retrieved: {len(prod_queues)}")

# Time range for last 5 minutes
end_time = datetime.datetime.now(datetime.UTC)
start_time = end_time - datetime.timedelta(minutes=5)

# Check all PROD_ queue URLs
for queue_url in prod_queues:

    # Extract queue name
    queue_name = queue_url.split('/')[-1]

    # Get CloudWatch metric statistics
    response = cloudwatch.get_metric_statistics(
        Namespace="AWS/SQS",
        MetricName="ApproximateNumberOfMessagesVisible",
        Dimensions=[{"Name": "QueueName", "Value": queue_name}],
        Statistics=["Maximum"],
        Period=3000,  # 5-minute period
        StartTime=start_time,
        EndTime=end_time
    )

    # Extract the max number of messages seen in the last 5 minutes
    data_points = response.get("Datapoints", [])
    if data_points:
        max_messages = max(dp["Maximum"] for dp in data_points)
    else:
        max_messages = 0  # No data points = no messages in the last 5 minutes

    # If the queue exceeded 2 messages in the last 5 minutes, send an alert
    if max_messages > 5000:
        print(f"🚨 TEST ALERT! {queue_name} had {max_messages} messages in the last 5 minutes.")
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=f"Queue {queue_name} had {max_messages} messages in the last 5 minutes!",
            Subject="SQS Queue Overload Alert"
        )
