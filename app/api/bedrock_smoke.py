"""Make one explicit Bedrock Converse request using configured credentials."""
import json
import os
import boto3

def main():
    response = boto3.client("bedrock-runtime").converse(
        modelId=os.environ["ANSWER_MODEL_ID"],
        messages=[{"role": "user", "content": [{"text": "Reply with one short greeting."}]}],
        inferenceConfig={"maxTokens": 64},
    )
    print(json.dumps({"message": response["output"]["message"],
                      "usage": response.get("usage", {})}, indent=2))

if __name__ == "__main__":
    main()
