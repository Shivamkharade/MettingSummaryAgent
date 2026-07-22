from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, START ,END
from video_tanscript_generate import transcript_graph
from utils import (
    get_output_directory,
    save_text_file,
    extract_text,
    get_llm,
)
from typing import TypedDict,Optional
from pathlib import Path
from win11toast import toast



class MeetingState(TypedDict):
    video_path: str
    output_dir: str

    transcript: Optional[str]
    summary: Optional[str]
    action_items: Optional[str]


def transcript_node(state: MeetingState):
    result = transcript_graph.invoke(
        {
            "video_path":state['video_path']
        }
    )
    
    return {
        "transcript": result["transcript"]
    }
    
def summary_node(state: MeetingState):
    
    print("entered summary_node")
    transcript = state["transcript"]
    
    SUMMARY_PROMPT = PromptTemplate(
        template="""
        You are a professional meeting assistant.

        Analyze the following meeting transcript and generate a well-structured summary.

        IMPORTANT:
        - ALWAYS generate the summary in English, regardless of the language of the meeting transcript.
        - If the transcript is in any language other than English, first understand its content and then produce the summary in clear, professional English.
        - Do NOT mix languages in the output. The final summary must be entirely in English.

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
        input_variables=["transcript"]
    )
    llm = get_llm()
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
    
    print("exited summary node and saved the summary")
    return {
        "summary": summary
    }

def action_items(state:MeetingState):
    print("entered action items node")
    transcript = state['transcript']
    
    ACTION_ITEMS_PROMPT = PromptTemplate(
        template="""
        You are a professional meeting assistant.

        Analyze the following meeting transcript and identify all action items.

        IMPORTANT:
        - ALWAYS generate the action items in English, regardless of the language of the meeting transcript.
        - If the transcript is in any language other than English, first understand its content and then produce the action items in clear, professional English.
        - Do NOT mix languages in the output. The final output must be entirely in English.

        For each action item, include:

        - Assignee (if mentioned)
        - Task
        - Deadline (if mentioned)

        Format your response exactly like this:

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
        input_variables=["transcript"]
    )
    
    llm = get_llm()
    
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
    
    print("exited action_items node and saved action items ")

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
    print("sent the window notification")
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
