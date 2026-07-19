from langchain_google_genai import ChatGoogleGenerativeAI
from google import genai
from langchain_core.prompts import PromptTemplate

from langgraph.graph import StateGraph, START ,END

from dotenv import load_dotenv
from typing import TypedDict,Optional
from pathlib import Path
import os
from win11toast import toast


import time

load_dotenv(".env")
api_key_google = os .getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

class MeetingState(TypedDict):
    video_path: str
    output_dir: str

    transcript: Optional[str]
    summary: Optional[str]
    action_items: Optional[str]

def get_output_directory(video_path: str) -> Path:
    """
    Creates the following structure:

    Meeting_Agent/
    ├── Meetings/
    │     meeting.mp4
    │
    └── Summary/
          meeting/
    """

    video = Path(video_path)

    # Meeting_Agent/Meetings
    meetings_folder = video.parent

    # Meeting_Agent
    project_root = meetings_folder.parent

    # Meeting_Agent/Summary
    summary_root = project_root / "Summary"

    # Meeting_Agent/Summary/<meeting_name>
    meeting_folder = summary_root / video.stem

    meeting_folder.mkdir(parents=True, exist_ok=True)

    return meeting_folder

def extract_text(response):

    content = response.content

    if isinstance(content, str):
        return content

    elif isinstance(content, dict):
        return content.get("text", "")

    elif isinstance(content, list):
        parts = []

        for item in content:

            if isinstance(item, dict):
                parts.append(item.get("text", ""))

            elif hasattr(item, "text"):
                parts.append(item.text)

            else:
                parts.append(str(item))

        return "\n".join(parts)

    return str(content)



def save_text_file(video_path: str, filename: str, content: Any) -> Path:
    """
    Saves text content into the meeting's output folder.
    """

    output_folder = get_output_directory(video_path)
    file_path = output_folder / filename

    if isinstance(content, str):
        text = content

    elif isinstance(content, dict):
        text = content.get("text", str(content))

    elif isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(item.get("text", ""))
            elif hasattr(item, "text"):
                parts.append(item.text)
            else:
                parts.append(str(item))
        text = "\n".join(parts)

    else:
        text = str(content)

    file_path.write_text(text, encoding="utf-8")

    return file_path

def transcript_node(state: MeetingState):
    
    client = genai.Client(api_key=api_key_google)

    video_path = state["video_path"]

    # Upload video
    video = client.files.upload(file=video_path)

    # Wait until Google finishes processing
    while True:
        video = client.files.get(name=video.name)

        if str(video.state).endswith("ACTIVE"):
            break

        if str(video.state).endswith("FAILED"):
            raise RuntimeError("Video processing failed.")

        time.sleep(5)

    # Generate transcript
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=[
            video,
            """
            Generate a complete verbatim transcript of this meeting.

            Requirements:
            - Do not summarize.
            - Preserve punctuation.
            - Ignore background music.
            - Include all spoken dialogue.
            """
        ]
    )

    transcript = response.text

    # Save transcript
    save_text_file(
    state["video_path"],
    "transcript.txt",
    transcript
    )

    return {
        "transcript": transcript
    }
    
def summary_node(state: MeetingState):

    transcript = state["transcript"]
    
    SUMMARY_PROMPT = PromptTemplate(
        template="""
        You are a professional meeting assistant.

        Analyze the following meeting transcript and generate a well-structured summary.

        Your summary should contain the following sections:

        ## Meeting Overview
        Provide a concise overview of the meeting.

        ## Key Discussion Points
        List the important topics discussed.

        ## Decisions Made
        List any decisions that were made during the meeting.
        If no decisions were made, write "None".

        Keep the response clear, professional, and concise.

        Meeting Transcript:

        {transcript}
        """,
        input_variables= ['transcript']
        )

    chain = SUMMARY_PROMPT | llm

    response = chain.invoke({
        "transcript": transcript
    })

    summary = extract_text(response)
    
    save_text_file(
    state["video_path"],
    "summary.txt",
    summary
    )

    return {
        "summary": summary
    }

def action_items(state:MeetingState):
    
    transcript = state['transcript']
    
    ACTION_ITEMS_PROMPT =PromptTemplate( 
        template="""
        You are a professional meeting assistant.

        Analyze the following meeting transcript and identify all action items.

        For each action item, include:

        - Assignee (if mentioned)
        - Task
        - Deadline (if mentioned)

        Format your response like this:

        1.
        Assignee:
        Task:
        Deadline:

        2.
        Assignee:
        Task:
        Deadline:

        If there are no action items in the meeting, respond exactly with:

        No action items identified.

        Meeting Transcript:

        {transcript}
        """,
        input_variables=['transcript']
    )
    
    
    action_items_chain = ACTION_ITEMS_PROMPT | llm
    
    response = action_items_chain.invoke(
        {
            "transcript": transcript
        }
    )

    action_items_text = extract_text(response)  

    # Replace this later with the helper function
    save_text_file(
    state["video_path"],
    "action_items.txt",
    action_items_text
    )

    return {
        "action_items": action_items_text
    }
    

def notification_node(state: MeetingState):

    output_folder = get_output_directory(state["video_path"])

    toast(
        "✅ Meeting Processing Completed",
        f"{Path(state['video_path']).stem}\n\n"
        "Transcript, Summary and Action Items have been generated.",
        buttons=[
            {
                "activationType": "protocol",
                "arguments": output_folder.as_uri(),
                "content": "📂 Open Folder"
            },
            {
                "activationType": "system",
                "arguments": "dismiss",
                "content": "Dismiss"
            }
        ]
    )

    return {}

# graph building
builder = StateGraph(MeetingState)

# adding nodes
builder.add_node('transcript',transcript_node)
builder.add_node('summary',summary_node)
builder.add_node('action_items',action_items)
builder.add_node('notification',notification_node)

# adding edges
builder.add_edge(START, "transcript")

builder.add_edge("transcript", "summary")
builder.add_edge("transcript", "action_items")

builder.add_edge("summary", "notification")
builder.add_edge("action_items", "notification")

builder.add_edge("notification", END)

graph = builder.compile()