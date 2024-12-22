import os
from dotenv import find_dotenv, load_dotenv

import getpass
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
import anthropic

# returning api key and logging in
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
api_key = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=api_key,
)

test_weather = [30, 20]
# Defining function
def return_output(input):
    
    degrees = input[0]
    wind = input[1]

    client = anthropic.Anthropic(
        api_key=api_key,
    )
    message = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=1000,
    temperature=0.0,
    system="you are a helpful meteorologist assisstant, you have an in depth understanding of weather forecasting and are trying to help users understand upcoming weather.",
    messages=[
        {"role": "user", "content": "If the forecasted temperature is {degrees} farenheight with {wind} mph wind, what will running in this be like?".format(degrees = degrees, wind = wind)}
    ]
)
    return message.content

print(return_output(test_weather))

