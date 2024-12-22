import os
from dotenv import find_dotenv, load_dotenv

import getpass
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
import anthropic



# Defining function
def query_condition_description(api_key, input):
    
    client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key=api_key,
    )
    degrees = input[0]
    wind = input[1]
    cloud = input[2]

    client = anthropic.Anthropic(
        api_key=api_key,
    )
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=200,
        temperature=0.0,
        system='''you are a helpful meteorologist assisstant, you have an in depth understanding of 
              weather forecasting and are trying to help users understand upcoming weather.''',
        messages=[
        {"role": "user", "content": '''If the forecasted temperature is {degrees} celcius with {wind} kph wind and 
                                        cloud cover {cloud} %, what will running in this be like? Limit your 
                                        response to less than 100 words'''.format(degrees = degrees, wind = wind, cloud = cloud)}
        ]
     )   

    return message.content[0].text


