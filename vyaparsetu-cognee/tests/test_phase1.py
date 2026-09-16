import asyncio
import os
import cognee
from dotenv import load_dotenv

load_dotenv()

TENANT_URL = os.getenv("COGNEE_TENANT_URL")
API_KEY = os.getenv("COGNEE_API_KEY")

DATASET_NAME = "scratch_unstructured"

SAMPLE_TEXT = (
    "Suresh bhaiya came to Sharma Kirana Store today and took 2 packs of Dahi "
    "worth 60 rupees and 1 litre of refined oil worth 180 rupees on credit. "
    "He promised to pay the total amount of 240 rupees next Tuesday."
)


async def main():
  print("Connecting to Cognee Cloud...")
  await cognee.serve(url=TENANT_URL, api_key=API_KEY)

  print(f"Adding unstructured text to dataset '{DATASET_NAME}'...")
  await cognee.add(data=SAMPLE_TEXT, dataset_name=DATASET_NAME)

  print("Running cognify() to extract knowledge graph...")
  await cognee.cognify(datasets=[DATASET_NAME])

  print("Cognify complete! Check the Cognee Cloud Dashboard.")
  await cognee.disconnect()


if __name__ == "__main__":
  asyncio.run(main())