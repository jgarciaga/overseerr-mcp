from collections.abc import Sequence
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
import json
import os
from . import overseerr

# Constants for tool names
TOOL_GET_STATUS = "overseerr_status"
TOOL_GET_MOVIE_REQUESTS = "overseerr_movie_requests"
TOOL_GET_TV_REQUESTS = "overseerr_tv_requests"

# Environment variables
api_key = os.getenv("OVERSEERR_API_KEY", "")
url = os.getenv("OVERSEERR_URL", "")

if not api_key or not url:
    raise ValueError("OVERSEERR_API_KEY and OVERSEERR_URL environment variables are required")

# Media status mapping
MEDIA_STATUS_MAPPING = {
    1: "UNKNOWN",
    2: "PENDING", 
    3: "PROCESSING",
    4: "PARTIALLY_AVAILABLE",
    5: "AVAILABLE"
}

class ToolHandler():
    def __init__(self, tool_name: str):
        self.name = tool_name

    def get_tool_description(self) -> Tool:
        raise NotImplementedError()

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        raise NotImplementedError()

class StatusToolHandler(ToolHandler):
    def __init__(self):
        super().__init__(TOOL_GET_STATUS)

    def get_tool_description(self):
        return Tool(
            name=self.name,
            description="Get the status of the Overseerr server.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            },
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        # Create synchronous client
        client = overseerr.Overseerr(api_key=api_key, url=url)
        data = client.get_status()

        if "version" in data:
            status_response = f"\n---\nOverseerr is available and these are the status data:\n"
            status_response += "\n- " + "\n- ".join([f"{key}: {val}" for key, val in data.items()])
        else:
            status_response = f"\n---\nOverseerr is not available and below is the request error: \n"
            status_response += "\n- " + "\n- ".join([f"{key}: {val}" for key, val in data.items()])

        return [
            TextContent(
                type="text",
                text=status_response
            )
        ]

class MovieRequestsToolHandler(ToolHandler):
    def __init__(self):
        super().__init__(TOOL_GET_MOVIE_REQUESTS)

    def get_tool_description(self):
        return Tool(
            name=self.name,
            description="Get the list of all movie requests that satisfies the filter arguments.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by media availability status.",
                        "enum": ["all", "approved", "available", "pending", "processing", "unavailable", "failed"]
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Filter for the date of request, formatted as '2020-09-12T10:00:27.000Z'"
                    }
                }
            },
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        # Extract arguments
        status = args.get("status")
        start_date = args.get("start_date")
        
        # Now using synchronous approach
        results = self.get_movie_requests(status, start_date)
        
        return [
            TextContent(
                type="text",
                text=json.dumps(results, indent=2)
            )
        ]
        
    def get_movie_requests(self, status=None, start_date=None):
        client = overseerr.Overseerr(api_key=api_key, url=url)
        
        # Parameter validation
        valid_statuses = ["all", "approved", "available", "pending", "processing", "unavailable", "failed"]
        if status and status not in valid_statuses:
            status = None
            
        # Initialize pagination parameters
        take = 20  # Number of items per page
        skip = 0   # Starting offset
        has_more = True
        
        all_results = []
        
        # Process all pages
        while has_more:
            # Prepare params
            params = {
                "take": take,
                "skip": skip
            }
            
            # Add filter if specified
            if status:
                params["filter"] = status
            
            # Call API
            response = client.get_requests(params)
            
            # Process results
            results = response.get("results", [])
            
            for result in results:
                # Only process if it's a movie (no tvdbId)
                media_info = result.get("media", {})
                if media_info and not media_info.get("tvdbId"):
                    # Check if request date matches the filter if provided
                    created_at = result.get("createdAt", "")
                    if start_date and start_date > created_at:
                        continue
                    
                    # Get movie details to get the title
                    movie_id = media_info.get("tmdbId")
                    movie_details = client.get_movie_details(movie_id)
                    
                    # Map media availability to string value
                    media_status_code = media_info.get("status", 1)
                    media_availability = MEDIA_STATUS_MAPPING.get(media_status_code, "UNKNOWN")
                    
                    # Create formatted result
                    formatted_result = {
                        "title": movie_details.get("title", "Unknown Movie"),
                        "media_availability": media_availability,
                        "request_date": created_at
                    }
                    
                    all_results.append(formatted_result)
            
            # Check if there are more pages
            page_info = response.get("pageInfo", {})
            if page_info.get("pages", 0) <= (skip // take) + 1:
                has_more = False
            else:
                skip += take
        
        return all_results

class TvRequestsToolHandler(ToolHandler):
    def __init__(self):
        super().__init__(TOOL_GET_TV_REQUESTS)

    def get_tool_description(self):
        return Tool(
            name=self.name,
            description="Get the list of all TV requests that satisfies the filter arguments.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Filter by media availability status.",
                        "enum": ["all", "approved", "available", "pending", "processing", "unavailable", "failed"]
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Filter for the date of request, formatted as '2020-09-12T10:00:27.000Z'"
                    }
                }
            },
        )

    def run_tool(self, args: dict) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        # Extract arguments
        status = args.get("status")
        start_date = args.get("start_date")
        
        # Now using synchronous approach
        results = self.get_tv_requests(status, start_date)
        
        return [
            TextContent(
                type="text",
                text=json.dumps(results, indent=2)
            )
        ]
        
    def get_tv_requests(self, status=None, start_date=None):
        client = overseerr.Overseerr(api_key=api_key, url=url)
        
        # Parameter validation
        valid_statuses = ["all", "approved", "available", "pending", "processing", "unavailable", "failed"]
        if status and status not in valid_statuses:
            status = None
            
        # Initialize pagination parameters
        take = 20  # Number of items per page
        skip = 0   # Starting offset
        has_more = True
        
        all_results = []
        
        # Process all pages
        while has_more:
            # Prepare params
            params = {
                "take": take,
                "skip": skip
            }
            
            # Add filter if specified
            if status:
                params["filter"] = status
            
            # Call API
            response = client.get_requests(params)
            
            # Process results
            results = response.get("results", [])
            
            for result in results:
                # Only process if it's a TV show (has tvdbId)
                media_info = result.get("media", {})
                if media_info and media_info.get("tvdbId"):
                    # Check if request date matches the filter if provided
                    created_at = result.get("createdAt", "")
                    if start_date and start_date > created_at:
                        continue
                    
                    # Get TV details to get the title and seasons
                    tv_id = media_info.get("tmdbId")
                    tv_details = client.get_tv_details(tv_id)
                    
                    # Map media availability to string value
                    media_status_code = media_info.get("status", 1)
                    tv_title_availability = MEDIA_STATUS_MAPPING.get(media_status_code, "UNKNOWN")
                    
                    # Get seasons information
                    seasons = tv_details.get("seasons", [])
                    
                    # For each season, get more detailed info including episodes
                    for season in seasons:
                        season_number = season.get("seasonNumber", 0)
                        
                        # Skip if it's a special season (season 0)
                        if season_number == 0:
                            continue
                        
                        # Format season string (e.g., S01)
                        season_str = f"S{season_number:02d}"
                        
                        # Get detailed season info including episodes
                        season_details = client.get_season_details(tv_id, season_number)
                        
                        # Season availability is assumed to be the same as the show
                        tv_season_availability = tv_title_availability
                        
                        # Process episodes
                        episodes = season_details.get("episodes", [])
                        episode_details = []
                        
                        for episode in episodes:
                            episode_number = episode.get("episodeNumber", 0)
                            episode_details.append({
                                "episode_number": f"{episode_number:02d}",
                                "episode_name": episode.get("name", f"Episode {episode_number}")
                            })
                        
                        # Create formatted result for this season
                        formatted_result = {
                            "tv_title": tv_details.get("name", "Unknown TV Show"),
                            "tv_title_availability": tv_title_availability,
                            "tv_season": season_str,
                            "tv_season_availability": tv_season_availability,
                            "tv_episodes": episode_details,
                            "request_date": created_at
                        }
                        
                        all_results.append(formatted_result)
            
            # Check if there are more pages
            page_info = response.get("pageInfo", {})
            if page_info.get("pages", 0) <= (skip // take) + 1:
                has_more = False
            else:
                skip += take
        
        return all_results