
from a2ui.core.basic_catalog import BasicCatalog
from a2ui.core.schema import ProtocolVersion
from a2ui.inference_formats.direct_json import DirectJsonFormatFactory
from a2ui.processor import A2uiRequestProcessor, CatalogConfig
from a2ui.utils import to_version_number


ROLE_DESCRIPTION = (
    "You are a helpful restaurant finding assistant."
    "Your final output MUST be an A2UI UI definition."
)

UI_DESCRIPTION = """
- If the query is for a list of restaurants, use the restaurant data you have already received from the `get_restaurants` tool to populate the `updateDataModel` message.
- IMPORTANT: When using updateDataModel to update items, you MUST specify `path: "/items"` in `updateDataModel`, and the `value` MUST be an array of restaurants.
- IMPORTANT: Always specify the path when using updateDataModel. The part message is ignored when the path is missin.
- If the number of restaurants is 5 or fewer, you MUST use the `SINGLE_COLUMN_LIST_EXAMPLE` template.
- If the number of restaurants is more than 5, you MUST use the `TWO_COLUMN_LIST_EXAMPLE` template.
- If the query is to book a restaurant (e.g., "USER_WANTS_TO_BOOK..."), you MUST use the `BOOKING_FORM_EXAMPLE` template.
- If the query is a booking submission (e.g., "User submitted a booking..."), you MUST use the `CONFIRMATION_EXAMPLE` template.
"""

def get_text_prompt() -> str:
    """
    Constructs the prompt for a text-only agent.
    """
    return """
        You are a helpful restaurant finding assistant. Your final output MUST be a text response.

        To generate the response, you MUST follow these rules:
        1.  **For finding restaurants:**
            a. You MUST call the `get_restaurants` tool. Extract the cuisine, location, and a specific number (`count`) of restaurants from the user's query.
            b. After receiving the data, format the restaurant list as a clear, human-readable text response. 
               You MUST preserve any markdown formatting (like for links) that you receive from the tool.
        2.  **For booking a table (when you receive a query like 'USER_WANTS_TO_BOOK...'):**
            a. Respond by asking the user for the necessary details to make a booking (party size, date, time, dietary requirement).
        3.  **For confirming a booking (when you receive a query like 'User submitted a booking...'):**
            a. Respond with a simple text confirmation of the booking details.
"""

if "__main__" == __name__:
    from a2ui.utils import load_examples

    # Example of how to use A2uiRequestProcessor to generate a system prompt In you actual application,
    # you would call this from your main agent logic.
    version = ProtocolVersion.V0_9
    catalog = CatalogConfig(BasicCatalog(version)).transformed_catalog
    processor = A2uiRequestProcessor(
        [catalog], format_factory=DirectJsonFormatFactory()
    )
    examples = load_examples(
        processor.active_catalogs,
        f"examples/{to_version_number(version)}",
        validate=True,
    )
    prompt_parts = [
        ROLE_DESCRIPTION,
        f"## UI Description:\n{UI_DESCRIPTION}",
        processor.prompt_snippet,
    ]
    if examples:
        prompt_parts.append(f"### Example:\n{examples}")
    restaurant_prompt = "\n\n".join(prompt_parts)

    print(restaurant_prompt)
    
    # This demonstrates how you could save the prompt to a file for inspection
    with open("generated_prompt.txt", "w") as f:
        f.write(restaurant_prompt)
    print("\nGenerated prompt saved to generated_prompt.txt")

