from google.genai.errors import ServerError
from langgraph.graph import StateGraph, START ,END
from langgraph.types import Send
from typing import TypedDict,Optional,Annotated
from utils1 import (
    save_text_file,
    get_output_directory,
    get_gemini_client,
    Global_model
)
import time
import operator
import subprocess
import json


class ChunkTranscript(TypedDict):
    chunk_number: int
    transcript: str

class TranscriptState(TypedDict):

    video_path: str

    chunks: Optional[list[str]]

    transcripts: Annotated[list[ChunkTranscript], operator.add]

    transcript: Optional[str]

class ChunkWorkerState(TypedDict):
    chunk_path: str
    chunk_number: int

#------------------hellper functions------------------#

def is_long_video(video_path: str, max_duration: int = 3000) -> bool:
    """
    Returns True if the video's duration exceeds max_duration.

    Parameters
    ----------
    video_path : str
        Path to the video.

    max_duration : int, optional
        Maximum duration (in seconds) that can be processed
        as a single video. Videos longer than this will be
        split into chunks.

        Default = 3000 seconds (50 minutes).
    """

    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        video_path,
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    duration = float(json.loads(result.stdout)["format"]["duration"])

    return duration > max_duration

def route_video(state: TranscriptState) -> str:
    """
    Routes the video based on its duration.

    Returns:
        "short" -> Process directly.
        "long"  -> Split into chunks and process in parallel.
    """

    if is_long_video(state["video_path"]):
        return "long"

    return "short"

#------------------main nodes------------------#

def transcript_node(state: TranscriptState):
    print("Entered transcript node")

    client = get_gemini_client()
    video_path = state["video_path"]

    print("Uploading video...")

    # Upload only once
    video = client.files.upload(file=video_path)

    print("Video uploaded. Waiting for processing...")

    while True:
        video = client.files.get(name=video.name)

        if str(video.state).endswith("ACTIVE"):
            break

        if str(video.state).endswith("FAILED"):
            raise RuntimeError("Video processing failed.")

        print("Video is processing...")
        time.sleep(5)

    print("Video is ACTIVE.")

    MAX_RETRIES = 8
    wait_time = 5

    for attempt in range(MAX_RETRIES):
        try:
            print(f"Generating transcript (Attempt {attempt + 1}/{MAX_RETRIES})...")

            response = client.models.generate_content(
                model=Global_model,
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
                ],
            )

            transcript = response.text

            save_text_file(
                state["video_path"],
                "transcript",
                transcript,
            )

            print("Transcript generated successfully.")

            return {
                "transcript": transcript
            }

        except ServerError as e:
            if attempt == MAX_RETRIES - 1:
                print("Maximum retries reached.")
                raise

            print(
                f"Server busy (503). Waiting {wait_time} seconds before retry..."
            )

            time.sleep(wait_time)

            # Exponential backoff
            wait_time *= 2
        except ServerError as e:
            if attempt == MAX_RETRIES - 1:
                print("Maximum retries reached.")
                raise

            wait_time = 10 * (attempt + 1)

            print(
                f"Gemini server is busy (503). "
                f"Retrying in {wait_time} seconds..."
            )

            time.sleep(wait_time)

def split_video_node(state: TranscriptState):

    video_path = state["video_path"]

    # Split into 45-minute chunks (2700 seconds)
    CHUNK_DURATION = 2700

    # Create the chunks directory inside the meeting output folder
    meeting_output_dir = get_output_directory(video_path)

    chunks_dir = meeting_output_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------
    # Get video duration using ffprobe
    # ------------------------------------
    probe_command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json",
        video_path,
    ]

    result = subprocess.run(
        probe_command,
        capture_output=True,
        text=True,
        check=True,
    )

    duration = float(json.loads(result.stdout)["format"]["duration"])

    print(f"Video duration: {duration / 60:.2f} minutes")

    # ------------------------------------
    # Split the video into chunks
    # ------------------------------------
    chunks = []

    chunk_number = 0

    for start_time in range(0, int(duration), CHUNK_DURATION):

        output_file = chunks_dir / f"chunk_{chunk_number:03}.mp4"

        split_command = [
            "ffmpeg",
            "-y",
            "-ss", str(start_time),
            "-i", video_path,
            "-t", str(CHUNK_DURATION),
            "-c", "copy",
            str(output_file),
        ]

        subprocess.run(
            split_command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        print(f"Created {output_file.name}")

        chunks.append(str(output_file))

        chunk_number += 1

    print(f"\nTotal chunks created: {len(chunks)}")

    return {
        "chunks": chunks
    }

def fan_out_chunks(state: TranscriptState):

    sends = []

    for chunk_number, chunk_path in enumerate(state["chunks"]):

        sends.append(
            Send(
                "transcribe_chunk_node",
                {
                    "chunk_path": chunk_path,
                    "chunk_number": chunk_number
                }
            )
        )

    return sends

def transcribe_chunk_node(state: ChunkWorkerState):
    client = get_gemini_client()
    chunk_path = state["chunk_path"]
    chunk_number = state["chunk_number"]

    print(f"Uploading Chunk {chunk_number}...")

    # Upload the chunk
    video_file = client.files.upload(file=chunk_path)

    # Wait until Gemini finishes processing the uploaded file
    while video_file.state.name == "PROCESSING":
        print(f"Chunk {chunk_number} is processing...")
        time.sleep(5)
        video_file = client.files.get(name=video_file.name)

    if video_file.state.name == "FAILED":
        raise Exception(f"Chunk {chunk_number} failed during upload/processing.")

    print(f"Generating transcript for Chunk {chunk_number}...")
    
    

    # Generate transcript
    MAX_RETRIES = 3

    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=Global_model,
                contents=[
                    video_file,
                    """
                    Generate a complete verbatim transcript of this meeting.

                    Requirements:
                    - Do not summarize.
                    - Preserve punctuation.
                    - Ignore background music.
                    - Include all spoken dialogue.
                    """
                ],
            )

            # Success
            break

        except ServerError as e:
            if attempt == MAX_RETRIES - 1:
                raise

            wait_time = 10 * (attempt + 1)

            print(
                f"Chunk {chunk_number}: Gemini is busy (503). "
                f"Retrying in {wait_time} seconds..."
            )

            time.sleep(wait_time)

    print(f"Finished Chunk {chunk_number}")

    return {
        "transcripts": [
            {
                "chunk_number": chunk_number,
                "transcript": response.text,
            }
        ]
    }   

def merge_transcripts_node(state: TranscriptState):

    ordered = sorted(
        state["transcripts"],
        key=lambda item: item["chunk_number"]
    )

    transcript = "\n\n".join(
        item["transcript"]
        for item in ordered
    )
    
    save_text_file(
        state['video_path'],
        "transcript",
        transcript
    )
    
    print("Merged transcript saved.")
    
    return {
        "transcript": transcript
    }

transcript_builder = StateGraph(TranscriptState)

# ---------------- Nodes ---------------- #

transcript_builder.add_node("transcript_node", transcript_node)
transcript_builder.add_node("split_video_node", split_video_node)
transcript_builder.add_node("transcribe_chunk_node", transcribe_chunk_node)
transcript_builder.add_node("merge_transcripts_node", merge_transcripts_node)

# ---------------- Flow ---------------- #

transcript_builder.add_conditional_edges(
    START,
    route_video,
    {
        "short": "transcript_node",
        "long": "split_video_node",
    }
)

# Fan-out
transcript_builder.add_conditional_edges(
    "split_video_node",
    fan_out_chunks
)

# All worker executions join here
transcript_builder.add_edge(
    "transcribe_chunk_node",
    "merge_transcripts_node"
)

# Short video path
transcript_builder.add_edge(
    "transcript_node",
    END
)

# Long video path
transcript_builder.add_edge(
    "merge_transcripts_node",
    END
)

# Compile
transcript_graph = transcript_builder.compile()
