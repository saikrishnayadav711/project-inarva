#This file is for whether the Azure Search upload is working fine
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import uuid

SEARCH_ENDPOINT = "https://hr-policy-search.search.windows.net"
SEARCH_KEY = "U6pKfXo0AiBXpWNNC6viRFEA1oVjzMXE8MEVexccNdAzSeDajQpK"
SEARCH_INDEX = "hr-policy-index"

client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=SEARCH_INDEX,
    credential=AzureKeyCredential(SEARCH_KEY)
)

doc = {
    "id": str(uuid.uuid4()),
    "content": "Employees are entitled to casual leave.",
    "embedding": [0.0] * 1536,
    "source": "sanity-test"
}

res = client.upload_documents([doc])
print(res)
