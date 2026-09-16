import asyncio
import os
import cognee
from dotenv import load_dotenv

load_dotenv()

TENANT_URL = os.getenv("COGNEE_TENANT_URL")
API_KEY = os.getenv("COGNEE_API_KEY")


async def main():
  print("Connecting to Cognee Cloud...")
  await cognee.serve(url=TENANT_URL, api_key=API_KEY)
  print("Connected successfully.")

  print("Disconnecting...")
  await cognee.disconnect()
  print("Disconnected cleanly.")


if __name__ == "__main__":
  asyncio.run(main())