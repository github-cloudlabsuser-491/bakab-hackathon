from promptflow import tool
from openai import AzureOpenAI
import openai

openai.api_type = "azure"
openai.api_version = "2024-02-15-preview"

# Azure OpenAI setup
openai.api_base = "https://hackathon-1307763.openai.azure.com/" # Add your endpoint here
openai.api_key = "c822e4186dbd4585a3c6a8cfff242888" # Add your OpenAI API key here
deployment_id = "gpt-35-turbo" # Add your deployment ID here

# Azure AI Search setup
search_endpoint = "https://hackathon-aisearch-1307763.search.windows.net"; # Add your Azure AI Search endpoint here
search_key = "dJvch0L3HtQMphkXRp8C31o5YrTAouriP1Li5wM7OgAzSeAm7C0P"; # Add your Azure AI Search admin key here
search_index_wf = "vector-1714700262298-workfusion"; # Add your Azure AI Search index name here
search_index_uipath = "vector-1714699887369-uipath"; # Add your Azure AI Search index name here


# The inputs section will change based on the arguments of the tool function, after you save the code
# Adding type to arguments and return value will help the system show the types properly
# Please update the function name/signature per need
@tool
def my_python_tool(original_question: str) -> str:    
    searchidx = search_index_wf
    return chatdocs(original_question, searchidx)


def chatdocs(user_prompt:str, search_index_name:str) -> str:
    message_system = [{"role": "system", "content": "You're a helpful assistant. If you don't know the answer, respond $nocomment."}]
    message_text = [{"role": "user", "content": user_prompt}]
    print(f"user prompt is {user_prompt}")
   
    try:
        # Flag to show citations
        show_citations = True       
        
        # Initialize the Azure OpenAI client
        client = AzureOpenAI(
            base_url=f"{openai.api_base}/openai/deployments/{deployment_id}/extensions",
            api_key=openai.api_key,
            api_version="2023-09-01-preview"
        )
        
        extension_config = dict(dataSources = [
        {
            "type": "AzureCognitiveSearch",
            "parameters" : {
                "endpoint":search_endpoint,
                "key": search_key,
                "indexName": search_index_name
            }

        }])

        # Send request to Azure OpenAI model
        print("...Sending the following request to Azure OpenAI endpoint...")
        print("Request: " + user_prompt + "\n")

        response = client.chat.completions.create(
            model = deployment_id,
            temperature = 0.5,
            max_tokens = 100,
            messages = message_text,
            extra_body = extension_config
        )

        # Print response
        print("Response: " + response.choices[0].message.content + "\n")

        if (show_citations):
            # Print citations
            #print(response)
            print("Citations:")
            citations = response.choices[0].message.context['citations']
            print(citations)
            citation_json = json.loads(citations)
            for c in citation_json:
                print("  Title: " + c['title'])

        return response.choices[0].message.content
        
    except Exception as ex:
        print(ex)
