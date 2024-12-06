
try:
    dynamodb = boto3.resource("dynamodb",
                              aws_access_key_id=key_id,
                              aws_secret_access_key=secret_id,
                              region_name='eu-north-1')

    table = dynamodb.Table('vova_table2')
    table.put_item(Item={'vova_table2': 'xyz'})
    print("Item successfully added to DynamoDB table.")

except Exception as e:
    print("Error:", e)

