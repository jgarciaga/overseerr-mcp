import os
from datetime import datetime
from copy import deepcopy
from typing import Any, List, Dict, Optional
import httpx
from mcp.server.fastmcp import FastMCP

from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("overseerr-mcp")

# Constants
overseerr_url = os.environ["OVERSEERR_URL"]
overseerr_api_key = os.environ["OVERSEERR_API_KEY"]

# Helper Functions
async def make_overseerr_request(url: str) -> dict[str, Any]:
    """Make a request to the Overseerr API with proper error handling."""
    headers = {
        "Accept": "application/json",
        "X-Api-Key": overseerr_api_key
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as err:
            return {"Request Error": str(err)}


async def format_media_request_list(media_requests: list[dict]) -> dict[str, Any]:
    """Format the media requests"""
    media_availability_status_mapper = {
        1: "UNKNOWN",
        2: "PENDING",
        3: "PROCESSING",
        4: "PARTIALLY_AVAILABLE",
        5: "AVAILABLE"
    }

    formatted_list = []
    for item in media_requests:
        new_item = {}

        formatted_list += [deepcopy(new_item)]



@mcp.tool()
async def get_overseerr_status() -> str:
    """Get the status of the Overseerr Server.

    """
    url = f"{overseerr_url}/api/v1/status"
    data = await make_overseerr_request(url)

    if "version" in data:
        status_response = f"\n---\nOverseerr is available and these are the status data:"
        status_response += "\n- " + "\n- ".join([f"{key}: {val}" for key,val in data.items()])
    else:
        status_response = f"\n---\nOverseerr is not available and below is the request error: "
        data["url": url]
        status_response += "\n- " + "\n- ".join([f"{key}: {val}" for key, val in data.items()])

    return status_response

async def get_movie_details(movie_id: int) -> dict[str, Any]:
    """Get movie details for a specific movie ID."""
    url = f"{overseerr_url}/api/v1/movie/{movie_id}"
    return await make_overseerr_request(url)

@mcp.tool()
async def get_movie_requests(status: Optional[str] = None, start_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get the list of all movie requests that satisfies the filter arguments.

    Args:
        status: media availability of the requested movie. Only applicable values are ['UNKNOWN', 'PENDING', 'PROCESSING', 'PARTIALLY_AVAILABLE', 'AVAILABLE'].
        start_date: filter for the date of request for the movie formatted as '2020-09-12T10:00:27.000Z'

    Returns:
        List of dictionaries with movie request information in the format:
        {
            "title": "Movie Title",
            "media_availability": "AVAILABLE",
            "request_date": "2020-09-12T10:00:27.000Z"
        }
    """
    # Map media status codes to string values
    media_status_mapping = {
        1: "UNKNOWN",
        2: "PENDING",
        3: "PROCESSING",
        4: "PARTIALLY_AVAILABLE",
        5: "AVAILABLE"
    }

    # Parameter validation
    valid_statuses = ["all", "approved", "available", "pending", "processing", "unavailable", "failed"]
    if status and status not in valid_statuses:
        status = None

    # Initialize pagination parameters
    take = 20  # Number of items per page
    skip = 0  # Starting offset
    has_more = True

    all_results = []

    # Process all pages
    while has_more:
        # Build the request URL with query parameters
        params = {"take": take, "skip": skip, "sort": "added"}
        if status:
            params["filter"] = status.lower()

        # Build query string
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        request_url = f"{overseerr_url}/api/v1/request?{query_string}"

        # Make the API request
        response = await make_overseerr_request(request_url)

        if "Request Error" in response:
            # Return the error if the request failed
            return [{"error": response["Request Error"]}]

        # Extract results
        results = response.get("results", [])

        # Process each result
        for result in results:
            # Only process if it's a movie (has tmdbId but no tvdbId)
            media_info = result.get("media", {})
            if media_info and media_info.get("tmdbId") and not media_info.get("tvdbId"):
                # Check if request date matches the filter if provided
                created_at = result.get("createdAt", "")
                if start_date and start_date > created_at:
                    continue

                # Get movie details to get the title
                movie_details = await get_movie_details(media_info.get("tmdbId"))

                # Map media availability to string value
                media_status_code = media_info.get("status", 1)
                media_availability = media_status_mapping.get(media_status_code, "UNKNOWN")

                # Create formatted result
                formatted_result = {
                    "title": movie_details.get("title", "Unknown Title"),
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

@mcp.tool()
async def get_overseerr_unavailable_tv_requests() -> str:
    """Get the list of TV requests that are still unavailable.

    """
    url = f"{overseerr_url}/api/v1/status"
    data = await make_overseerr_request(url)

    if "version" in data:
        status_response = f"\n---\nOverseerr is available and these are the status data:"
        status_response += "\n- " + "\n- ".join([f"{key}: {val}" for key,val in data.items()])
    else:
        status_response = f"\n---\nOverseerr is not available and below is the request error: "
        data["url": url]
        status_response += "\n- " + "\n- ".join([f"{key}: {val}" for key, val in data.items()])

    return status_response


async def get_tv_details(tv_id: int) -> dict[str, Any]:
    """Get TV details for a specific TV ID."""
    url = f"{overseerr_url}/api/v1/tv/{tv_id}"
    return await make_overseerr_request(url)


async def get_season_details(tv_id: int, season_id: int) -> dict[str, Any]:
    """Get season details including episodes for a specific TV show and season."""
    url = f"{overseerr_url}/api/v1/tv/{tv_id}/season/{season_id}"
    return await make_overseerr_request(url)


@mcp.tool()
async def get_tv_requests(status: Optional[str] = None, start_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get the list of all TV show requests that satisfies the filter arguments.

    Args:
        status: media availability of the requested tv. Only applicable values are ['UNKNOWN', 'PENDING', 'PROCESSING', 'PARTIALLY_AVAILABLE', 'AVAILABLE'].
        start_date: filter for the date of request for the tv series formatted as '2020-09-12T10:00:27.000Z'

    Returns:
        List of dictionaries with TV request information in the format:
        {
            "tv_title": "TV Show Title",
            "tv_title_availability": "AVAILABLE",
            "tv_season": "S01",
            "tv_season_availability": "AVAILABLE",
            "tv_episodes": [
                {
                    "episode_number": "01",
                    "episode_name": "Episode Name"
                },
                ...
            ],
            "request_date": "2020-09-12T10:00:27.000Z"
        }
    """
    # Map media status codes to string values
    media_status_mapping = {
        1: "UNKNOWN",
        2: "PENDING", 
        3: "PROCESSING",
        4: "PARTIALLY_AVAILABLE",
        5: "AVAILABLE"
    }
    
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
        # Build the request URL with query parameters
        params = {"take": take, "skip": skip, "sort": "added"}
        if status:
            params["filter"] = status.lower()
        
        # Build query string
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        request_url = f"{overseerr_url}/api/v1/request?{query_string}"
        
        # Make the API request
        response = await make_overseerr_request(request_url)
        
        if "Request Error" in response:
            # Return the error if the request failed
            return [{"error": response["Request Error"]}]
        
        # Extract results
        results = response.get("results", [])
        
        # Process each result
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
                tv_details = await get_tv_details(tv_id)
                
                # Map media availability to string value
                media_status_code = media_info.get("status", 1)
                tv_title_availability = media_status_mapping.get(media_status_code, "UNKNOWN")
                
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
                    season_details = await get_season_details(tv_id, season_number)
                    
                    # Season availability is assumed to be the same as the show in this implementation
                    # A more accurate implementation might check individual season availability
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


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')